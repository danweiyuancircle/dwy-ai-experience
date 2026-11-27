"""纯资金退款命令的独立数据库验收，不导入任何宿主应用或访问真实支付。"""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from dwyeapi import dt
from dwyeapi.database import Base
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_payment.errors import PaymentChannelError, RefundNotFoundError
from dwy_payment.models import PaymentOrder
from dwy_payment.protocols import ChannelNotify
from dwy_payment.refunds.commands import request_refund
from dwy_payment.refunds.models import RefundRecord
from dwy_payment.refunds.protocols import RefundChannelResult
from dwy_payment.refunds.service import RefundResultService, persist_refund_intent
from dwy_payment.runtime import configure_refunds


class RefundGateway:
    """合成渠道：捕获原参数，查询凭据与同一笔已支付交易一致。"""

    supports_refund_results = True

    def __init__(self, order):
        self.query = AsyncMock(return_value=ChannelNotify(
            order_no=order.order_no, amount_fen=order.amount_fen, trade_state="SUCCESS", trade_type="NATIVE",
            event_type="QUERY", transaction_id=order.channel_trade_no, raw="{}",
        ))
        self.refund = AsyncMock(return_value="PROCESSING")
        self.refund_query = AsyncMock(side_effect=RefundNotFoundError("refund not found"))

    def is_configured(self):
        return True


@pytest.fixture
async def funds(tmp_path):
    """新建隔离数据库及已提交的原支付，fixture 不读取运行时 factory 或数据库 URL。"""
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'refund-commands.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as db:
        order = PaymentOrder(user_id="host-user", order_no="funds-original-000001", amount_fen=1000,
                             channel="wechat", channel_trade_no="wx-original-000001", status="success",
                             description="合成资金退款测试")
        db.add(order)
        await db.commit()
        await db.refresh(order)
        db.expunge(order)
    gateway = RefundGateway(order)
    configure_refunds()
    yield sessions, order, gateway
    configure_refunds()
    await engine.dispose()


async def _request(funds, *, refund_no="refund-command-1", refund_fen=600, order=None, result_hook=None):
    sessions, original, gateway = funds
    return await request_refund(order=original if order is None else order, refund_no=refund_no,
                                refund_fen=refund_fen, session_factory=sessions, gateway=gateway,
                                result_hook=result_hook)


async def _expire_lease(sessions, refund_no="refund-command-1"):
    async with sessions() as db:
        record = await db.scalar(select(RefundRecord).where(RefundRecord.refund_no == refund_no))
        record.last_query_at = dt.now() - timedelta(minutes=2)
        record.next_query_at = dt.now() - timedelta(minutes=1)
        await db.commit()


def _result(order, refund_no="refund-command-1", refund_fen=600, status="SUCCESS"):
    return RefundChannelResult(order_no=order.order_no, transaction_id=order.channel_trade_no,
                               amount_fen=order.amount_fen, refund_no=refund_no, refund_id="wx-refund-command-1",
                               refund_fen=refund_fen, refund_status=status)


async def test_commits_intent_before_channel_and_leaves_payment_pending_refund(funds):
    sessions, order, gateway = funds

    async def refund(*args):
        async with sessions() as db:
            saved = await db.scalar(select(RefundRecord).where(RefundRecord.refund_no == args[1]))
            assert saved is not None
            assert saved.refund_fen == 600
        return "PROCESSING"

    gateway.refund.side_effect = refund
    record = await _request(funds)
    assert record.provider_status == "PROCESSING"
    gateway.refund.assert_awaited_once_with(order.order_no, "refund-command-1", 600, 1000)
    async with sessions() as db:
        original = await db.get(PaymentOrder, order.id)
        assert original.refunded_fen == 0
        assert original.status == "success"


async def test_same_key_and_parameters_do_not_resubmit_during_lease(funds):
    first = await _request(funds)
    again = await _request(funds)
    assert first.id == again.id
    funds[2].refund.assert_awaited_once()
    funds[2].refund_query.assert_not_awaited()


async def test_same_key_with_conflicting_amount_is_rejected(funds):
    await _request(funds)
    with pytest.raises(ValueError, match="mismatch"):
        await _request(funds, refund_fen=500)
    funds[2].refund.assert_awaited_once()


@pytest.mark.parametrize("amount", [True, 1.5, "600", 0, -1, 1001])
async def test_amount_is_strict_integer_in_original_payment_range(funds, amount):
    with pytest.raises(ValueError):
        await _request(funds, refund_fen=amount)
    funds[2].refund.assert_not_awaited()
    async with funds[0]() as db:
        assert await db.scalar(select(func.count()).select_from(RefundRecord)) == 0


