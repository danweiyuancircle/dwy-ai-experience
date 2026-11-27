"""Apple 验签边界只传播安全错误码，不携带原始签名与 SDK 异常。"""

from dwyeapi.exceptions import AppError


class WebhookVerificationError(AppError):
    """status_code 区分无效签名与可重试的验证服务不可用。"""

    def __init__(self, code: str = "signature_invalid", *, status_code: int = 401):
        self.code, self.status_code = code, status_code
        super().__init__(code, code=code)
