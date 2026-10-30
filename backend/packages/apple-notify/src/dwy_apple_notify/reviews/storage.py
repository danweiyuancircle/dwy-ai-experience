"""通过调用方会话和迁移表保存评论；同步状态和通知始终在同一事务提交。"""

import hashlib
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from dwy_notify.sqlalchemy import build_delivery_table
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    case,
    delete,
    false,
    func,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .formatting import baseline_content, review_content
from .models import AppleReview


@dataclass(frozen=True, slots=True)
class ReviewTables:
    """每个来源独立的三张表；调用方负责迁移，库不创建或关闭数据库。"""

    state: Table
    reviews: Table
    deliveries: Table


def build_review_tables(metadata: MetaData, prefix: str = "app_store_review") -> ReviewTables:
    """仅声明评论表及兼容现有投递队列的 outbox，不执行任何数据库操作。"""
    if not isinstance(prefix, str) or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,51}", prefix) is None:
        raise ValueError("Invalid review table prefix")
    state = Table(
        prefix + "_state",
        metadata,
        Column("app_id", String(128), primary_key=True),
        Column("initialized", Boolean, nullable=False, server_default=false()),
        Column("last_success_at", BigInteger),
        # 单调推进通知下界；扩大保留期可补历史，但不能重新通知曾被排除的历史评论。
        Column("retention_cutoff_at", BigInteger),
        Column("next_poll_at", BigInteger, nullable=False, server_default="0"),
        Column("interval_seconds", Integer, nullable=False, server_default="3600"),
        Column("lease_until", BigInteger, nullable=False, server_default="0"),
        Column("lease_token", String(36)),
    )
    reviews = Table(
        prefix + "_reviews",
        metadata,
        Column("app_id", String(128), primary_key=True),
        Column("id", String(128), primary_key=True),
        Column("fingerprint", String(64), nullable=False),
        Column("created_at", BigInteger, nullable=False, index=True),
        Column("payload", JSON, nullable=False),
    )
    deliveries = build_delivery_table(metadata, prefix + "_deliveries")
    deliveries.append_column(Column("created_at", BigInteger, nullable=False, index=True))
    return ReviewTables(state, reviews, deliveries)


