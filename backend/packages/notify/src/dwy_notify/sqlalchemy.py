"""外部会话、表与发送器驱动的持久投递；模块不连接或初始化项目数据库。"""

import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Collection
from functools import partial
from typing import TYPE_CHECKING
from uuid import uuid4

from dwyeapi.logger import get_logger
from sqlalchemy import JSON, BigInteger, Column, Integer, MetaData, String, Table, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from .delivery import (
    DeliveryPolicy,
    NotificationDeliveryError,
    _delivery_values,
    deliver_notifications,
    delivery_failure,
)
from .events import NotificationEvent
from .models import NotificationAppearance

if TYPE_CHECKING:
    from dwy_notify import Notifier


def _bounded_text(value: str, maximum: int, code: str) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or not value.strip():
        raise ValueError(code)


def build_delivery_table(metadata: MetaData, name: str = "webhook_deliveries", *,
                         scope_length: int = 128) -> Table:
    """仅构造表定义；调用项目通过自己的 Alembic 迁移管理实际 schema。

    app_id 是来源内的隔离 scope；沿用已有字段名以兼容 ASC 账本。
    一个表归属一个来源，由调用方分别注入，不能把不同来源写进同一表。
    """
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,62}", name) is None or not 1 <= scope_length <= 255:
        raise ValueError("Invalid webhook delivery table definition")
    return Table(
        name, metadata,
        Column("app_id", String(scope_length), primary_key=True),
        Column("id", String(128), primary_key=True),
        Column("event_type", String(128), nullable=False),
        Column("payload", JSON, nullable=False),
        Column("status", String(20), nullable=False),
        Column("attempts", Integer, nullable=False, server_default="0"),
        Column("next_attempt_at", BigInteger, nullable=False, server_default="0"),
        Column("lease_until", BigInteger, nullable=False, server_default="0"),
        Column("lease_token", String(36)),
        Column("error_code", String(64)),
        Column("message_id", String(128)),
    )