@pytest.mark.parametrize("refund_no", ["", "R" * 65, "with space", "bad/number", "中文退款号"])
async def test_refund_number_has_bounded_provider_character_set(funds, refund_no):
    with pytest.raises(ValueError):
        await _request(funds, refund_no=refund_no)
    funds[2].refund.assert_not_awaited()


async def test_concurrent_distinct_refunds_cannot_reserve_over_original_total(funds):
    results = await asyncio.gather(_request(funds, refund_no="refund-concurrent-a"),
                                   _request(funds, refund_no="refund-concurrent-b"), return_exceptions=True)
    assert sum(isinstance(result, RefundRecord) for result in results) == 1
    assert sum(isinstance(result, ValueError) for result in results) == 1
    funds[2].refund.assert_awaited_once()
    async with funds[0]() as db:
        assert await db.scalar(select(func.sum(RefundRecord.refund_fen))) == 600


@pytest.mark.parametrize("status", ["PROCESSING", "SUCCESS", "ABNORMAL"])
async def test_processing_success_and_abnormal_all_reserve_original_money(funds, status):
    sessions, order, gateway = funds
    record, _ = await persist_refund_intent(order=order, refund_no="reserved-refund", refund_fen=600,
                                          session_factory=sessions)
    async with sessions() as db:
        saved = await db.get(RefundRecord, record.id)
        saved.provider_status = status
        saved.verified_status = None if status == "PROCESSING" else status
        await db.commit()
    with pytest.raises(ValueError, match="amount"):
        await _request(funds, refund_fen=500)
    gateway.refund.assert_not_awaited()


async def test_verified_closed_releases_original_money_reservation(funds):
    sessions, order, gateway = funds
    record, _ = await persist_refund_intent(order=order, refund_no="closed-refund", refund_fen=600,
                                          session_factory=sessions)
    async with sessions() as db:
        saved = await db.get(RefundRecord, record.id)
        saved.provider_status = saved.verified_status = "CLOSED"
        await db.commit()
    result = await _request(funds, refund_fen=1000)
    assert result.refund_fen == 1000
    gateway.refund.assert_awaited_once()


async def test_timeout_recovers_by_querying_original_number_and_runs_result_hook(funds):
    sessions, order, gateway = funds
    hook = AsyncMock()
    configure_refunds(session_factory=sessions, result_hook=hook)
    gateway.refund.side_effect = PaymentChannelError("synthetic timeout")
    first = await _request(funds)
    assert first.verified_status is None
    await _expire_lease(sessions)
    gateway.refund_query.side_effect = None
    gateway.refund_query.return_value = _result(order)
    recovered = await _request(funds)
    assert recovered.id == first.id
    assert recovered.verified_status == "SUCCESS"
    gateway.refund.assert_awaited_once()
    gateway.refund_query.assert_awaited_once_with("refund-command-1")
    hook.assert_awaited_once()


@pytest.mark.parametrize("missing", [False, True])
async def test_only_verified_not_found_allows_same_number_parameter_retry(funds, missing):
    sessions, order, gateway = funds
    gateway.refund.side_effect = PaymentChannelError("synthetic timeout")
    await _request(funds)
    await _expire_lease(sessions)
    gateway.refund.side_effect = None
    gateway.refund_query.side_effect = (RefundNotFoundError("not found") if missing
                                       else PaymentChannelError("query unavailable"))
    await _request(funds)
    assert gateway.refund.await_count == (2 if missing else 1)
    for call in gateway.refund.await_args_list:
        assert call.args == (order.order_no, "refund-command-1", 600, 1000)


@pytest.mark.parametrize("field,value", [("amount_fen", 999), ("transaction_id", "wrong-transaction"),
                                         ("order_no", "other-order-0001"), ("trade_state", "NOTPAY")])
async def test_original_channel_payment_must_match_persisted_order(funds, field, value):
    _, order, gateway = funds
    values = dict(order_no=order.order_no, amount_fen=1000, transaction_id=order.channel_trade_no,
                  trade_state="SUCCESS", trade_type="NATIVE", event_type="QUERY", raw="{}")
    values[field] = value
    gateway.query.return_value = ChannelNotify(**values)
    with pytest.raises(ValueError, match="payment"):
        await _request(funds)
    gateway.refund.assert_not_awaited()


