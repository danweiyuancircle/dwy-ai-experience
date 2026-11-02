"""显式启用的本机 PostgreSQL 并发验收，不读取宿主部署数据库配置。"""

import asyncio
import os
from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from dwyeapi import dt
from dwyeapi.database import Base
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from dwy_payment import NoOpPaymentHook, PaymentConfig, PaymentService, create_payment
from dwy_payment.errors import PaymentChannelError
from dwy_payment.events import PaymentEvent, acknowledge_payment_event, pending_payment_events
from dwy_payment.models import PaymentOrder
from dwy_payment.protocols import ChannelNotify
from dwy_payment.refunds.commands import request_refund
from dwy_payment.refunds.models import RefundRecord
from dwy_payment.refunds.protocols import RefundChannelResult
from dwy_payment.refunds.service import RefundResultService

PG_TEST_URL = os.environ.get("TEST_PAYMENT_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not PG_TEST_URL, reason="未显式启用本机 payment_test PostgreSQL 测试库")


class RefundGateway:
    """只模拟渠道网络，退款意图、锁、CAS 和事件始终使用真实 PostgreSQL。"""

    supports_refund_results = True

    def __init__(self, order):
        self.query = AsyncMock(return_value=ChannelNotify(
            order_no=order.order_no, amount_fen=order.amount_fen, transaction_id=order.channel_trade_no,
            trade_state="SUCCESS", trade_type="NATIVE", event_type="QUERY", raw="{}",
        ))
        self.refund = AsyncMock(return_value="PROCESSING")
        self.refund_query = AsyncMock()

    def is_configured(self):
        return True


class PaymentGateway:
    """支付二维码替身，保留原单号和原截止时间，实际意图由数据库维护。"""

    def __init__(self):
        self.create_native = AsyncMock(return_value="weixin://wxpay/isolated-postgres-test")

    def is_configured(self):
        return True


@pytest.fixture
async def postgres_case():
    """每测建立随机 schema，连接严格限定为显式指定的本机合成测试库。"""
    url = make_url(PG_TEST_URL)
    if (url.drivername != "postgresql+asyncpg" or url.host not in {"localhost", "127.0.0.1", "::1"}
            or url.database != "payment_test"):
        pytest.fail("仅允许显式连接本机 payment_test 合成数据库")
    schema = "payment_pg_" + uuid4().hex
    control = create_async_engine(url, poolclass=NullPool)
    engine = create_async_engine(
        url, poolclass=NullPool,
        connect_args={"server_settings": {"search_path": schema, "lock_timeout": "8000", "statement_timeout": "9000"}},
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with control.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with sessions() as db:
            order = PaymentOrder(user_id="isolated-host-user", order_no=uuid4().hex, amount_fen=1000,
                                 channel="wechat", channel_trade_no="pg-isolated-paid-transaction", status="success",
                                 description="合成数据，不是真实交易")
            db.add(order)
            await db.commit()
            await db.refresh(order)
            db.expunge(order)
        yield sessions, order, RefundGateway(order)
    finally:
        await engine.dispose()
        async with control.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await control.dispose()


async def _request(case, refund_no="pg-refund-1", refund_fen=600):
    sessions, order, gateway = case
    return await request_refund(order=order, refund_no=refund_no, refund_fen=refund_fen,
                                session_factory=sessions, gateway=gateway)


async def _cancel(*tasks):
    for task in tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def test_postgres_same_refund_key_concurrent_requests_submit_once(postgres_case):
    """两个独立数据库会话争同一退款键，只能形成一个资金预留及渠道请求。"""
    first, second = await asyncio.wait_for(asyncio.gather(_request(postgres_case), _request(postgres_case)), timeout=10)
    assert first.id == second.id
    postgres_case[2].refund.assert_awaited_once()
    async with postgres_case[0]() as db:
        assert await db.scalar(select(func.count()).select_from(RefundRecord)) == 1
        assert await db.scalar(select(func.sum(RefundRecord.refund_fen))) == 600


async def test_postgres_distinct_keys_cannot_concurrently_overreserve_original_payment(postgres_case):
    """同支付两个600分意图并发时，1000分原额只能容纳其中一个。"""
    results = await asyncio.wait_for(asyncio.gather(
        _request(postgres_case, refund_no="pg-refund-a"), _request(postgres_case, refund_no="pg-refund-b"),
        return_exceptions=True,
    ), timeout=10)
    assert sum(isinstance(result, RefundRecord) for result in results) == 1
    assert sum(isinstance(result, ValueError) for result in results) == 1
    postgres_case[2].refund.assert_awaited_once()
    async with postgres_case[0]() as db:
        assert await db.scalar(select(func.sum(RefundRecord.refund_fen))) == 600


async def test_postgres_acceptance_and_callback_race_preserves_success_and_replay(postgres_case):
    """回调持退款行锁时让受理响应争锁，不死锁、不降级，结果可重复读取直至业务确认。"""
    sessions, order, gateway = postgres_case
    submitted, allow_acceptance = asyncio.Event(), asyncio.Event()
    callback_holds_refund, allow_callback = asyncio.Event(), asyncio.Event()

    async def accepted(*_args):
        submitted.set()
        await allow_acceptance.wait()
        return "PROCESSING"

    async def held_hook(_result, _db):
        callback_holds_refund.set()
        await allow_callback.wait()

    note = RefundChannelResult(
        order_no=order.order_no, transaction_id=order.channel_trade_no, amount_fen=1000,
        refund_no="pg-refund-1", refund_id="pg-isolated-refund", refund_fen=600, refund_status="SUCCESS",
    )

    async def callback():
        async with sessions() as db:
            await RefundResultService(db, result_hook=held_hook).apply(note, queried=True)
            await db.commit()

    gateway.refund.side_effect = accepted
    requesting = asyncio.create_task(_request(postgres_case))
    callback_task = None
    try:
        await asyncio.wait_for(submitted.wait(), timeout=10)
        callback_task = asyncio.create_task(callback())
        await asyncio.wait_for(callback_holds_refund.wait(), timeout=10)
        allow_acceptance.set()
        await asyncio.sleep(0.05)
        allow_callback.set()
        result, _ = await asyncio.wait_for(asyncio.gather(requesting, callback_task), timeout=10)
        assert result.provider_status == result.verified_status == "SUCCESS"
    finally:
        allow_acceptance.set()
        allow_callback.set()
        await _cancel(requesting, *([callback_task] if callback_task is not None else []))
    async with sessions() as db:
        await RefundResultService(db).apply(note, queried=True)
        await db.commit()
        events = await pending_payment_events(db)
        assert len(events) == 1
        event_id = events[0].event_id
        assert events[0].payload["event_type"] == "REFUND.SUCCESS"
        await acknowledge_payment_event(db, event_id)
        await db.rollback()
    async with sessions() as db:
        assert len(await pending_payment_events(db)) == 1
        await acknowledge_payment_event(db, event_id)
        await db.commit()
    async with sessions() as db:
        assert await pending_payment_events(db) == []
        assert await db.scalar(select(func.count()).select_from(PaymentEvent)) == 1
        record = await db.scalar(select(RefundRecord))
        record.last_query_at = dt.now() - timedelta(minutes=2)
        await db.commit()
    replayed = await _request(postgres_case)
    assert replayed.verified_status == "SUCCESS"
    gateway.refund.assert_awaited_once()
    gateway.refund_query.assert_not_awaited()


async def test_postgres_create_payment_concurrent_key_is_persisted_before_network_and_submits_once(postgres_case):
    """独立支付命令先提交意图，同键并发在第二会话行锁后复用唯一二维码。"""
    sessions = postgres_case[0]
    gateway = PaymentGateway()
    entered, release = asyncio.Event(), asyncio.Event()

    async def native(**params):
        async with sessions() as db:
            persisted = await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == params["order_no"]))
            assert persisted is not None
            assert persisted.expires_at == params["time_expire"]
        entered.set()
        await release.wait()
        return "weixin://wxpay/isolated-postgres-test"

    gateway.create_native.side_effect = native
    arguments = dict(session_factory=sessions, gateway=gateway, config=PaymentConfig(), user_id="pg-create-user",
                     amount_fen=1000, description="PG并发支付意图", idempotency_key="pg-create-intent")
    first = asyncio.create_task(create_payment(**arguments))
    second = None
    try:
        await asyncio.wait_for(entered.wait(), timeout=10)
        second = asyncio.create_task(create_payment(**arguments))
        await asyncio.sleep(0.05)
        release.set()
        first_result, second_result = await asyncio.wait_for(asyncio.gather(first, second), timeout=10)
        assert first_result.order_no == second_result.order_no
        assert first_result.code_url == second_result.code_url == "weixin://wxpay/isolated-postgres-test"
    finally:
        release.set()
        await _cancel(first, *([second] if second is not None else []))
    gateway.create_native.assert_awaited_once()
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(PaymentOrder).where(
            PaymentOrder.idempotency_key == "pg-create-intent",
        )) == 1


