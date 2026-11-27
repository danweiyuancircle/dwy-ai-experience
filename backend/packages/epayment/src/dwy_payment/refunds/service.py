"""独立持久退款意图、统一回调/查询结果及有界补查；不修改宿主权益。"""

import hashlib
import re
from datetime import timedelta

from dwy_wechatpay_notify import ConfirmedWechatPayResult
from dwyeapi import dt
from dwyeapi.logger import get_logger
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dwy_payment.constants import AMOUNT_FEN_MAX, ORDER_NO_RE
from dwy_payment.errors import PaymentChannelError, PaymentNotConfiguredError, PaymentVerifyError
from dwy_payment.events import PaymentEventPayload, record_payment_event
from dwy_payment.models import PaymentOrder
from dwy_payment.refunds.models import RefundRecord
from dwy_payment.refunds.protocols import RefundChannelResult, RefundManualReviewHook, RefundResultHook

logger = get_logger(__name__)
_FINAL = frozenset({"SUCCESS", "ABNORMAL", "CLOSED"})


async def _lock_refund_budget(db: AsyncSession, order_no: str) -> None:
    """只串行化本库的同支付退款意图，不锁父支付行；SQLite 测试使用写事务。"""
    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        key = int.from_bytes(hashlib.sha256(("dwy-payment-refund:" + order_no).encode()).digest()[:8], signed=True)
        await db.execute(select(func.pg_advisory_xact_lock(key)))
        return
    if dialect == "sqlite":
        await db.execute(text("BEGIN IMMEDIATE"))
        return
    raise RuntimeError("refund budget requires PostgreSQL or SQLite")


async def persist_refund_intent(
    *,
    order: PaymentOrder,
    refund_no: str,
    refund_fen: int,
    session_factory=None,
) -> tuple[RefundRecord, bool]:
    """独立提交并预留原支付金额，返回(记录,是否新建)；同号参数必须一致。

    不提交父业务事务、不锁父支付行；SQLite 的数据库级写锁不能用于嵌套持写锁的父会话。
    父支付钩子尚未提交交易号时仅保存可信快照，真实退款命令另查已持久支付并核对渠道。
    """
    from dwy_payment.runtime import get_refund_session_factory

    if (order.channel != "wechat" or not order.channel_trade_no
            or type(order.amount_fen) is not int or not 0 < order.amount_fen <= AMOUNT_FEN_MAX
            or type(refund_fen) is not int or not 0 < refund_fen <= order.amount_fen
            or not isinstance(order.order_no, str) or not ORDER_NO_RE.fullmatch(order.order_no)):
        raise ValueError("invalid refund intent")
    if not isinstance(refund_no, str) or not re.fullmatch(r"[0-9A-Za-z_|\-*@]{1,64}", refund_no):
        raise ValueError("invalid refund number")
    factory = get_refund_session_factory() if session_factory is None else session_factory
    async with factory() as db:
        await _lock_refund_budget(db, order.order_no)
        persisted = await db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == order.order_no))
        if (persisted is None or persisted.channel != order.channel or persisted.amount_fen != order.amount_fen
                or persisted.is_deleted or (persisted.channel_trade_no is not None
                                           and persisted.channel_trade_no != order.channel_trade_no)):
            raise ValueError("refund payment mismatch")
        try:
            async with db.begin_nested():
                record = await db.scalar(select(RefundRecord).where(RefundRecord.refund_no == refund_no))
                if record is None:
                    legacy_refunded = max(persisted.refunded_fen, order.refunded_fen)
                    if legacy_refunded:
                        marker = await db.scalar(select(RefundRecord).where(
                            RefundRecord.order_no == order.order_no, RefundRecord.refund_no == persisted.refund_no,
                        ))
                        successful = await db.scalar(select(func.coalesce(func.sum(RefundRecord.refund_fen), 0)).where(
                            RefundRecord.order_no == order.order_no, RefundRecord.verified_status == "SUCCESS",
                        ))
                        if (marker is None or not (marker.refund_fen == legacy_refunded
                                or (marker.verified_status == "SUCCESS" and successful == legacy_refunded))):
                            raise ValueError("legacy refund amount requires reconciliation")
                    committed = await db.scalar(select(func.coalesce(func.sum(RefundRecord.refund_fen), 0)).where(
                        RefundRecord.order_no == order.order_no,
                        (RefundRecord.verified_status.is_(None)) | (RefundRecord.verified_status != "CLOSED"),
                    ))
                    reserved = max(committed, legacy_refunded)
                    if reserved + refund_fen > order.amount_fen:
                        raise ValueError("refund amount exceeds original payment")
                    record = RefundRecord(
                        order_no=order.order_no,
                        refund_no=refund_no,
                        transaction_id=order.channel_trade_no,
                        amount_fen=order.amount_fen,
                        refund_fen=refund_fen,
                        source="app",
                    )
                    db.add(record)
                    await db.flush()
                    created = True
                else:
                    created = False
        except IntegrityError:
            # 两个父事务同时准备同号时只保留首个意图，不让第二个再次申请。
            record = await db.scalar(select(RefundRecord).where(RefundRecord.refund_no == refund_no))
            if record is None:
                raise
            created = False
        if (record.order_no, record.transaction_id, record.amount_fen, record.refund_fen) != (
            order.order_no,
            order.channel_trade_no,
            order.amount_fen,
            refund_fen,
        ):
            raise ValueError("refund intent mismatch")
        await db.commit()
        await db.refresh(record)
        db.expunge(record)
        return record, created