def _integer(value: int, lower: int, upper: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise ValueError("Invalid review synchronization budget")


def _app_id(value: str) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= 128:
        raise ValueError("Invalid review application scope")


def _insert(db, table: Table):
    factory = {"sqlite": sqlite_insert, "postgresql": pg_insert}.get(db.get_bind().dialect.name)
    if factory is None:
        raise ValueError("Review store requires PostgreSQL or SQLite")
    return factory(table)


def _fingerprint(review: AppleReview) -> str:
    content = [review.rating, review.title, review.body, review.reviewer_nickname, review.territory]
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


class ReviewStore:
    """持久化每应用的调度租约、评论基线和通知；资源生命周期完全由宿主管理。"""

    def __init__(self, sessions, tables: ReviewTables, *, clock: Callable[[], float] = time.time):
        """会话工厂和三张迁移表必须属于同一数据库，以保证状态与 outbox 原子提交。"""
        self.sessions, self.tables, self.clock = sessions, tables, clock

    async def summary(self, app_id: str, day: date) -> dict[str, int]:
        """返回已完整覆盖的 UTC 创建日计数；无基线或已清理日期返回空映射。

        Args:
            app_id: 来源应用 ID，1–128 字符，例如 "1234567890"。
            day: UTC 评论创建日，例如 date(2026, 10, 25)；不统计商店全部星级。
        """
        _app_id(app_id)
        if type(day) is not date:
            raise ValueError("Review summary requires a calendar date")
        start = int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp())
        end = start + int(timedelta(days=1).total_seconds())
        state, reviews = self.tables.state, self.tables.reviews
        async with self.sessions() as db:
            row = (await db.execute(select(state).where(state.c.app_id == app_id))).mappings().first()
            if (row is None or not row["initialized"] or (row["last_success_at"] or 0) < end
                    or start < (row["retention_cutoff_at"] or 0)):
                return {}
            counts = (await db.execute(select(
                func.count(), func.sum(case((reviews.c.payload["rating"].as_integer() <= 2, 1), else_=0)),
            ).where(
                reviews.c.app_id == app_id, reviews.c.created_at >= start, reviews.c.created_at < end,
            ))).one()
        return {"review_count": counts[0], "low_star_reviews": counts[1] or 0}

    async def claim(
        self,
        app_id: str,
        poll_interval_seconds: int = 3600,
        lease_seconds: int = 300,
    ) -> str | None:
        """仅领取到期且没有有效租约的应用；重启保留调度，周期变化按最后成功时间生效。"""
        _app_id(app_id)
        _integer(poll_interval_seconds, 60, 604800)
        _integer(lease_seconds, 1, 3600)
        now, token = int(self.clock()), str(uuid4())
        state = self.tables.state
        async with self.sessions.begin() as db:
            await db.execute(
                _insert(db, state)
                .values(
                    app_id=app_id,
                    interval_seconds=poll_interval_seconds,
                )
                .on_conflict_do_nothing(index_elements=["app_id"])
            )
            await db.execute(
                update(state)
                .where(
                    state.c.app_id == app_id,
                    state.c.lease_until <= now,
                    state.c.interval_seconds != poll_interval_seconds,
                )
                .values(
                    interval_seconds=poll_interval_seconds,
                    next_poll_at=case(
                        (
                            state.c.last_success_at.is_not(None),
                            state.c.last_success_at + poll_interval_seconds,
                        ),
                        else_=state.c.next_poll_at,
                    ),
                )
            )
            result = await db.execute(
                update(state)
                .where(
                    state.c.app_id == app_id,
                    state.c.lease_until <= now,
                    state.c.next_poll_at <= now,
                )
                .values(lease_token=token, lease_until=now + lease_seconds)
            )
            return token if result.rowcount else None

    async def complete(
        self,
        app_id: str,
        token: str,
        reviews: list[AppleReview],
        *,
        app_name: str,
        poll_interval_seconds: int,
        retention_days: int,
    ) -> bool:
        """完成整次拉取后才提交；过期或被替代租约不能写入基线、评论或通知。"""
        _app_id(app_id)
        _integer(poll_interval_seconds, 60, 604800)
        _integer(retention_days, 1, 3650)
        now = int(self.clock())
        cutoff = now - retention_days * 86400
        state, table, deliveries = self.tables.state, self.tables.reviews, self.tables.deliveries
        # Apple 分页可能重复同一条记录；同次同步只处理最终版本，避免一次拉取制造伪更新。
        recent = {review.id: review for review in reviews if review.created_at.timestamp() >= cutoff}
        async with self.sessions.begin() as db:
            claimed = await db.execute(
                update(state)
                .where(
                    state.c.app_id == app_id,
                    state.c.lease_token == token,
                    state.c.lease_until > now,
                )
                .values(lease_token=token)
            )
            if not claimed.rowcount:
                return False
            sync_state = (
                (
                    await db.execute(
                        select(state.c.initialized, state.c.retention_cutoff_at).where(
                            state.c.app_id == app_id,
                        )
                    )
                )
                .mappings()
                .one()
            )
            initialized, notification_floor = sync_state["initialized"], sync_state["retention_cutoff_at"]
            await self._cleanup(db, cutoff, app_id)
            previous = {
                row["id"]: row["fingerprint"]
                for row in (
                    await db.execute(
                        select(table.c.id, table.c.fingerprint).where(
                            table.c.app_id == app_id,
                        )
                    )
                ).mappings()
            }
            for review in recent.values():
                fingerprint = _fingerprint(review)
                if previous.get(review.id) == fingerprint:
                    continue
                created_at = int(review.created_at.timestamp())
                values = dict(
                    fingerprint=fingerprint,
                    created_at=created_at,
                    payload=review.model_dump(mode="json"),
                )
                await db.execute(
                    _insert(db, table)
                    .values(
                        app_id=app_id,
                        id=review.id,
                        **values,
                    )
                    .on_conflict_do_update(index_elements=["app_id", "id"], set_=values)
                )
                # 扩大保留窗口时补回的历史记录只建基线，避免将已清理的评论误报为新增。
                historical_backfill = (
                    review.id not in previous
                    and notification_floor is not None
                    and created_at < notification_floor
                )
                if initialized and not historical_backfill:
                    await db.execute(
                        _insert(db, deliveries).values(
                            app_id=app_id,
                            id=str(uuid4()),
                            event_type="review.updated" if review.id in previous else "review.created",
                            payload={
                                "content": review_content(
                                    app_id,
                                    app_name,
                                    review,
                                    updated=review.id in previous,
                                )
                            },
                            status="pending",
                            created_at=created_at,
                        )
                    )
            if not initialized:
                await db.execute(
                    _insert(db, deliveries).values(
                        app_id=app_id,
                        id=str(uuid4()),
                        event_type="reviews.baseline",
                        payload={"content": baseline_content(app_id, app_name, len(recent))},
                        status="pending",
                        created_at=now,
                    )
                )
            await db.execute(
                update(state)
                .where(state.c.app_id == app_id)
                .values(
                    initialized=True,
                    last_success_at=now,
                    next_poll_at=now + poll_interval_seconds,
                    interval_seconds=poll_interval_seconds,
                    lease_token=None,
                    lease_until=0,
                )
            )
            return True

    async def release(self, app_id: str, token: str, retry_seconds: int = 60) -> None:
        """拉取失败只释放对应租约并推迟重试；旧 worker 无法清除新 worker 的租约。"""
        _app_id(app_id)
        _integer(retry_seconds, 1, 604800)
        state = self.tables.state
        async with self.sessions.begin() as db:
            await db.execute(
                update(state)
                .where(
                    state.c.app_id == app_id,
                    state.c.lease_token == token,
                )
                .values(lease_token=None, lease_until=0, next_poll_at=int(self.clock()) + retry_seconds)
            )

    async def cleanup(self, retention_days: int) -> int:
        """独立清理过期评论和通知正文，即使 Apple 拉取失败也可执行；返回总删除行数。"""
        _integer(retention_days, 1, 3650)
        async with self.sessions.begin() as db:
            return await self._cleanup(db, int(self.clock()) - retention_days * 86400)

    async def _cleanup(self, db, cutoff: int, app_id: str | None = None) -> int:
        state = self.tables.state
        # 与 complete 保持 state→内容表的加锁顺序，避免 PostgreSQL 清理和同步相互死锁。
        floor = update(state).where(
            state.c.retention_cutoff_at.is_(None) | (state.c.retention_cutoff_at < cutoff),
        )
        if app_id is not None:
            floor = floor.where(state.c.app_id == app_id)
        await db.execute(floor.values(retention_cutoff_at=cutoff))
        deleted = 0
        for table in (self.tables.reviews, self.tables.deliveries):
            statement = delete(table).where(table.c.created_at < cutoff)
            if app_id is not None:
                statement = statement.where(table.c.app_id == app_id)
            result = await db.execute(statement)
            deleted += result.rowcount
        return deleted