async def test_postgres_unknown_create_recovers_original_key_and_expiry_once_under_concurrency(postgres_case):
    """未知下单后并发重试仍用已提交原号及截止，不能受新配置影响或生成第二订单。"""
    from dwyeapi.exceptions import BusinessError

    sessions = postgres_case[0]
    gateway = PaymentGateway()
    arguments = dict(session_factory=sessions, gateway=gateway, config=PaymentConfig(), user_id="pg-create-user",
                     amount_fen=1000, description="PG未知支付恢复", idempotency_key="pg-create-recovery")
    gateway.create_native.side_effect = PaymentChannelError("synthetic unknown creation")
    with pytest.raises(BusinessError):
        await create_payment(**arguments)
    original = gateway.create_native.await_args.kwargs
    gateway.create_native.side_effect = None
    arguments["config"] = PaymentConfig(order_expire_minutes=60)
    first, second = await asyncio.wait_for(asyncio.gather(create_payment(**arguments), create_payment(**arguments)),
                                           timeout=10)
    assert first.order_no == second.order_no == original["order_no"]
    assert gateway.create_native.await_count == 2
    assert gateway.create_native.await_args.kwargs == original
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(PaymentOrder).where(
            PaymentOrder.idempotency_key == "pg-create-recovery",
        )) == 1