class RefundResultService:
    """结果服务不提交事务；宿主必须将此处更新与sink写入一起commit或rollback。"""

    def __init__(self, db: AsyncSession, *, result_hook: RefundResultHook | None = None) -> None:
        """绑定结果会话；hook只能使用同session登记通知，不能直接访问app模块。"""
        from dwy_payment.runtime import get_refund_result_hook

        self.db = db
        self.hook = get_refund_result_hook() if result_hook is None else result_hook

    async def apply(self, result: RefundChannelResult, *, queried: bool) -> bool:
        """完整回对后原子写入结果；外部退款回调先观察，queried=True才发最终通知。

        原订单属于其他应用时确认接收，仅记录安全诊断；错金额等本项目冲突抛ValueError。
        SUCCESS/CLOSED为官方终态，ABNORMAL仍可由后续查询或回调推进至SUCCESS。
        """
        if result.refund_status not in _FINAL | {"PROCESSING"} or result.currency != "CNY":
            raise ValueError("invalid refund result")
        order = await self.db.scalar(select(PaymentOrder).where(PaymentOrder.order_no == result.order_no))
        if order is None or order.channel != "wechat":
            logger.info("wechat refund ignored reason=foreign_order")
            return True
        if order.amount_fen != result.amount_fen or not 0 < result.refund_fen <= result.amount_fen:
            raise ValueError("refund original amount mismatch")
        record = await self.db.scalar(
            select(RefundRecord)
            .where(RefundRecord.refund_no == result.refund_no)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            if order.channel_trade_no != result.transaction_id:
                raise ValueError("refund transaction mismatch")
            # 保存点只处理同号插入竞争，不影响调用方已有事务。
            try:
                async with self.db.begin_nested():
                    record = RefundRecord(
                        order_no=result.order_no,
                        refund_no=result.refund_no,
                        transaction_id=result.transaction_id,
                        amount_fen=result.amount_fen,
                        refund_fen=result.refund_fen,
                        source="external",
                    )
                    self.db.add(record)
                    await self.db.flush()
            except IntegrityError:
                record = await self.db.scalar(
                    select(RefundRecord)
                    .where(RefundRecord.refund_no == result.refund_no)
                    .with_for_update()
                    .execution_options(populate_existing=True)
                )
                if record is None:
                    raise
        if (record.order_no, record.transaction_id, record.amount_fen, record.refund_fen) != (
            result.order_no,
            result.transaction_id,
            result.amount_fen,
            result.refund_fen,
        ) or (order.channel_trade_no is not None and order.channel_trade_no != result.transaction_id):
            raise ValueError("refund request mismatch")
        if record.provider_refund_id is not None and record.provider_refund_id != result.refund_id:
            raise ValueError("refund provider id mismatch")
        if record.verified_status in {"SUCCESS", "CLOSED"}:
            return True
        observed = record.source == "external" and not queried
        if not observed and record.verified_status == result.refund_status:
            return True
        now = dt.now()
        values = {
            "provider_refund_id": result.refund_id,
            "provider_status": result.refund_status,
            "version": record.version + 1,
            "next_query_at": max(now, record.last_query_at + timedelta(seconds=60))
            if observed and record.last_query_at is not None
            else now
            if observed
            else now + timedelta(seconds=60),
        }
        if not observed and result.refund_status in _FINAL:
            values["verified_status"] = result.refund_status
            if result.refund_status in {"SUCCESS", "CLOSED"}:
                values["next_query_at"] = None
        updated = await self.db.execute(
            update(RefundRecord)
            .where(RefundRecord.id == record.id, RefundRecord.version == record.version)
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        if updated.rowcount != 1:
            # SQLite没有行锁；CAS失败后重读状态，同号竞争不能重复登记通知。
            return await self.apply(result, queried=queried)
        await self.db.refresh(record)
        if not observed and result.refund_status in _FINAL:
            confirmed = ConfirmedWechatPayResult(
                event_type=f"REFUND.{result.refund_status}",
                provider_event_id=result.provider_event_id,
                order_no=result.order_no,
                transaction_id=result.transaction_id,
                amount_fen=result.amount_fen,
                refund_no=result.refund_no,
                refund_id=result.refund_id,
                refund_fen=result.refund_fen,
                refund_status=result.refund_status,
                occurred_at=result.occurred_at,
            )
            await record_payment_event(self.db, PaymentEventPayload(
                event_type=confirmed.event_type, order_no=record.order_no, channel="wechat",
                transaction_id=record.transaction_id, amount_fen=record.amount_fen,
                refund_no=record.refund_no, refund_fen=record.refund_fen, version=record.version,
                idempotency_key=order.idempotency_key,
            ))
            await self.hook(confirmed, self.db)
        return True


async def reconcile_refunds(
    *, session_factory=None, gateway=None, limit: int = 20,
    result_hook: RefundResultHook | None = None, manual_review_hook: RefundManualReviewHook | None = None,
) -> list[RefundRecord]:
    """每分钟调度一次，最多20笔、单笔至少60秒；返回首次超24小时人工告警记录。

    先提交查询租约再调用网络，进程中断也不能立刻重查。永不重新调用渠道refund。
    """
    from dwy_payment.runtime import get_gateway, get_refund_manual_review_hook, get_refund_session_factory

    factory = get_refund_session_factory() if session_factory is None else session_factory
    current_gateway = get_gateway() if gateway is None else gateway
    manual_hook = get_refund_manual_review_hook() if manual_review_hook is None else manual_review_hook
    require = getattr(current_gateway, "require", None)
    if callable(require):
        current_gateway = require("wechat")
    manual = []
    async with factory() as db:
        if db.bind.dialect.name == "postgresql":
            # 多worker先串行分配整分钟查询预算，锁在网络调用前随租约提交释放。
            await db.execute(select(func.pg_advisory_xact_lock(0x647779726566756E)))
        now = dt.now()
        recent = await db.scalar(
            select(func.count())
            .select_from(RefundRecord)
            .where(
                RefundRecord.last_query_at > now - timedelta(seconds=60),
            )
        )
        allowance = min(max(limit, 0), 20 - recent)
        if allowance <= 0:
            return []
        rows = list(
            (
                await db.scalars(
                    select(RefundRecord)
                    .where(RefundRecord.next_query_at <= now)
                    .order_by(RefundRecord.next_query_at, RefundRecord.id)
                    .limit(allowance)
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        tasks = []
        for record in rows:
            if record.created_at <= now - timedelta(hours=24) and not record.manual_required:
                await manual_hook(db, refund_no=record.refund_no, order_no=record.order_no)
                record.manual_required = True
                manual.append(record)
            record.last_query_at = now
            record.next_query_at = now + timedelta(seconds=60)
            tasks.append((record.id, record.refund_no))
        await db.commit()
        for record in manual:
            await db.refresh(record)
            db.expunge(record)
    for record_id, refund_no in tasks:
        try:
            result = await current_gateway.refund_query(refund_no)
            async with factory() as db:
                await RefundResultService(db, result_hook=result_hook).apply(result, queried=True)
                await db.commit()
        except (PaymentChannelError, PaymentNotConfiguredError, PaymentVerifyError, ValueError):
            logger.warning("wechat refund reconciliation failed record_id=%s", record_id)
    return manual
