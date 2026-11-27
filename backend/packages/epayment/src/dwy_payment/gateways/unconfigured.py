"""未配置渠道。保证进程能启动,任何真实收单动作都失败。"""

from datetime import datetime

from dwy_payment.errors import PaymentNotConfiguredError
from dwy_payment.protocols import ChannelNotify


class UnconfiguredGateway:
    """凭证没配齐时的占位渠道。"""

    def is_configured(self) -> bool:
        """始终未配置。"""
        return False

    async def create_native(
        self,
        *,
        order_no: str,
        description: str,
        amount_fen: int,
        time_expire: datetime,
    ) -> str:
        """拒绝下单。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"abc123def456"``。
            description (str): 商品描述。长度 ``[1, 127]``。示例:``"基础版月付"``。
            amount_fen (int): 金额分。取值范围 ``[1, 100000000]``。示例:``9900``。
            time_expire (datetime): 支付截止时间。示例:上海墙钟。
        Raises:
            PaymentNotConfiguredError: 总是抛出。
        """
        raise PaymentNotConfiguredError

    async def query(self, order_no: str) -> ChannelNotify:
        """拒绝查单。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"abc123def456"``。
        Raises:
            PaymentNotConfiguredError: 总是抛出。
        """
        raise PaymentNotConfiguredError

    async def close(self, order_no: str) -> None:
        """拒绝关单。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"abc123def456"``。
        Raises:
            PaymentNotConfiguredError: 总是抛出。
        """
        raise PaymentNotConfiguredError

    async def refund(self, order_no: str, refund_no: str, refund_fen: int, total_fen: int) -> None:
        """拒绝退款。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"abc123def456"``。
            refund_no (str): 商户退款单号。长度 ``[1, 64]``。示例:``"Rabc123def456"``。
            refund_fen (int): 退款分。取值范围 ``[1, 100000000]``。示例:``9900``。
            total_fen (int): 原实付分。取值范围 ``[1, 100000000]``。示例:``9900``。
        Raises:
            PaymentNotConfiguredError: 总是抛出。
        """
        raise PaymentNotConfiguredError

    async def parse_notify(self, headers: object, body: bytes) -> ChannelNotify:
        """没有密钥就不能解密回调。

        Args:
            headers (object): 回调头。示例:``{"wechatpay-signature": "..."}``。
            body (bytes): 回调正文。长度 ``[0, 1048576]``。示例:``b"{}"``。
        Raises:
            PaymentNotConfiguredError: 总是抛出。
        """
        raise PaymentNotConfiguredError
