"""每日全局租约、时区隔离的历史及固定日报 outbox。"""

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

from dwy_notify.sqlalchemy import build_delivery_table
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Float,
    MetaData,
    String,
    Table,
    delete,
    false,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .formatting import comparison_dates, digest_content, split_content
from .models import AppleRating, AppleRatingsConfig


@dataclass(frozen=True, slots=True)
class RatingTables:
    """仅声明表；宿主负责迁移并确保三表位于同一数据库。"""

    state: Table
    snapshots: Table
    deliveries: Table


def build_rating_tables(metadata: MetaData, prefix: str = "app_store_ratings") -> RatingTables:
    """支持同库独立监控器的表名前缀，不创建连接或执行 DDL。"""
    if not isinstance(prefix, str) or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,51}", prefix) is None:
        raise ValueError("Invalid rating table prefix")
    state = Table(
        prefix + "_state",
        metadata,
        Column("timezone", String(64), primary_key=True),
        Column("day", String(10), primary_key=True),
        Column("completed", Boolean, nullable=False, server_default=false()),
        Column("lease_token", String(36)),
        Column("lease_until", BigInteger, nullable=False, server_default="0"),
    )
    snapshots = Table(
        prefix + "_snapshots",
        metadata,
        Column("timezone", String(64), primary_key=True),
        Column("app_id", String(128), primary_key=True),
        Column("territory", String(2), primary_key=True),
        Column("day", String(10), primary_key=True),
        Column("status", String(8), nullable=False),
        Column("count", BigInteger),
        Column("average", Float),
        Column("collected_at", BigInteger, nullable=False),
    )
    deliveries = build_delivery_table(metadata, prefix + "_deliveries")
    deliveries.append_column(Column("created_at", BigInteger, nullable=False, index=True))
    return RatingTables(state, snapshots, deliveries)


def _insert(db, table):
    factory = {"sqlite": sqlite_insert, "postgresql": pg_insert}.get(db.get_bind().dialect.name)
    if factory is None:
        raise ValueError("Rating store requires PostgreSQL or SQLite")
    return factory(table)


class RatingStore:
    """持有当前有效租约才可原子保存当日全部结果与日报；不管理数据库生命周期。"""

    def __init__(self, sessions, tables: RatingTables, *, clock: Callable[[], float] = time.time):
        self.sessions, self.tables, self.clock = sessions, tables, clock

    async def claim(self, timezone: str, day: date) -> str | None:
        """以时区和日期持久去重；300 秒后可恢复被中断的采集。"""
        state, now, token = self.tables.state, int(self.clock()), str(uuid4())
        async with self.sessions.begin() as db:
            await db.execute(
                _insert(db, state)
                .values(timezone=timezone, day=day.isoformat())
                .on_conflict_do_nothing(index_elements=["timezone", "day"])
            )
            result = await db.execute(
                update(state)
                .where(
                    state.c.timezone == timezone,
                    state.c.day == day.isoformat(),
                    state.c.completed.is_(False),
                    state.c.lease_until <= now,
                )
                .values(lease_token=token, lease_until=now + 300)
            )
        return token if result.rowcount else None

    async def renew(self, timezone: str, day: date, token: str) -> bool:
        """每个网络请求之前续租；已过期或被替换的 worker 不得继续采集。"""
        state, now = self.tables.state, int(self.clock())
        async with self.sessions.begin() as db:
            result = await db.execute(
                update(state)
                .where(
                    state.c.timezone == timezone,
                    state.c.day == day.isoformat(),
                    state.c.lease_token == token,
                    state.c.lease_until > now,
                    state.c.completed.is_(False),
                )
                .values(lease_until=now + 300)
            )
        return bool(result.rowcount)

    async def release(self, timezone: str, day: date, token: str) -> None:
        """取消或内部提交异常后仅释放自己的租约，不能解除新 worker 的租约。"""
        state = self.tables.state
        async with self.sessions.begin() as db:
            await db.execute(
                update(state)
                .where(
                    state.c.timezone == timezone,
                    state.c.day == day.isoformat(),
                    state.c.lease_token == token,
                )
                .values(lease_token=None, lease_until=0)
            )

    async def complete(
        self,
        config: AppleRatingsConfig,
        day: date,
        token: str,
        results: dict[tuple[str, str], AppleRating | None],
    ) -> bool:
        """成功及失败结果一并定稿；失效租约不能写入任何快照或 outbox。"""
        now, state, snapshots = int(self.clock()), self.tables.state, self.tables.snapshots
        actual_day = datetime.fromtimestamp(now, ZoneInfo(config.timezone)).date()
        if actual_day < day or (actual_day > day and any(value is not None for value in results.values())):
            return False
        async with self.sessions.begin() as db:
            accepted = await db.execute(
                update(state)
                .where(
                    state.c.timezone == config.timezone,
                    state.c.day == day.isoformat(),
                    state.c.lease_token == token,
                    state.c.lease_until > now,
                    state.c.completed.is_(False),
                )
                .values(completed=True, lease_token=None, lease_until=0)
            )
            if not accepted.rowcount:
                return False
            scope = (
                snapshots.c.timezone == config.timezone,
                snapshots.c.app_id.in_(config.apps),
                snapshots.c.territory.in_(config.territories),
            )
            seen_scopes = set(
                (
                    await db.execute(
                        select(
                            snapshots.c.app_id,
                            snapshots.c.territory,
                        )
                        .where(*scope, snapshots.c.day < day.isoformat())
                        .distinct()
                    )
                ).tuples()
            )
            history = {
                (row["app_id"], row["territory"], row["day"]): row
                for row in (
                    await db.execute(
                        select(snapshots).where(
                            *scope,
                            snapshots.c.day.in_(
                                baseline.isoformat() for baseline in comparison_dates(day).values()
                            ),
                        )
                    )
                ).mappings()
            }
            content = digest_content(config, day, now, results, history, seen_scopes)
            for (app_id, territory), rating in results.items():
                await db.execute(
                    _insert(db, snapshots).values(
                        timezone=config.timezone,
                        app_id=app_id,
                        territory=territory,
                        day=day.isoformat(),
                        status="ok" if rating is not None else "error",
                        count=rating.count if rating is not None else None,
                        average=rating.average if rating is not None else None,
                        collected_at=now,
                    )
                )
            for index, chunk in enumerate(split_content(content)):
                await db.execute(
                    _insert(db, self.tables.deliveries).values(
                        app_id=config.timezone,
                        id=f"{day.isoformat()}:{index:04d}",
                        event_type="ratings.daily",
                        payload={"content": chunk, "app_ids": list(config.apps)},
                        status="pending",
                        created_at=now,
                    )
                )
            await self._cleanup(db, config, day, now)
        return True

    async def cleanup(self, config: AppleRatingsConfig, day: date) -> None:
        """即使今日尚未到期，也清理当前时区到期历史；其它时区保持独立。"""
        async with self.sessions.begin() as db:
            await self._cleanup(db, config, day, int(self.clock()))

    async def _cleanup(self, db, config, day, now):
        cutoff = (day - timedelta(days=config.retention_days)).isoformat()
        for table in (self.tables.state, self.tables.snapshots):
            await db.execute(delete(table).where(table.c.timezone == config.timezone, table.c.day < cutoff))
        deliveries = self.tables.deliveries
        await db.execute(
            delete(deliveries).where(
                deliveries.c.app_id == config.timezone,
                deliveries.c.created_at < now - config.retention_days * 86400,
            )
        )