async def test_postgres_close_racing_verified_payment_cannot_overwrite_received_money(postgres_case):
    """真实两个 PG 会话中收款先提交，迟到关单响应不能覆盖成功或丢失持久资金事件。"""
    sessions = postgres_case[0]
    gateway = PaymentGateway()
    created = await create_payment(session_factory=sessions, gateway=gateway, config=PaymentConfig(),
                                   user_id="pg-close-user", amount_fen=1000, description="PG关单收款竞争",
                                   idempotency_key="pg-close-intent")
    closing, release_close = asyncio.Event(), asyncio.Event()

    async def close(_order_no):
        closing.set()
        await release_close.wait()

    gateway.close = AsyncMock(side_effect=close)
    gateway.parse_notify = AsyncMock(return_value=ChannelNotify(
        order_no=created.order_no, amount_fen=1000, transaction_id="pg-payment-during-close", trade_state="SUCCESS",
        trade_type="NATIVE", event_type="TRANSACTION.SUCCESS", raw="{}",
    ))

    async def close_order():
        async with sessions() as db:
            row = await PaymentService(db, gateway, NoOpPaymentHook(), PaymentConfig()).close_for_user(
                "pg-close-user", created.order_no,
            )
            return row.status

    closing_task = asyncio.create_task(close_order())
    try:
        await asyncio.wait_for(closing.wait(), timeout=10)
        async with sessions() as db:
            assert await asyncio.wait_for(
                PaymentService(db, gateway, NoOpPaymentHook(), PaymentConfig()).handle_notify({}, b"{}"), timeout=10,
            )
        release_close.set()
        assert await asyncio.wait_for(closing_task, timeout=10) == "success"
    finally:
        release_close.set()
        await _cancel(closing_task)
    async with sessions() as db:
        row = await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == created.order_no))
        assert row.status == "success" and row.channel_trade_no == "pg-payment-during-close"
        events = await pending_payment_events(db)
        assert len(events) == 1 and events[0].payload["event_type"] == "PAYMENT.SUCCESS"
