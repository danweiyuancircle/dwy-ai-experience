"""独立支付指令；先持久意图，进程中断后仍可按原号核对和恢复。"""

from sqlalchemy import select

from dwy_payment.config import PaymentConfig
from dwy_payment.models import PaymentOrder
from dwy_payment.protocols import NoOpPaymentHook, PaymentGateway
from dwy_payment.schemas import PaymentEcho
from dwy_payment.service import PaymentService


async def create_payment(
    *, session_factory, gateway: PaymentGateway, config: PaymentConfig,
    user_id: str, amount_fen: int, description: str, idempotency_key: str, channel: str = "wechat",
) -> PaymentEcho:
    """可信宿主先持久自己的业务关联，再调用本函数；本函数不使用宿主请求会话。

    同键参数固定，未知下单只重取原号二维码；第二个短会话的行锁串行同号渠道调用。
    会话工厂可设置expire_on_commit=True，本函数不会在commit后读取过期ORM属性。
    """
    if not isinstance(idempotency_key, str) or not idempotency_key:
        raise ValueError("a stable payment idempotency key is required")
    async with session_factory() as db:
        service = PaymentService(db, gateway, NoOpPaymentHook(), config)
        order = await service._prepare(
            user_id=user_id, amount_fen=amount_fen, description=description,
            channel=channel, idempotency_key=idempotency_key,
        )
        order_no = order.order_no
        await db.commit()
    async with session_factory() as db:
        await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == order_no).with_for_update())
        service = PaymentService(db, gateway, NoOpPaymentHook(), config)
        result = await service.create(
            user_id=user_id, amount_fen=amount_fen, description=description,
            channel=channel, idempotency_key=idempotency_key,
        )
        await db.commit()
        return result
