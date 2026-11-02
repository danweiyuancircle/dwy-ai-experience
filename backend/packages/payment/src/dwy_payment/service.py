"""支付流水:下单、按用户查询、处理回调。

回调先对渠道金额和落库金额,一致才标成功并吐回 user_id、金额、订单号。
待支付的详情、列表和账单补查也会查渠道。查到 Native 已支付且金额、订单号一致,走同一套入账钩子。
"""

import re
import uuid

from dwyeapi import dt
from dwyeapi.exceptions import BusinessError, NotFoundError
from dwyeapi.logger import get_logger
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dwy_payment.config import PaymentConfig
from dwy_payment.constants import (
    AMOUNT_FEN_MAX,
    AMOUNT_FEN_MIN,
    CHANNEL_WECHAT,
    CHANNELS,
    DESCRIPTION_MAX_LEN,
    EVENT_QUERY,
    EVENT_TRANSACTION_SUCCESS,
    PENDING_PULL_LIMIT,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_REFUND,
    STATUS_SUCCESS,
    TRADE_STATE_SUCCESS,
    TRADE_TYPE_NATIVE,
    USER_ID_MAX_LEN,
)
from dwy_payment.errors import PaymentChannelError, PaymentNotConfiguredError, PaymentVerifyError
from dwy_payment.events import PaymentEventPayload, record_payment_event
from dwy_payment.models import PaymentOrder
from dwy_payment.protocols import ChannelNotify, PaymentGateway, PaymentPaid, PaymentPaidHook
from dwy_payment.schemas import PaymentEcho

logger = get_logger(__name__)

_USER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def new_order_no() -> str:
    """生成商户订单号。32 位十六进制,符合微信 6–32 字符集。

    Returns:
        str: 订单号。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
    """
    return uuid.uuid4().hex


