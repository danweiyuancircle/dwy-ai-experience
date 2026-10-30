"""宿主迁移的账号隔离快照、调度租约和持久 outbox。"""

import hashlib
import re
import time
from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from dwy_notify.sqlalchemy import build_delivery_table
from sqlalchemy import JSON, BigInteger, Column, Date, MetaData, String, Table, delete, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .models import AppleBusinessSnapshot


@dataclass(frozen=True, slots=True)
class AnalyticsTables:
    """三张表必须使用同一数据库；定义不创建、迁移或关闭宿主资源。"""

    state: Table
    snapshots: Table
    deliveries: Table


def build_analytics_tables(metadata: MetaData, prefix: str = "app_store_analytics") -> AnalyticsTables:
    """返回 Alembic 使用的定义；issuer_id 隔离同 App 的不同 Apple 账号。"""
    if not isinstance(prefix, str) or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,50}", prefix) is None:
        raise ValueError("Invalid analytics table prefix")
    state = Table(
        prefix + "_state",
        metadata,
        Column("issuer_id", String(128), primary_key=True),
        Column("app_id", String(128), primary_key=True),
        Column("last_report_date", Date),
        Column("last_success_at", BigInteger),
        Column("next_poll_at", BigInteger, nullable=False, server_default="0"),
        Column("lease_until", BigInteger, nullable=False, server_default="0"),
        Column("lease_token", String(36)),
    )
    snapshots = Table(
        prefix + "_snapshots",
        metadata,
        Column("issuer_id", String(128), primary_key=True),
        Column("app_id", String(128), primary_key=True),
        Column("report_date", Date, primary_key=True),
        Column("collected_at", BigInteger, nullable=False, index=True),
        Column("payload", JSON, nullable=False),
    )
    deliveries = build_delivery_table(metadata, prefix + "_deliveries", scope_length=255)
    deliveries.append_column(Column("created_at", BigInteger, nullable=False, index=True))
    return AnalyticsTables(state, snapshots, deliveries)


def _scope(issuer_id, app_id):
    if any(not isinstance(v, str) or not 1 <= len(v) <= 128 or ":" in v for v in (issuer_id, app_id)):
        raise ValueError("Invalid analytics account or application scope")
    scope = issuer_id + ":" + app_id
    if len(scope) > 255:
        raise ValueError("Invalid analytics delivery scope")
    return scope


def _insert(db, table):
    factory = {"sqlite": sqlite_insert, "postgresql": pg_insert}.get(db.get_bind().dialect.name)
    if factory is None:
        raise ValueError("Analytics store requires PostgreSQL or SQLite")
    return factory(table)


def _delivery_id(scope, period, start, end, index):
    identity = f"{scope}:{period}:{start.isoformat()}:{end.isoformat()}"
    # 公共队列按 id 排序；分段编号放在哈希后，保持首次投递顺序。
    return f"{end.isoformat()}:{period}:{hashlib.sha256(identity.encode()).hexdigest()[:32]}:{index:04}"


