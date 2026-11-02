"""退款查询结果与宿主通知接口；不把PROCESSING转换为官方成功事件。"""

from datetime import datetime
from typing import Annotated, Literal, Protocol

from dwy_wechatpay_notify import ConfirmedWechatPayResult
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession


class RefundChannelResult(BaseModel):
    """已验签回调或SDK已验签查询的白名单字段；查询保留provider_event_id=None。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    order_no: Annotated[str, Field(min_length=6, max_length=32, pattern=r"^[0-9A-Za-z_|\-*]+$")]
    transaction_id: Annotated[str, Field(min_length=1, max_length=64)]
    amount_fen: Annotated[int, Field(strict=True, ge=1, le=100000000)]
    refund_no: Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[0-9A-Za-z_|\-*@]+$")]
    refund_id: Annotated[str, Field(min_length=1, max_length=64)]
    refund_fen: Annotated[int, Field(strict=True, ge=1, le=100000000)]
    refund_status: Literal["SUCCESS", "PROCESSING", "ABNORMAL", "CLOSED"]
    currency: str = Field(default="CNY", min_length=3, max_length=3)
    provider_event_id: str | None = None
    occurred_at: datetime | None = None


class RefundResultHook(Protocol):
    """原子状态更新后、提交前调用；只登记持久通知，不发网络消息、不自行commit。"""

    async def __call__(self, result: ConfirmedWechatPayResult, db: AsyncSession) -> None:
        """同一退款号/核验状态可重入；使用传入会话保证账本和通知同事务。"""
        ...


async def noop_refund_result(result: ConfirmedWechatPayResult, db: AsyncSession) -> None:
    """宿主未配置通知时的空sink；不推导业务权益。"""
    return


class RefundManualReviewHook(Protocol):
    """超时人工核对通知与manual_required标记同事务；禁止自行commit或发外部消息。"""

    async def __call__(self, db: AsyncSession, *, refund_no: str, order_no: str) -> bool | None:
        """首次超过24小时调用；返回值可用于宿主去重，不影响事务提交。"""
        ...


async def noop_refund_manual_review(db: AsyncSession, *, refund_no: str, order_no: str) -> None:
    """未注入人工核对通知时的空sink。"""
    return