class PaymentService:
    """渠道流水服务。不认识套餐;成功后的业务动作交给钩子。"""

    def __init__(
        self,
        db: AsyncSession,
        gateway: PaymentGateway,
        hook: PaymentPaidHook,
        config: PaymentConfig,
    ) -> None:
        """绑定本次请求的会话和进程级渠道。

        Args:
            db (AsyncSession): 请求级会话。示例:``Depends(get_db)``。
            gateway (PaymentGateway): 渠道。未配置时是空实现。
            hook (PaymentPaidHook): 成功钩子。示例:套餐发放。
            config (PaymentConfig): 支付配置。示例:``PaymentConfig()``。
        """
        self.db = db
        self.gateway = gateway
        self.hook = hook
        self.config = config

    async def create(
        self,
        *,
        user_id: str,
        amount_fen: int,
        description: str,
        channel: str = CHANNEL_WECHAT,
        idempotency_key: str | None = None,
    ) -> PaymentEcho:
        """创建一笔待支付流水并向下单渠道要二维码。

        成功时不提交。调用方在同一会话写入桥接行再提交,避免只有二维码没有项目单。
        渠道结果未知时保留待查并提交。独立新接入推荐create_payment先持久意图再触网。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``,字符集字母数字及 ``_-``。示例:``"1001"``。
            amount_fen (int): 金额分。取值范围 ``[1, 100000000]``。示例:``9900``。
            description (str): 商品描述。长度 ``[1, 127]``。示例:``"基础版月付"``。
            channel (str): 支付渠道。枚举 ``{"wechat", "alipay"}``,默认 ``"wechat"``。示例:``"alipay"``。
        Returns:
            PaymentEcho: 回对字段和 code_url。
        Raises:
            PaymentNotConfiguredError: 这条渠道未配置。不落流水。
            BusinessError: 入参不合法,或渠道下单失败(code ``PAYMENT_CHANNEL_ERROR``)。
        """
        order = await self._prepare(
            user_id=user_id, amount_fen=amount_fen, description=description,
            channel=channel, idempotency_key=idempotency_key,
        )
        if order.status == STATUS_PENDING and order.code_url is None:
            if order.expires_at is None or order.expires_at <= dt.now():
                raise BusinessError("支付截止已过期或原参数未知，请先核对关闭原单", "PAYMENT_EXPIRED")
            await self._place(order)
        return self._echo(order)

    async def _prepare(self, *, user_id, amount_fen, description, channel, idempotency_key) -> PaymentOrder:
        self._check_input(user_id, amount_fen, description)
        if channel not in CHANNELS:
            raise BusinessError("支付渠道不合法", "INVALID_PAYMENT")
        if idempotency_key is not None:
            if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", idempotency_key):
                raise BusinessError("支付幂等键不合法", "INVALID_PAYMENT")
            existing = await self.db.scalar(
                select(PaymentOrder).where(PaymentOrder.idempotency_key == idempotency_key)
            )
            if existing is not None:
                return self._existing_intent(existing, user_id, amount_fen, description, channel)
        await self._reject_pending_cap(user_id)
        if not self._gateway_for(channel).is_configured():
            raise PaymentNotConfiguredError
        order = PaymentOrder(
            user_id=user_id,
            order_no=new_order_no(),
            amount_fen=amount_fen,
            channel=channel,
            status=STATUS_PENDING,
            description=description,
            idempotency_key=idempotency_key,
            expires_at=dt.after(minutes=self.config.order_expire_minutes),
        )
        try:
            async with self.db.begin_nested():
                self.db.add(order)
                await self.db.flush()
        except IntegrityError:
            if idempotency_key is None:
                raise
            existing = await self.db.scalar(
                select(PaymentOrder).where(PaymentOrder.idempotency_key == idempotency_key)
            )
            if existing is None:
                raise
            return self._existing_intent(existing, user_id, amount_fen, description, channel)
        return order

    def _existing_intent(self, order, user_id, amount_fen, description, channel) -> PaymentOrder:
        if (order.user_id, order.amount_fen, order.description, order.channel) != (
            user_id, amount_fen, description, channel
        ):
            raise BusinessError("支付幂等键参数不一致", "PAYMENT_IDEMPOTENCY_CONFLICT")
        return order

    async def list_for_user(self, user_id: str, page: int, page_size: int) -> tuple[list[PaymentOrder], int]:
        """分页列出该用户未软删的流水,新的在前。

        本页里的待支付单会向渠道查一次。查到已支付才入账,避免关掉收银台后列表一直停在待支付。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            page (int): 页码。取值范围 ``[1, 10000]``。示例:``1``。
            page_size (int): 每页条数。枚举 ``{20, 50, 100}``。示例:``20``。
        Returns:
            tuple[list[PaymentOrder], int]: 当前页和总数。
        """
        rows, total = await self._list_page(user_id, page, page_size)
        if await self._refresh_pending(rows):
            rows, total = await self._list_page(user_id, page, page_size)
        return rows, total

    async def get_for_user(self, user_id: str, order_no: str) -> PaymentOrder:
        """取该用户的一笔流水。别人的订单号也当不存在。

        仍是待支付时向渠道查一次。收银台两秒轮询走这里,回调丢失时靠这次查单入账。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Returns:
            PaymentOrder: 流水行。查单成功后状态可能已是 success。
        Raises:
            NotFoundError: 不存在、已软删、或不是该用户的。
        """
        order = await self._find_owned(user_id, order_no)
        if order.status == STATUS_PENDING:
            await self._refresh_pending([order])
            order = await self._find_owned(user_id, order_no)
        return order

    async def pull_pending_for_user(self, user_id: str) -> None:
        """补查该用户最近的待支付单。账单页不打开支付详情时仍要能入账。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
        """
        stmt = (
            select(PaymentOrder)
            .where(
                PaymentOrder.user_id == user_id,
                PaymentOrder.is_deleted.is_(False),
                PaymentOrder.status == STATUS_PENDING,
            )
            .order_by(PaymentOrder.id.desc())
            .limit(PENDING_PULL_LIMIT)
        )
        rows = list((await self.db.scalars(stmt)).all())
        await self._refresh_pending(rows)

    async def refresh_recent_pending(self, limit: int = PENDING_PULL_LIMIT) -> None:
        """补查全库最近的待支付单。扫描任务用,不是某个用户的列表。

        Args:
            limit (int): 最多查几笔。取值范围 ``[1, 20]``,默认 ``20``。示例:``20``。
        """
        stmt = (
            select(PaymentOrder)
            .where(
                PaymentOrder.is_deleted.is_(False),
                PaymentOrder.status == STATUS_PENDING,
            )
            .order_by(PaymentOrder.id.desc())
            .limit(limit)
        )
        rows = list((await self.db.scalars(stmt)).all())
        await self._refresh_pending(rows)

    async def close_for_user(self, user_id: str, order_no: str) -> PaymentOrder:
        """关闭本人的待支付单。渠道关闭成功后才把本地状态标失败,不发放权益。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Returns:
            PaymentOrder: 状态已是 failed 的行。
        Raises:
            NotFoundError: 不存在或不是该用户的。
            BusinessError: 不是待支付。code ``PAYMENT_NOT_PENDING``。
            PaymentNotConfiguredError: 渠道未配置。
            PaymentChannelError: 渠道拒绝关单。
        """
        order = await self._find_owned(user_id, order_no)
        if order.status != STATUS_PENDING:
            raise BusinessError("只能关闭待支付订单", "PAYMENT_NOT_PENDING")
        gateway = self._gateway_for(order.channel)
        if not gateway.is_configured():
            raise PaymentNotConfiguredError
        await gateway.close(order.order_no)
        # 渠道关闭与成功回调可能并行；不能覆盖另一事务已确认的收款。
        await self.db.execute(
            update(PaymentOrder)
            .where(PaymentOrder.id == order.id, PaymentOrder.status == STATUS_PENDING)
            .values(status=STATUS_FAILED)
        )
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def mark_refunded(self, user_id: str, order_no: str, refunded_fen: int, refund_no: str) -> PaymentOrder:
        """把已支付流水标成已退。不提交,由计费编排和权益收回放在同一事务。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            refunded_fen (int): 本次已退分。取值范围 ``[1, 100000000]``。示例:``9580``。
            refund_no (str): 商户退款单号。长度 ``[1, 64]``。示例:``"Ra1b2c3d4e5f64789a0b1c2d3e4f5678"``。
        Returns:
            PaymentOrder: 已标成 refund 的行,尚未提交。
        Raises:
            NotFoundError: 不存在或不是该用户的。
            BusinessError: 不是已支付,或退款单号对不上已有退款。code ``PAYMENT_NOT_SUCCESS``。
        """
        order = await self._find_owned(user_id, order_no)
        if order.status == STATUS_REFUND and order.refund_no == refund_no:
            return order
        if order.status != STATUS_SUCCESS:
            raise BusinessError("只能退已支付的订单", "PAYMENT_NOT_SUCCESS")
        order.status = STATUS_REFUND
        order.refunded_fen = refunded_fen
        order.refund_no = refund_no
        await self.db.flush()
        return order

    async def _reject_pending_cap(self, user_id: str) -> None:
        """待支付笔数达到配置上限时拒绝再下单。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
        Raises:
            BusinessError: 未支付单已满。code ``TOO_MANY_PENDING_ORDERS``。
        """
        total = await self.db.scalar(
            select(func.count())
            .select_from(PaymentOrder)
            .where(
                PaymentOrder.user_id == user_id,
                PaymentOrder.status == STATUS_PENDING,
                PaymentOrder.is_deleted.is_(False),
            )
        )
        if int(total or 0) >= self.config.max_pending_orders:
            raise BusinessError("待支付订单过多", "TOO_MANY_PENDING_ORDERS")

    async def _list_page(self, user_id: str, page: int, page_size: int) -> tuple[list[PaymentOrder], int]:
        """读一页流水,不查渠道。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            page (int): 页码。取值范围 ``[1, 10000]``。示例:``1``。
            page_size (int): 每页条数。枚举 ``{20, 50, 100}``。示例:``20``。
        Returns:
            tuple[list[PaymentOrder], int]: 当前页和总数。
        """
        filters = (PaymentOrder.user_id == user_id, PaymentOrder.is_deleted.is_(False))
        total = await self.db.scalar(select(func.count()).select_from(PaymentOrder).where(*filters))
        stmt = (
            select(PaymentOrder)
            .where(*filters)
            .order_by(PaymentOrder.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = list((await self.db.scalars(stmt)).all())
        return rows, int(total or 0)

    async def _find_owned(self, user_id: str, order_no: str) -> PaymentOrder:
        """按用户和订单号取未软删流水。

        Args:
            user_id (str): 调用方用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Returns:
            PaymentOrder: 流水行。
        Raises:
            NotFoundError: 不存在、已软删、或不是该用户的。
        """
        stmt = select(PaymentOrder).where(
            PaymentOrder.order_no == order_no,
            PaymentOrder.user_id == user_id,
            PaymentOrder.is_deleted.is_(False),
        )
        order = (await self.db.execute(stmt)).scalar_one_or_none()
        if order is None:
            raise NotFoundError("支付订单")
        return order

    async def _refresh_pending(self, orders: list[PaymentOrder]) -> bool:
        """把待支付单拿去查渠道。先抄订单号,入账提交后不再读循环里的旧对象。

        Args:
            orders (list[PaymentOrder]): 刚从本会话读出的流水,可含非待支付。示例:当前页。
        Returns:
            bool: 至少有一笔在这次标成成功并提交。
        """
        order_nos = [order.order_no for order in orders if order.status == STATUS_PENDING]
        changed = False
        for order_no in order_nos:
            order = await self._find(order_no)
            if order is None or order.status != STATUS_PENDING:
                continue
            if await self._pull_one(order):
                changed = True
        return changed

    async def _pull_one(self, order: PaymentOrder) -> bool:
        """查一笔待支付。渠道失败或未支付保持原状态。

        Args:
            order (PaymentOrder): 状态仍是 pending 的行。
        Returns:
            bool: 已标成功并完成钩子提交。
        """
        gateway = self._gateway_for(order.channel)
        if not gateway.is_configured():
            return False
        try:
            parsed = await gateway.query(order.order_no)
        except (PaymentChannelError, PaymentNotConfiguredError, PaymentVerifyError):
            # 收银台两秒一轮。查单失败不能把详情打成 500,下一轮再试。
            logger.warning("payment query failed order_no=%s", order.order_no)
            return False
        if not self._channel_paid(order, parsed):
            return False
        if not await self._mark_success(order, parsed):
            return False
        return await self._emit_paid(order)

    def _channel_paid(self, order: PaymentOrder, parsed: ChannelNotify) -> bool:
        """Native 已支付,且金额、订单号与落库行一致。

        查单事件名是 QUERY,回调是 TRANSACTION.SUCCESS。其它事件不入账。

        Args:
            order (PaymentOrder): 本地待支付流水。
            parsed (ChannelNotify): 渠道查单或回调。示例:``trade_state="SUCCESS"``。
        Returns:
            bool: 可以走入账钩子。
        """
        if order.amount_fen != parsed.amount_fen or order.order_no != parsed.order_no:
            return False
        if parsed.trade_state != TRADE_STATE_SUCCESS or parsed.trade_type != TRADE_TYPE_NATIVE:
            return False
        return parsed.event_type in (EVENT_TRANSACTION_SUCCESS, EVENT_QUERY)

    async def list_orders(
        self,
        *,
        order_no: str | None,
        channel_trade_no: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PaymentOrder], int]:
        """按订单号或渠道单号精确列出未软删流水。都不传则最近的在前。

        两个条件都传时同时相等。一个搜索框要先试订单号、再试渠道单号时,由调用方分两次查。

        Args:
            order_no (str | None): 商户订单号。长度 ``[6, 32]``。不传则不按它过滤。示例:``"abc123def456"``。
            channel_trade_no (str | None): 渠道交易号。长度 ``[1, 64]``。不传则不按它过滤。示例:``"4200000001"``。
            page (int): 页码。取值范围 ``[1, 10000]``。示例:``1``。
            page_size (int): 每页条数。枚举 ``{20, 50, 100}``。示例:``20``。
        Returns:
            tuple[list[PaymentOrder], int]: 当前页和总数。
        """
        filters = [PaymentOrder.is_deleted.is_(False)]
        if order_no is not None:
            filters.append(PaymentOrder.order_no == order_no)
        if channel_trade_no is not None:
            filters.append(PaymentOrder.channel_trade_no == channel_trade_no)
        total = await self.db.scalar(select(func.count()).select_from(PaymentOrder).where(*filters))
        stmt = (
            select(PaymentOrder)
            .where(*filters)
            .order_by(PaymentOrder.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = list((await self.db.scalars(stmt)).all())
        return rows, int(total or 0)

    async def handle_notify(self, headers: object, body: bytes, *, channel: str = CHANNEL_WECHAT) -> bool:
        """处理渠道回调。返回 True 时路由回空 200;False 回 FAIL。

        已成功的同一订单号直接应答成功,不再调用钩子。

        Args:
            headers (object): 回调头。示例:微信 ``Wechatpay-Signature``。
            body (bytes): 原始正文。长度受配置 ``max_notify_bytes`` 限制。示例:``b"{}"``。
            channel (str): 这条回调属于哪条渠道。枚举 ``{"wechat", "alipay"}``,默认 ``"wechat"``。示例:``"alipay"``。
        Returns:
            bool: True 表示可以应答成功。
        """
        parsed = await self._parse(headers, body, channel)
        if parsed is None:
            return False
        order = await self._find(parsed.order_no)
        if not self._matches(order, parsed) or (order is not None and order.channel != channel):
            return False
        if order is None:
            return False
        if order.status in (STATUS_SUCCESS, STATUS_REFUND):
            return True
        if not await self._mark_success(order, parsed):
            fresh = await self._find(parsed.order_no)
            return fresh is not None and fresh.status in (STATUS_SUCCESS, STATUS_REFUND)
        return await self._emit_paid(order)

    async def _place(self, order: PaymentOrder) -> None:
        """用原下单快照获取code_url；未知结果保留原号并提交，不能生成第二笔支付。

        Args:
            order (PaymentOrder): 已 flush 的待支付行。
        Raises:
            BusinessError: 渠道失败。code ``PAYMENT_CHANNEL_ERROR``。
        """
        try:
            order.code_url = await self._gateway_for(order.channel).create_native(
                order_no=order.order_no,
                description=order.description,
                amount_fen=order.amount_fen,
                time_expire=order.expires_at,
            )
        except PaymentChannelError:
            logger.warning("payment create channel failed order_no=%s", order.order_no)
            # 网络错误可能发生在渠道已受理之后，保留原号供回调和查单核对。
            await self.db.commit()
            raise BusinessError("支付下单失败", "PAYMENT_CHANNEL_ERROR") from None

    async def refund_remote(self, order: PaymentOrder, refund_no: str, refund_fen: int, total_fen: int) -> str | None:
        """向这笔流水自己的渠道退款。

        Args:
            order (PaymentOrder): 已支付流水。示例:``channel="alipay"``。
            refund_no (str): 商户退款单号。长度 ``[1, 64]``。示例:``"Ra1b2c3d4e5f64789a0b1c2d3e4f5678"``。
            refund_fen (int): 本次退款分。取值范围 ``[1, 100000000]``。示例:``9900``。
            total_fen (int): 原实付分。取值范围 ``[1, 100000000]``。示例:``9900``。
        Raises:
            PaymentNotConfiguredError: 这条渠道未配置。
            PaymentChannelError: 渠道拒绝。
        """
        gateway = self._gateway_for(order.channel)
        if not gateway.is_configured():
            raise PaymentNotConfiguredError
        return await gateway.refund(order.order_no, refund_no, refund_fen, total_fen)

    def _gateway_for(self, channel: str) -> PaymentGateway:
        """双渠道表按名字取。测试注入的单网关没有 require,所有渠道都走它。

        Args:
            channel (str): 渠道名。枚举 ``{"wechat", "alipay"}``。示例:``"alipay"``。
        Returns:
            PaymentGateway: 该渠道实现。
        """
        require = getattr(self.gateway, "require", None)
        if callable(require):
            return require(channel)
        return self.gateway

    async def _parse(self, headers: object, body: bytes, channel: str) -> ChannelNotify | None:
        """验签解密。失败返回 None,由路由应答失败。

        Args:
            headers (object): 回调头。
            body (bytes): 正文。
            channel (str): 渠道名。枚举 ``{"wechat", "alipay"}``。示例:``"wechat"``。
        Returns:
            ChannelNotify | None: 解密结果;验签失败或未配置时为 None。
        """
        try:
            return await self._gateway_for(channel).parse_notify(headers, body)
        except (PaymentVerifyError, PaymentNotConfiguredError):
            return None

    async def _find(self, order_no: str) -> PaymentOrder | None:
        """按订单号找未软删流水。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"abc123def456abc123def456abc12345"``。
        Returns:
            PaymentOrder | None: 找到的行。
        """
        stmt = select(PaymentOrder).where(
            PaymentOrder.order_no == order_no,
            PaymentOrder.is_deleted.is_(False),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    def _matches(self, order: PaymentOrder | None, parsed: ChannelNotify) -> bool:
        """渠道报文必须是 Native 成功,且金额、订单号与落库行一致。

        Args:
            order (PaymentOrder | None): 落库行。不存在时为 None。
            parsed (ChannelNotify): 已解密通知。
        Returns:
            bool: 可以继续标成功或作重复通知。
        """
        if order is None or order.amount_fen != parsed.amount_fen or order.order_no != parsed.order_no:
            return False
        if order.channel_trade_no is not None and order.channel_trade_no != parsed.transaction_id:
            return False
        if parsed.event_type != EVENT_TRANSACTION_SUCCESS or parsed.trade_state != TRADE_STATE_SUCCESS:
            return False
        if parsed.trade_type != TRADE_TYPE_NATIVE:
            return False
        return order.status in (STATUS_PENDING, STATUS_SUCCESS, STATUS_REFUND)

    async def _mark_success(self, order: PaymentOrder, parsed: ChannelNotify) -> bool:
        """仅当仍是 pending 时改成 success。并发回调只有一笔能改成功。

        Args:
            order (PaymentOrder): 待支付行。
            parsed (ChannelNotify): 已对上金额的通知。
        Returns:
            bool: 本请求抢到了状态迁移。
        """
        stmt = (
            update(PaymentOrder)
            .where(
                PaymentOrder.id == order.id,
                PaymentOrder.status == STATUS_PENDING,
                PaymentOrder.amount_fen == parsed.amount_fen,
            )
            .values(
                status=STATUS_SUCCESS,
                channel_trade_no=parsed.transaction_id,
                notify_payload=parsed.raw,
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        return result.rowcount == 1

    async def _emit_paid(self, order: PaymentOrder) -> bool:
        """把落库的三元组交给钩子。钩子异常则回滚,让渠道重试。

        Args:
            order (PaymentOrder): 刚标成功、尚未提交的行。
        Returns:
            bool: 钩子完成则为 True。
        """
        paid = PaymentPaid(user_id=order.user_id, amount_fen=order.amount_fen, order_no=order.order_no)
        try:
            await record_payment_event(self.db, PaymentEventPayload(
                event_type="PAYMENT.SUCCESS", order_no=order.order_no, channel=order.channel,
                transaction_id=order.channel_trade_no, amount_fen=order.amount_fen,
                idempotency_key=order.idempotency_key,
            ))
            await self.hook.on_paid(paid, self.db)
        except Exception:
            # 回调必须回微信的 FAIL 正文,不能把内部异常原样抛出去。事务回滚后渠道会重试。
            logger.exception("payment paid hook failed order_no=%s", order.order_no)
            await self.db.rollback()
            return False
        if self.db.in_transaction():
            await self.db.commit()
        return True

    def _check_input(self, user_id: str, amount_fen: int, description: str) -> None:
        """拦住空标识、超额金额和空描述。调用方是项目代码,仍按外边界校验。

        Args:
            user_id (str): 用户标识。
            amount_fen (int): 金额分。
            description (str): 商品描述。
        Raises:
            BusinessError: 任一字段不合法。code ``INVALID_PAYMENT``。
        """
        if not _USER_ID_RE.fullmatch(user_id) or len(user_id) > USER_ID_MAX_LEN:
            raise BusinessError("用户标识不合法", "INVALID_PAYMENT")
        if type(amount_fen) is not int or amount_fen < AMOUNT_FEN_MIN or amount_fen > AMOUNT_FEN_MAX:
            raise BusinessError("支付金额不合法", "INVALID_PAYMENT")
        if not description.strip() or len(description) > DESCRIPTION_MAX_LEN:
            raise BusinessError("商品描述不合法", "INVALID_PAYMENT")

    def _echo(self, order: PaymentOrder) -> PaymentEcho:
        """从流水行组装回对结果。

        Args:
            order (PaymentOrder): 已写上 code_url 的行。
        Returns:
            PaymentEcho: 吐给调用方的字段。
        """
        return PaymentEcho(
            user_id=order.user_id,
            amount_fen=order.amount_fen,
            order_no=order.order_no,
            code_url=order.code_url,
            status=order.status,
            channel=order.channel,
        )
