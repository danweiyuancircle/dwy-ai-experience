"""独立支付命令在触网前已有稳定记录，取消和未知结果可按原号恢复。"""

import asyncio

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from dwy_payment import PaymentConfig, create_payment
from dwy_payment.errors import PaymentChannelError
from dwy_payment.models import PaymentOrder


class Gateway:
    """模拟渠道仅接受已提交可见的意图，并记录重试参数。"""

    def __init__(self, factory, error=None):
        self.factory = factory
        self.calls = []
        self.error = error

    def is_configured(self):
        return True

    async def create_native(self, **kwargs):
        async with self.factory() as db:
            assert await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == kwargs["order_no"]))
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return "weixin://wxpay/test"


async def test_payment_is_committed_before_network_and_repeated_key_reuses_it(payment_db):
    gateway = Gateway(payment_db)
    args = dict(session_factory=payment_db, gateway=gateway, config=PaymentConfig(), user_id="u1",
                amount_fen=1000, description="商品", idempotency_key="business-1")
    first = await create_payment(**args)
    second = await create_payment(**args)
    assert first.order_no == second.order_no
    assert len(gateway.calls) == 1


@pytest.mark.parametrize("error", [PaymentChannelError("unknown"), asyncio.CancelledError()])
async def test_unknown_or_cancelled_call_recovers_same_order_and_original_expiry(payment_db, error):
    gateway = Gateway(payment_db, error=error)
    args = dict(session_factory=payment_db, gateway=gateway, config=PaymentConfig(), user_id="u1",
                amount_fen=1000, description="商品", idempotency_key="business-unknown")
    with pytest.raises((Exception, asyncio.CancelledError)):
        await create_payment(**args)
    async with payment_db() as db:
        order = await db.scalar(select(PaymentOrder))
        assert order.status == "pending"
        order_no, expires_at = order.order_no, order.expires_at
    gateway.error = None
    args["config"] = PaymentConfig(order_expire_minutes=60)
    result = await create_payment(**args)
    assert result.order_no == order_no
    assert gateway.calls[0]["time_expire"] == gateway.calls[1]["time_expire"] == expires_at
    async with payment_db() as db:
        assert await db.scalar(select(func.count()).select_from(PaymentOrder)) == 1


async def test_factory_expiring_on_commit_is_supported(payment_db):
    async with payment_db() as db:
        engine = db.bind
    factory = async_sessionmaker(engine, expire_on_commit=True)
    result = await create_payment(
        session_factory=factory, gateway=Gateway(factory), config=PaymentConfig(),
        user_id="u1", amount_fen=1000, description="商品", idempotency_key="business-expire",
    )
    assert result.code_url == "weixin://wxpay/test"


async def test_durable_entry_requires_a_stable_key(payment_db):
    gateway = Gateway(payment_db)
    with pytest.raises(ValueError):
        await create_payment(
            session_factory=payment_db, gateway=gateway, config=PaymentConfig(),
            user_id="u1", amount_fen=1000, description="商品", idempotency_key=None,
        )
    assert gateway.calls == []
