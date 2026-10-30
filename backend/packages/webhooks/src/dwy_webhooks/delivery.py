"""外部会话、表与发送器驱动的持久投递；模块不连接或初始化项目数据库。"""

import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Collection
from functools import partial
from typing import TYPE_CHECKING
from uuid import uuid4

from dwyeapi.logger import get_logger
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, BigInteger, Column, Integer, MetaData, String, Table, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from .errors import WebhookDeliveryError
from .events import WebhookEvent
from .notification_delivery import deliver_notifications, delivery_failure

if TYPE_CHECKING:
    from dwy_notify import Notifier


class DeliveryPolicy(BaseModel):
    """调用方可显式注入投递预算，缺省与已有 ASC 消费者行为一致。"""

    model_config = ConfigDict(frozen=True, extra="forbid")
    max_attempts: int = Field(default=8, ge=1, le=100)
    batch_size: int = Field(default=25, ge=1, le=500)
    lease_seconds: int = Field(default=60, ge=1, le=3600)
    poll_seconds: float = Field(default=2, gt=0, le=3600, allow_inf_nan=False)
    retry_cap_seconds: int = Field(default=3600, ge=1, le=86400)
    provider_retry_cap_seconds: int = Field(default=86400, ge=1, le=604800)


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
                 allowed_scopes: Collection[str] | None = None,
                 clock: Callable[[], float] = time.time):
        """注入 sender 或 notifier 其中一个；资源生命周期完全由宿主管理。"""
        if re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", source) is None:
            raise ValueError("Invalid webhook source")
        if (sender is None) == (notifier is None):
            raise ValueError("Provide exactly one of sender or notifier")
        self.sessions, self.table, self.sender = sessions, table, sender
        self.notifier = notifier
        self.source, self.clock = source, clock
        self.policy = policy if policy is not None else DeliveryPolicy()
        self.allowed_scopes = None if allowed_scopes is None else frozenset(allowed_scopes)

    async def __call__(self, event: WebhookEvent) -> bool:
        """接收器可直接作为 sink 注入；错误来源必须在持久化前拒绝。"""
        if event.source != self.source:
            raise ValueError("Webhook source does not match the delivery queue")
        return await self.enqueue(event.scope, event.event_id, event.event_type, event.content)

    async def enqueue(self, app_id: str, event_id: str, event_type: str, content: str) -> bool:
        """原子去重和入队；返回后接收端才能向提供方确认成功。"""
        table = self.table
        async with self.sessions.begin() as db:
            dialect = db.get_bind().dialect.name
            factory = {"sqlite": sqlite_insert, "postgresql": pg_insert}.get(dialect)
            if factory is None:
                raise ValueError("Webhook queue requires PostgreSQL or SQLite")
            result = await db.execute(factory(table).values(
                app_id=app_id, id=event_id, event_type=event_type,
                payload={"content": content}, status="pending",
            ).on_conflict_do_nothing(index_elements=["app_id", "id"]))
            return bool(result.rowcount)

    async def process_pending(self) -> int:
        """有界条件领取；进程崩溃后由其他消费者接管过期租约。"""
        table, sent = self.table, 0
        for _ in range(self.policy.batch_size):
            now, token = int(self.clock()), str(uuid4())
            ready = (table.c.status.in_(("pending", "retry", "processing")),
                     table.c.next_attempt_at <= now, table.c.lease_until <= now)
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
                raise WebhookDeliveryError("webhook_invalid_response")
        except WebhookDeliveryError as error:
            failure = error
        except Exception:
            # 第三方 sender 的异常也不能泄露原文，且必须受重试次数约束。
            failure = WebhookDeliveryError("webhook_delivery_error")
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
        # analytics 的公开入口也导出队列存储；延迟解析展示以避免初始化循环。
        from .appearance import notification_appearance

        return await deliver_notifications(
            self.notifier, row["payload"], policy=self.policy, clock=self.clock,
            checkpoint=partial(self._checkpoint, row),
            appearance=notification_appearance(self.source),
        )

    async def run(self) -> None:
        """由调用项目的 lifespan 启停；未知失败只记录固定错误码。"""
        while True:
            try:
                await self.process_pending()
            except Exception:
                get_logger(__name__).error("Webhook processor failed code=WEBHOOK_PROCESSOR_FAILED")
            await asyncio.sleep(self.policy.poll_seconds)
