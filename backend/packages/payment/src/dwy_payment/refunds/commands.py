"""业务无关的持久资金退款命令，不承担审核、密码或商品权益政策。"""

from datetime import timedelta

from dwyeapi import dt
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dwy_payment.constants import ORDER_NO_RE
from dwy_payment.errors import PaymentChannelError, PaymentNotConfiguredError, RefundNotFoundError
from dwy_payment.models import PaymentOrder
from dwy_payment.refunds.models import RefundRecord
from dwy_payment.refunds.protocols import RefundResultHook
from dwy_payment.refunds.service import RefundResultService, persist_refund_intent


async def _record(factory, refund_no: str) -> RefundRecord:
    async with factory() as db:
        row = await db.scalar(select(RefundRecord).where(RefundRecord.refund_no == refund_no))
        if row is None:
            raise ValueError("refund intent missing")
        db.expunge(row)
        return row


async def _claim(db: AsyncSession, record: RefundRecord) -> bool:
    if record.verified_status in {"SUCCESS", "CLOSED"}:
        return False
    now = dt.now()
    updated = await db.execute(update(RefundRecord).where(
        RefundRecord.id == record.id, RefundRecord.version == record.version,
        or_(RefundRecord.last_query_at.is_(None), RefundRecord.last_query_at <= now - timedelta(seconds=60)),
    ).values(last_query_at=now, next_query_at=now + timedelta(seconds=60), version=record.version + 1)
      .execution_options(synchronize_session=False))
    await db.commit()
    return updated.rowcount == 1


async def request_refund(
    *, order: PaymentOrder, refund_no: str, refund_fen: int, session_factory=None, gateway=None,
    result_hook: RefundResultHook | None = None,
) -> RefundRecord:
    """为已持久支付申请退款，同号原参数幂等，超时后只查原号或明确不存在再原号恢复。

    宿主必须先完成授权和业务预留提交；本函数不提交宿主会话。order 仅提供订单身份，
    原金额/交易号以数据库为准。预留和60秒执行租约先独立提交，才允许触网。
    预期渠道失败返回仍占用金额的待核对记录；不将受理成功当作已到账。
    """
    from dwy_payment.runtime import get_gateway, get_refund_session_factory

    if not isinstance(order.order_no, str) or not ORDER_NO_RE.fullmatch(order.order_no):
        raise ValueError("invalid refund payment")
    factory = get_refund_session_factory() if session_factory is None else session_factory
    channel = get_gateway() if gateway is None else gateway
    require = getattr(channel, "require", None)
    if callable(require):
        channel = require("wechat")
    if not channel.is_configured() or getattr(channel, "supports_refund_results", False) is not True:
        raise PaymentNotConfiguredError("refund result support is required")
    async with factory() as db:
        payment = await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == order.order_no))
        if (payment is None or payment.is_deleted or payment.channel != "wechat"
                or payment.status not in {"success", "refund"} or not payment.channel_trade_no):
            raise ValueError("refund payment is not a persisted successful transaction")
        db.expunge(payment)
    record, created = await persist_refund_intent(
        order=payment, refund_no=refund_no, refund_fen=refund_fen, session_factory=factory,
    )
    async with factory() as db:
        claimed = await _claim(db, record)
    if not claimed:
        return await _record(factory, refund_no)
    if not created:
        try:
            result = await channel.refund_query(refund_no)
        except RefundNotFoundError:
            pass
        except (PaymentChannelError, PaymentNotConfiguredError):
            return await _record(factory, refund_no)
        else:
            if (result.order_no, result.refund_no, result.transaction_id, result.amount_fen, result.refund_fen) != (
                payment.order_no, refund_no, payment.channel_trade_no, payment.amount_fen, refund_fen,
            ):
                raise ValueError("refund query mismatch")
            async with factory() as db:
                await RefundResultService(db, result_hook=result_hook).apply(result, queried=True)
                await db.commit()
            return await _record(factory, refund_no)
    try:
        original = await channel.query(payment.order_no)
    except (PaymentChannelError, PaymentNotConfiguredError):
        return await _record(factory, refund_no)
    if (original.order_no != payment.order_no or original.amount_fen != payment.amount_fen
            or original.transaction_id != payment.channel_trade_no or original.trade_state != "SUCCESS"):
        raise ValueError("original payment query mismatch")
    try:
        accepted = await channel.refund(payment.order_no, refund_no, refund_fen, payment.amount_fen)
    except (PaymentChannelError, PaymentNotConfiguredError):
        return await _record(factory, refund_no)
    if accepted not in {"SUCCESS", "PROCESSING"}:
        raise PaymentChannelError("refund acceptance state invalid")
    async with factory() as db:
        # 回调可能先提交终态，受理响应只能推进尚未核验的REQUESTED，不能覆盖成功。
        await db.execute(update(RefundRecord).where(
            RefundRecord.refund_no == refund_no, RefundRecord.provider_status == "REQUESTED",
            RefundRecord.verified_status.is_(None),
        ).values(provider_status=accepted, version=RefundRecord.version + 1))
        await db.commit()
    return await _record(factory, refund_no)
