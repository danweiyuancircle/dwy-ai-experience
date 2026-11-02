"""支付渠道错误。

这些异常不出 HTTP。用户接口由调用方改写成业务错误;微信回调改写成 FAIL 应答。
"""


class PaymentNotConfiguredError(Exception):
    """凭证未配齐。进程可以启动,下单与回调解密都不能当成功。"""


class PaymentVerifyError(Exception):
    """回调验签或解密失败。调用方必须回微信失败,不能标支付成功。"""


class PaymentChannelError(Exception):
    """微信下单/查单/关单返回非成功。message 只进日志,不回给前端。"""

    def __init__(self, message: str) -> None:
        """记录渠道失败原因。

        Args:
            message (str): 日志用摘要,不含密钥。长度 ``[1, 500]``。示例:``"status=400"``。
        """
        super().__init__(message)


class RefundNotFoundError(PaymentChannelError):
    """已核验渠道明确返回退款单不存在；允许原号原参数恢复，不表示网络错误。"""