async def test_persisted_payment_is_authority_not_stale_or_fabricated_snapshot(funds):
    _, order, gateway = funds
    stale = PaymentOrder(order_no=order.order_no, amount_fen=1, channel="wechat", channel_trade_no="stale",
                         status="pending", user_id="irrelevant-snapshot", description="stale")
    record = await _request(funds, order=stale)
    assert (record.amount_fen, record.transaction_id) == (1000, order.channel_trade_no)
    gateway.refund.assert_awaited_once_with(order.order_no, "refund-command-1", 600, 1000)


async def test_nonexistent_payment_never_creates_refund_or_calls_channel(funds):
    missing = PaymentOrder(order_no="nonexistent-order-0001", amount_fen=1000, channel="wechat",
                           channel_trade_no="fake-paid", status="success", user_id="fake", description="fake")
    with pytest.raises(ValueError, match="payment"):
        await _request(funds, order=missing)
    funds[2].refund.assert_not_awaited()


async def test_callback_success_during_acceptance_cannot_be_downgraded(funds):
    sessions, order, gateway = funds

    async def refund(*_args):
        async with sessions() as db:
            await RefundResultService(db).apply(_result(order), queried=True)
            await db.commit()
        return "PROCESSING"

    gateway.refund.side_effect = refund
    record = await _request(funds)
    assert (record.provider_status, record.verified_status) == ("SUCCESS", "SUCCESS")
    gateway.refund.assert_awaited_once()


async def test_concurrent_same_key_reserves_and_submits_once(funds):
    first, second = await asyncio.gather(_request(funds), _request(funds))
    assert first.id == second.id
    funds[2].refund.assert_awaited_once()
    async with funds[0]() as db:
        assert await db.scalar(select(func.count()).select_from(RefundRecord)) == 1


async def test_legacy_refunded_marker_and_pending_record_are_not_double_counted(funds):
    sessions, order, gateway = funds
    await persist_refund_intent(order=order, refund_no="previous-refund", refund_fen=600, session_factory=sessions)
    async with sessions() as db:
        original = await db.get(PaymentOrder, order.id)
        original.refunded_fen = 600
        original.refund_no = "previous-refund"
        await db.commit()
    result = await _request(funds, refund_fen=400)
    assert result.refund_fen == 400
    with pytest.raises(ValueError, match="amount"):
        await _request(funds, refund_no="one-more-cent", refund_fen=1)
    gateway.refund.assert_awaited_once()


async def test_unattributed_legacy_refunded_money_requires_reconciliation(funds):
    sessions, order, gateway = funds
    async with sessions() as db:
        original = await db.get(PaymentOrder, order.id)
        original.refunded_fen = 600
        original.refund_no = "legacy-without-record"
        await db.commit()
    with pytest.raises(ValueError, match="legacy.*reconciliation"):
        await _request(funds, refund_fen=400)
    gateway.refund.assert_not_awaited()
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(RefundRecord)) == 0


@pytest.mark.parametrize("field,value", [
    ("order_no", "other-query-order"), ("refund_no", "other-query-refund"),
    ("transaction_id", "other-original-trade"), ("amount_fen", 999), ("refund_fen", 500),
])
async def test_refund_query_identity_must_match_requested_intent_before_apply(funds, field, value):
    sessions, order, gateway = funds
    gateway.refund.side_effect = PaymentChannelError("synthetic timeout")
    await _request(funds)
    await _expire_lease(sessions)
    note = _result(order).model_dump()
    note[field] = value
    gateway.refund_query.side_effect = None
    gateway.refund_query.return_value = RefundChannelResult(**note)
    with pytest.raises(ValueError, match="refund query mismatch"):
        await _request(funds)
    async with sessions() as db:
        records = list(await db.scalars(select(RefundRecord)))
        assert len(records) == 1
        assert records[0].verified_status is None
    gateway.refund.assert_awaited_once()


async def test_explicit_hook_with_injected_factory_works_without_runtime_configuration(funds):
    sessions, order, gateway = funds
    hook = AsyncMock()
    gateway.refund.side_effect = PaymentChannelError("synthetic timeout")
    await _request(funds, result_hook=hook)
    await _expire_lease(sessions)
    gateway.refund_query.side_effect = None
    gateway.refund_query.return_value = _result(order)
    result = await _request(funds, result_hook=hook)
    assert result.verified_status == "SUCCESS"
    hook.assert_awaited_once()
