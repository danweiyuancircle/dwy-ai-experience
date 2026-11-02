"""支付指令、回调与持久事件的独立契约。"""

import pytest
from dwyeapi.exceptions import BusinessError
from sqlalchemy import func, select

from dwy_payment import NoOpPaymentHook, PaymentConfig, PaymentService
from dwy_payment.config import WechatPayConfig
from dwy_payment.errors import PaymentChannelError
from dwy_payment.events import (
    PaymentEvent,
    acknowledge_payment_event,
    pending_payment_events,
)
from dwy_payment.models import PaymentOrder
from dwy_payment.protocols import ChannelNotify


class Gateway:
    """确定性模拟渠道，不访问商户。"""

    def __init__(self):
        self.orders = []
        self.fail = False
        self.notification = None

    def is_configured(self):
        return True

    async def create_native(self, **kwargs):
        self.orders.append(kwargs["order_no"])
        if self.fail:
            raise PaymentChannelError("unknown")
        return "weixin://wxpay/bizpayurl?pr=test"

    async def parse_notify(self, headers, body):
        return self.notification

    async def query(self, order_no):
        return self.notification


def service(db, gateway):
    return PaymentService(db, gateway, NoOpPaymentHook(), PaymentConfig())


async def test_same_key_reuses_order_and_conflicting_parameters_fail(payment_db):
    gateway = Gateway()
    async with payment_db() as db:
        api = service(db, gateway)
        first = await api.create(user_id="u1", amount_fen=1000, description="商品", idempotency_key="order-1")
        await db.commit()
        second = await api.create(user_id="u1", amount_fen=1000, description="商品", idempotency_key="order-1")
        assert first.order_no == second.order_no
        assert gateway.orders == [first.order_no]
        with pytest.raises(BusinessError):
            await api.create(user_id="u1", amount_fen=900, description="商品", idempotency_key="order-1")
        assert await db.scalar(select(func.count()).select_from(PaymentOrder)) == 1


@pytest.mark.parametrize("amount", [True, 1.2, 0, -1, 100000001])
async def test_invalid_amount_never_reaches_channel(payment_db, amount):
    gateway = Gateway()
    async with payment_db() as db:
        with pytest.raises(BusinessError):
            await service(db, gateway).create(user_id="u1", amount_fen=amount, description="商品")
    assert gateway.orders == []


async def test_unknown_creation_keeps_original_pending_for_late_verified_callback(payment_db):
    gateway = Gateway()
    gateway.fail = True
    async with payment_db() as db:
        api = service(db, gateway)
        with pytest.raises(BusinessError):
            await api.create(user_id="u1", amount_fen=1000, description="商品", idempotency_key="order-unknown")
        order = await db.scalar(select(PaymentOrder))
        assert order.status == "pending"
        gateway.notification = ChannelNotify(
            order_no=order.order_no, amount_fen=1000, trade_state="SUCCESS", trade_type="NATIVE",
            event_type="TRANSACTION.SUCCESS", transaction_id="tx1", raw="{}",
        )
        assert await api.handle_notify({}, b"{}")
        assert await api.handle_notify({}, b"{}")
        assert len(await pending_payment_events(db)) == 1
        assert (await db.get(PaymentOrder, order.id)).status == "success"


async def test_result_replays_until_business_acknowledges_in_committed_transaction(payment_db):
    gateway = Gateway()
    async with payment_db() as db:
        api = service(db, gateway)
        order = await api.create(user_id="u1", amount_fen=1000, description="商品")
        await db.commit()
        gateway.notification = ChannelNotify(
            order_no=order.order_no, amount_fen=1000, trade_state="SUCCESS", trade_type="NATIVE",
            event_type="TRANSACTION.SUCCESS", transaction_id="tx1", raw="{}",
        )
        assert await api.handle_notify({}, b"{}")
        event_id = (await pending_payment_events(db))[0].event_id
        await acknowledge_payment_event(db, event_id)
        await db.rollback()
    async with payment_db() as db:
        assert (await pending_payment_events(db))[0].event_id == event_id
        await acknowledge_payment_event(db, event_id)
        await db.commit()
        assert await pending_payment_events(db) == []
        assert await db.scalar(select(func.count()).select_from(PaymentEvent)) == 1


async def test_duplicate_with_different_transaction_and_cross_channel_is_rejected(payment_db):
    gateway = Gateway()
    async with payment_db() as db:
        api = service(db, gateway)
        order = await api.create(user_id="u1", amount_fen=1000, description="商品")
        await db.commit()
        gateway.notification = ChannelNotify(
            order_no=order.order_no, amount_fen=1000, trade_state="SUCCESS", trade_type="NATIVE",
            event_type="TRANSACTION.SUCCESS", transaction_id="tx1", raw="{}",
        )
        assert not await api.handle_notify({}, b"{}", channel="alipay")
        assert await api.handle_notify({}, b"{}")
        gateway.notification.transaction_id = "tx-other"
        assert not await api.handle_notify({}, b"{}")


def test_merchant_secrets_are_not_exported_or_shown_in_configuration_errors():
    from pydantic import ValidationError

    secret = "sensitive-value"
    config = WechatPayConfig(private_key=secret, apiv3_key=secret)
    assert secret not in repr(config)
    assert secret not in config.model_dump_json()
    with pytest.raises(ValidationError) as error:
        WechatPayConfig(apiv3_key=secret * 100)
    assert secret not in str(error.value)


async def test_close_does_not_overwrite_success_committed_while_channel_was_closing(payment_db):
    gateway = Gateway()
    async with payment_db() as db:
        api = service(db, gateway)
        created = await api.create(user_id="u1", amount_fen=1000, description="商品")
        await db.commit()

        async def close(order_no):
            from sqlalchemy import update

            await db.execute(update(PaymentOrder).where(PaymentOrder.order_no == order_no).values(status="success"))

        gateway.close = close
        order = await api.close_for_user("u1", created.order_no)
        assert order.status == "success"
