"""支付渠道与支付成功钩子。

渠道实现只出现在 gateways/。钩子由装配层实现,支付包不认识套餐或退款申请。
"""

from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from dwy_payment.errors import PaymentChannelError, PaymentNotConfiguredError, PaymentVerifyError


class ChannelNotify:
    """验签解密后的渠道通知。金额以分计,订单号是商户订单号。"""

    def __init__(
        self,
        *,
        order_no: str,
        amount_fen: int,
        trade_state: str,
        trade_type: str,
        event_type: str,
        transaction_id: str,
        raw: str,
    ) -> None:
        """保存一条已验签的通知。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            amount_fen (int): 渠道报文里的金额,单位分。取值范围 ``[1, 100000000]``。示例:``9900``。
            trade_state (str): 微信交易状态。示例:``"SUCCESS"``。
            trade_type (str): 交易类型。Native 为 ``"NATIVE"``。示例:``"NATIVE"``。
            event_type (str): 通知事件。成功支付为 ``"TRANSACTION.SUCCESS"``。示例:``"TRANSACTION.SUCCESS"``。
            transaction_id (str): 微信支付订单号。长度 ``[1, 64]``。示例:``"4200000001"``。
            raw (str): 解密后的 resource JSON,仅落库审计,不回给前端。示例:``"{}"``。
        """
        self.order_no = order_no
        self.amount_fen = amount_fen
        self.trade_state = trade_state
        self.trade_type = trade_type
        self.event_type = event_type
        self.transaction_id = transaction_id
        self.raw = raw


class PaymentPaid:
    """支付成功后吐给项目的回对三元组:用户标识、金额、订单号。"""

    def __init__(self, *, user_id: str, amount_fen: int, order_no: str) -> None:
        """构造回对载荷。值来自支付流水落库行,不直接信任回调原文。

        Args:
            user_id (str): 下单时调用方传入的用户标识。长度 ``[1, 64]``。示例:``"1001"``。
            amount_fen (int): 下单金额,单位分。取值范围 ``[1, 100000000]``。示例:``9900``。
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        """
        self.user_id = user_id
        self.amount_fen = amount_fen
        self.order_no = order_no


class PaymentGateway(Protocol):
    """一个支付渠道。支付宝以后另写实现,不在微信文件里加分支。"""

    def is_configured(self) -> bool:
        """凭证是否够发起真实请求。"""
        ...

    async def create_native(
        self,
        *,
        order_no: str,
        description: str,
        amount_fen: int,
        time_expire: datetime,
    ) -> str:
        """Native 下单,返回 code_url。

        Raises:
            PaymentNotConfiguredError: 未配置。
            PaymentChannelError: 微信拒绝或应答无法解析。
        """
        ...

    async def query(self, order_no: str) -> ChannelNotify:
        """按商户订单号查单。未支付时 trade_state 不是 SUCCESS。"""
        ...

    async def close(self, order_no: str) -> None:
        """关闭未支付订单。"""
        ...

    async def refund(self, order_no: str, refund_no: str, refund_fen: int, total_fen: int) -> str | None:
        """按商户订单号退一笔。同一 refund_no 重试必须幂等。

        Raises:
            PaymentNotConfiguredError: 未配置。
            PaymentChannelError: 渠道拒绝。
        """
        ...

    async def parse_notify(self, headers: object, body: bytes) -> ChannelNotify:
        """验签并解密回调。失败必须抛 PaymentVerifyError,不能返回成功态。"""
        ...


class PaymentPaidHook(Protocol):
    """支付流水已标成功、尚未提交时调用。实现方用同一会话对账并发放业务权益。"""

    async def on_paid(self, paid: PaymentPaid, db: AsyncSession) -> None:
        """处理一笔已核对金额的成功支付。重复调用必须可重入。"""
        ...


class NoOpPaymentHook:
    """没有业务挂钩时使用。不发放任何权益。"""

    async def on_paid(self, paid: PaymentPaid, db: AsyncSession) -> None:
        """空实现。

        Args:
            paid (PaymentPaid): 回对三元组。示例:``user_id="1"``。
            db (AsyncSession): 当前回调会话。示例:请求级 ``get_db`` 会话。
        """
        return


__all__ = [
    "ChannelNotify",
    "NoOpPaymentHook",
    "PaymentChannelError",
    "PaymentGateway",
    "PaymentNotConfiguredError",
    "PaymentPaid",
    "PaymentPaidHook",
    "PaymentVerifyError",
]
