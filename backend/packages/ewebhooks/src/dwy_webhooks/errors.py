"""沿用 EAPI 异常基础，只传递安全错误码与调度建议。"""

from dwyeapi.exceptions import AppError


class WebhookDeliveryError(AppError):
    """发送失败；是否重试及如何持久化由调用方决定。"""

    def __init__(self, code: str, *, retry_after: float | None = None, permanent: bool = False):
        """retry_after 为有限非负秒数；生产发送器只使用固定错误码。"""
        self.code, self.retry_after, self.permanent = code, retry_after, permanent
        super().__init__(code, code=code)


class WebhookVerificationError(AppError):
    """提供方验签失败的安全结果；原始 JWS 与 SDK 异常不得向外传播。"""

    def __init__(self, code: str = "signature_invalid", *, status_code: int = 401):
        """status_code 区分无效签名与可重试的验证服务暂时不可用。"""
        self.code, self.status_code = code, status_code
        super().__init__(code, code=code)