class SQLAlchemyDeliveryQueue:
    """每个来源拥有独立账本；发送在事务外，完成更新必须持有本轮租约。"""

    def __init__(self, sessions, table: Table,
                 sender: Callable[[str], Awaitable[str | None]] | None = None, *,
                 notifier: "Notifier | None" = None,
                 source: str, policy: DeliveryPolicy | None = None,
                 appearance: NotificationAppearance | None = None,
                 allowed_scopes: Collection[str] | None = None,
                 clock: Callable[[], float] = time.time):
        """注入 sender 或 notifier 其中一个；资源生命周期完全由宿主管理。"""
        if re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", source) is None:
            raise ValueError("Invalid webhook source")
        if (sender is None) == (notifier is None):
            raise ValueError("Provide exactly one of sender or notifier")
        self.sessions, self.table, self.sender = sessions, table, sender
        self.notifier, self.appearance = notifier, appearance
        self.source, self.clock = source, clock
        self.policy = policy if policy is not None else DeliveryPolicy()
        self.allowed_scopes = None if allowed_scopes is None else frozenset(allowed_scopes)

    async def __call__(self, event: NotificationEvent) -> bool:
        """接收器可直接作为 sink 注入；错误来源必须在持久化前拒绝。"""
        if event.source != self.source:
            raise ValueError("Webhook source does not match the delivery queue")
        return await self.enqueue(event.scope, event.event_id, event.event_type, event.content,
                                  appearance=event.appearance)

    async def enqueue(self, app_id: str, event_id: str, event_type: str, content: str, *,
                      appearance: NotificationAppearance | None = None) -> bool:
        """原子去重和入队；返回后接收端才能向提供方确认成功。"""
        async with self.sessions.begin() as db:
            return await self.enqueue_in_session(db, app_id, event_id, event_type, content,
                                                 appearance=appearance)

    async def enqueue_in_session(
        self, db: AsyncSession, app_id: str, event_id: str, event_type: str, content: str,
        *, appearance: NotificationAppearance | None = None,
    ) -> bool:
        """加入宿主事务，True 为新增、False 为重复；不提交、回滚或关闭外部会话。

        标识按表字段限长，正文非空白且最多 65536 字符，不截断；宿主提交后才可确认事件。
        """
        self._validate_key(app_id, event_id)
        _bounded_text(event_type, 128, "invalid_notification_event_type")
        _bounded_text(content, 65536, "invalid_notification_content")
        table = self.table
        factory = {"sqlite": sqlite_insert, "postgresql": pg_insert}.get(db.get_bind().dialect.name)
        if factory is None:
            raise ValueError("Webhook queue requires PostgreSQL or SQLite")
        payload = {"content": content}
        if appearance is not None:
            payload["appearance"] = appearance.model_dump(exclude_unset=True)
        result = await db.execute(factory(table).values(
            app_id=app_id, id=event_id, event_type=event_type,
            payload=payload, status="pending",
        ).on_conflict_do_nothing(index_elements=["app_id", "id"]))
        return bool(result.rowcount)

    async def requeue_failed_in_session(
        self, db: AsyncSession, app_id: str, event_id: str, targets: tuple[str, ...],
    ) -> bool:
        """在宿主事务中重置指定 dead/retry 目标，不发消息且不管理外部会话生命周期。

        拒绝成功目标、新目标、指纹变化和活跃租约；无记录、无快照或无失败目标返回 False。
        持有记录写锁直到宿主事务结束，调用方应及时提交或回滚；错误仅含固定安全原因码。
        """
        self._validate_key(app_id, event_id)
        if (not isinstance(targets, tuple) or not targets
                or any(not isinstance(name, str) or not name.strip() for name in targets)
                or len(targets) != len(set(targets))):
            raise ValueError("invalid_notification_targets")
        if self.notifier is None:
            raise ValueError("notification_replay_requires_notifier")
        if db.get_bind().dialect.name not in ("sqlite", "postgresql"):
            raise ValueError("Webhook queue requires PostgreSQL or SQLite")
        table, now = self.table, int(self.clock())
        key = (table.c.app_id == app_id, table.c.id == event_id)
        # SQLite 忽略 FOR UPDATE；无值变化的 UPDATE 同时锁住两种数据库，避免读后覆盖新检查点。
        row = (await db.execute(update(table).where(*key).values(
            lease_until=table.c.lease_until,
        ).returning(table))).mappings().first()
        if row is None:
            return False
        if row["lease_until"] > now:
            raise ValueError("notification_active_lease")
        payload = row["payload"]
        if "notifications" not in payload:
            return False
        states = payload["notifications"]
        for name in targets:
            if name not in states:
                raise ValueError("notification_target_not_in_snapshot")
            if states[name]["status"] == "sent":
                raise ValueError("notification_target_sent")
            if name not in self.notifier.targets:
                raise ValueError("notification_target_missing")
            if self.notifier.target_fingerprint(name) != states[name]["fingerprint"]:
                raise ValueError("notification_target_changed")
        failed = [states[name] for name in targets if states[name]["status"] in ("dead", "retry")]
        if not failed:
            return False
        for state in failed:
            state.update(status="pending", attempts=0, next_attempt_at=now, error_code=None, message_id=None)
        result = await db.execute(update(table).where(
            *key, table.c.lease_until <= now, table.c.lease_token == row["lease_token"],
            table.c.status == row["status"],
        ).values(payload=payload, **_delivery_values(states), lease_until=0, lease_token=None))
        return bool(result.rowcount)

    def _validate_key(self, app_id: str, event_id: str) -> None:
        _bounded_text(app_id, self.table.c.app_id.type.length, "invalid_notification_scope")
        _bounded_text(event_id, 128, "invalid_notification_event_id")

    async def process_pending(self) -> int:
        """有界条件领取；进程崩溃后由其他消费者接管过期租约。"""
        table, sent = self.table, 0
        for _ in range(self.policy.batch_size):
            now, token = int(self.clock()), str(uuid4())
            ready = (table.c.status.in_(("pending", "retry", "processing")),
                     table.c.next_attempt_at <= now, table.c.lease_until <= now)
            if self.allowed_scopes is not None:
                ready += (table.c.app_id.in_(self.allowed_scopes),)
            async with self.sessions.begin() as db:
                row = (await db.execute(select(table).where(*ready).order_by(
                    table.c.next_attempt_at, table.c.app_id, table.c.id
                ).limit(1))).mappings().first()
                if row is None:
                    break
                key = (table.c.app_id == row["app_id"], table.c.id == row["id"])
                claimed = await db.execute(update(table).where(*key, *ready).values(
                    status="processing", lease_token=token, lease_until=now + self.policy.lease_seconds))
                if not claimed.rowcount:
                    continue
                row = dict(row)
                row["lease_token"] = token
            values = await self._send(row)
            async with self.sessions.begin() as db:
                result = await db.execute(update(table).where(
                    *key, table.c.lease_token == token
                ).values(**values, lease_token=None, lease_until=0))
                sent += int(bool(result.rowcount) and values["status"] == "sent")
        return sent

    async def _send(self, row) -> dict:
        if self.allowed_scopes is not None and row["app_id"] not in self.allowed_scopes:
            return dict(status="suppressed", payload={}, error_code=None)
        if self.notifier is not None:
            return await self._send_notifications(row)
        failure = None
        try:
            message_id = await self.sender(row["payload"]["content"])
            if message_id is not None and (
                not isinstance(message_id, str) or not 1 <= len(message_id) <= 128
            ):
                raise NotificationDeliveryError("webhook_invalid_response")
        except NotificationDeliveryError as error:
            failure = error
        except Exception:
            # 第三方 sender 的异常也不能泄露原文，且必须受重试次数约束。
            failure = NotificationDeliveryError("webhook_delivery_error")
        if failure is not None:
            return self._failure(row["attempts"], failure)
        return dict(status="sent", message_id=message_id, error_code=None)

    def _failure(self, attempts, failure) -> dict:
        return delivery_failure(attempts, failure, policy=self.policy, clock=self.clock)

    async def _checkpoint(self, row, **values) -> bool:
        table = self.table
        async with self.sessions.begin() as db:
            result = await db.execute(update(table).where(
                table.c.app_id == row["app_id"], table.c.id == row["id"],
                table.c.lease_token == row["lease_token"],
            ).values(**values))
            return bool(result.rowcount)

    async def _send_notifications(self, row) -> dict:
        return await deliver_notifications(
            self.notifier, row["payload"], policy=self.policy, clock=self.clock,
            checkpoint=partial(self._checkpoint, row),
            appearance=self.appearance,
        )

    async def run(self) -> None:
        """由调用项目的 lifespan 启停；未知失败只记录固定错误码。"""
        while True:
            try:
                await self.process_pending()
            except Exception:
                get_logger(__name__).error("Webhook processor failed code=WEBHOOK_PROCESSOR_FAILED")
            await asyncio.sleep(self.policy.poll_seconds)
