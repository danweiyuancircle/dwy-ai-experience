"""持久资金结果；宿主至少一次消费并幂等处理，外部操作不得发生在写入事务中。"""

from datetime import datetime
from hashlib import sha256
from typing import Literal

from dwyeapi import dt
from dwyeapi.database import Base, TimestampMixin
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, DateTime, String, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


class PaymentEventPayload(BaseModel):
    """仅投影已核验资金字段；不包含用户资料、凭据、回调原文或商品结构。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    event_type: Literal["PAYMENT.SUCCESS", "REFUND.SUCCESS", "REFUND.ABNORMAL", "REFUND.CLOSED"]
    order_no: str = Field(min_length=6, max_length=32)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=64)
    channel: Literal["wechat", "alipay"]
    transaction_id: str = Field(min_length=1, max_length=64)
    amount_fen: int = Field(strict=True, ge=1, le=100000000)
    currency: Literal["CNY"] = "CNY"
    refund_no: str | None = Field(default=None, min_length=1, max_length=64)
    refund_fen: int | None = Field(default=None, strict=True, ge=1, le=100000000)
    version: int = Field(default=1, strict=True, ge=1)


class PaymentEvent(Base, TimestampMixin):
    """单个宿主消费组的持久结果队列；确认必须与本地业务更新同事务提交。"""

    __tablename__ = "payment_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    order_no: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)


async def record_payment_event(db: AsyncSession, payload: PaymentEventPayload) -> None:
    """与资金CAS变更同事务登记；状态转换调用方已保证同一状态只登记一次。"""
    key = f"{payload.order_no}:{payload.refund_no or ''}:{payload.event_type}"
    event_id = sha256(key.encode()).hexdigest()
    if await db.get(PaymentEvent, event_id) is None:
        db.add(PaymentEvent(event_id=event_id, order_no=payload.order_no, payload=payload.model_dump()))
        await db.flush()


async def pending_payment_events(db: AsyncSession, *, limit: int = 20) -> list[PaymentEvent]:
    """读取待消费结果，不取得独占权；并发消费者可能读到同一事件，必须幂等。"""
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("event limit must be between 1 and 100")
    return list(await db.scalars(
        select(PaymentEvent)
        .where(PaymentEvent.acknowledged_at.is_(None))
        .order_by(PaymentEvent.created_at, PaymentEvent.event_id)
        .limit(limit)
    ))


async def acknowledge_payment_event(db: AsyncSession, event_id: str) -> None:
    """标记已消费但不提交；跨数据库消费者须先持久处理再确认，允许重复交付。"""
    if len(event_id) != 64 or any(char not in "0123456789abcdef" for char in event_id):
        raise ValueError("invalid event identifier")
    await db.execute(
        update(PaymentEvent)
        .where(PaymentEvent.event_id == event_id, PaymentEvent.acknowledged_at.is_(None))
        .values(acknowledged_at=dt.now())
    )