class AnalyticsStore:
    """网络采集在事务外；提交必须仍持有效租约，快照和通知原子落库。"""

    def __init__(self, sessions, tables: AnalyticsTables, *, clock=time.time):
        """注入宿主会话、表和可控时钟，不持有引擎生命周期。"""
        self.sessions, self.tables, self.clock = sessions, tables, clock

    async def claim(
        self, issuer_id: str, app_id: str, report_date: date, *, lease_seconds: int = 300
    ) -> str | None:
        """仅领取未完成日期；租约过期后另一 worker 可接管，重启不重复采集。"""
        _scope(issuer_id, app_id)
        if type(report_date) is not date or type(lease_seconds) is not int or not 1 <= lease_seconds <= 3600:
            raise ValueError("Invalid analytics schedule")
        table, now, token = self.tables.state, int(self.clock()), str(uuid4())
        async with self.sessions.begin() as db:
            await db.execute(
                _insert(db, table)
                .values(issuer_id=issuer_id, app_id=app_id)
                .on_conflict_do_nothing(index_elements=["issuer_id", "app_id"])
            )
            result = await db.execute(
                update(table)
                .where(
                    table.c.issuer_id == issuer_id,
                    table.c.app_id == app_id,
                    table.c.lease_until <= now,
                    table.c.next_poll_at <= now,
                    table.c.last_report_date.is_(None) | (table.c.last_report_date < report_date),
                )
                .values(lease_token=token, lease_until=now + lease_seconds)
            )
            return token if result.rowcount else None

    async def load(self, issuer_id: str, app_id: str, start: date, end: date) -> list[AppleBusinessSnapshot]:
        """读取包含边界的归一化日期区间，不把缺日补成零。"""
        _scope(issuer_id, app_id)
        table = self.tables.snapshots
        async with self.sessions() as db:
            payloads = (
                (
                    await db.execute(
                        select(table.c.payload)
                        .where(
                            table.c.issuer_id == issuer_id,
                            table.c.app_id == app_id,
                            table.c.report_date >= start,
                            table.c.report_date <= end,
                        )
                        .order_by(table.c.report_date)
                    )
                )
                .scalars()
                .all()
            )
        return [AppleBusinessSnapshot.model_validate(payload) for payload in payloads]

    async def complete(
        self,
        issuer_id: str,
        app_id: str,
        token: str,
        snapshots: list[AppleBusinessSnapshot],
        *,
        report_date: date,
        messages: list,
        next_poll_at: int,
    ) -> bool:
        """替换日期版本并按账号/App/期间/分段去重；失效 worker 不得写入任何内容。"""
        scope = _scope(issuer_id, app_id)
        if not 1 <= len(snapshots) <= 7 or any(s.app_id != app_id for s in snapshots):
            raise ValueError("Invalid analytics snapshot batch")
        table, state, outbox = self.tables.snapshots, self.tables.state, self.tables.deliveries
        now = int(self.clock())
        key = (state.c.issuer_id == issuer_id, state.c.app_id == app_id, state.c.lease_token == token)
        async with self.sessions.begin() as db:
            fenced = await db.execute(
                update(state).where(*key, state.c.lease_until > now).values(lease_token=token)
            )
            if not fenced.rowcount:
                return False
            for snapshot in snapshots:
                values = dict(payload=snapshot.model_dump(mode="json"), collected_at=now)
                await db.execute(
                    _insert(db, table)
                    .values(issuer_id=issuer_id, app_id=app_id, report_date=snapshot.report_date, **values)
                    .on_conflict_do_update(index_elements=["issuer_id", "app_id", "report_date"], set_=values)
                )
            for period, start, end, parts in messages:
                if period not in ("daily", "weekly") or (end - start).days != (
                    6 if period == "weekly" else 0
                ):
                    raise ValueError("Invalid analytics notification period")
                for index, content in enumerate(parts):
                    if not isinstance(content, str) or not 1 <= len(content.encode("utf-16-le")) // 2 <= 2000:
                        raise ValueError("Invalid analytics notification content")
                    await db.execute(
                        _insert(db, outbox)
                        .values(
                            app_id=scope,
                            id=_delivery_id(scope, period, start, end, index),
                            event_type="analytics." + period,
                            payload={"content": content},
                            status="pending",
                            created_at=now,
                        )
                        .on_conflict_do_nothing(index_elements=["app_id", "id"])
                    )
            await db.execute(
                update(state)
                .where(*key)
                .values(
                    last_report_date=report_date,
                    last_success_at=now,
                    next_poll_at=next_poll_at,
                    lease_token=None,
                    lease_until=0,
                )
            )
            return True

    async def fail(
        self,
        issuer_id: str,
        app_id: str,
        token: str,
        report_date: date,
        *,
        app_name: str,
        retry_seconds: int = 60,
    ) -> bool:
        """同 App/统计日最多一条安全告警；入队与释放租约同事务，不妨碍后续成功日报。"""
        scope = _scope(issuer_id, app_id)
        if type(report_date) is not date or type(retry_seconds) is not int or not 1 <= retry_seconds <= 86400:
            raise ValueError("Invalid analytics failure schedule")
        state, outbox, now = self.tables.state, self.tables.deliveries, int(self.clock())
        async with self.sessions.begin() as db:
            fenced = await db.execute(
                update(state)
                .where(
                    state.c.issuer_id == issuer_id,
                    state.c.app_id == app_id,
                    state.c.lease_token == token,
                    state.c.lease_until > now,
                )
                .values(lease_token=None, lease_until=0, next_poll_at=now + retry_seconds)
            )
            if not fenced.rowcount:
                return False
            name = str(app_name)[:128].replace("@", "＠").replace("\n", " ").replace("\r", " ")
            await db.execute(
                _insert(db, outbox)
                .values(
                    app_id=scope,
                    id=_delivery_id(scope, "failed", report_date, report_date, 0),
                    event_type="analytics.collection_failed",
                    payload={
                        "content": f"**【Apple 经营采集失败】**\n应用：{name}\n"
                        f"统计日：{report_date.isoformat()}\n"
                        "错误码：ANALYTICS_COLLECTION_FAILED\n采集将自动重试；失败不表示经营指标为 0。"
                    },
                    status="pending",
                    created_at=now,
                )
                .on_conflict_do_nothing(index_elements=["app_id", "id"])
            )
            return True

    async def release(self, issuer_id: str, app_id: str, token: str, *, retry_seconds: int = 60) -> None:
        """失败仅延迟本租约的下一次尝试，旧 worker 不能解除新租约。"""
        _scope(issuer_id, app_id)
        if type(retry_seconds) is not int or not 1 <= retry_seconds <= 86400:
            raise ValueError("Invalid analytics retry schedule")
        table = self.tables.state
        async with self.sessions.begin() as db:
            await db.execute(
                update(table)
                .where(table.c.issuer_id == issuer_id, table.c.app_id == app_id, table.c.lease_token == token)
                .values(lease_token=None, lease_until=0, next_poll_at=int(self.clock()) + retry_seconds)
            )

    async def cleanup(self, issuer_id: str, retention_days: int) -> int:
        """仅清理当前账号的历史快照和通知正文，不删除去重调度状态。"""
        if type(retention_days) is not int or not 1 <= retention_days <= 3650:
            raise ValueError("Invalid analytics retention")
        _scope(issuer_id, "scope")
        cutoff, deleted = int(self.clock()) - retention_days * 86400, 0
        async with self.sessions.begin() as db:
            snapshots = self.tables.snapshots
            result = await db.execute(
                delete(snapshots).where(snapshots.c.issuer_id == issuer_id, snapshots.c.collected_at < cutoff)
            )
            deleted += result.rowcount
            outbox = self.tables.deliveries
            # 不使用 LIKE：账号输入中的 SQL 通配符不能跨租户清理。
            scopes = select(self.tables.state.c.app_id).where(self.tables.state.c.issuer_id == issuer_id)
            apps = (await db.execute(scopes)).scalars().all()
            if apps:
                result = await db.execute(
                    delete(outbox).where(
                        outbox.c.app_id.in_([_scope(issuer_id, app) for app in apps]),
                        outbox.c.created_at < cutoff,
                    )
                )
                deleted += result.rowcount
        return deleted
