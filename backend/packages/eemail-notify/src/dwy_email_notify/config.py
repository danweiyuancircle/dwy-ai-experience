"""宿主显式注入的邮件事件配置，不读取环境或调用业务发信能力。"""

import base64
import binascii
from typing import Annotated

from dwy_notify.integration import DiscordUsername, NotificationSettings
from pydantic import Field, SecretStr, field_validator

EventType = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")]
AppKey = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
LocalPath = Annotated[str, Field(max_length=256, pattern=r"^/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+$")]


class ResendWebhookConfig(NotificationSettings):
    """Resend 原文签名与事件筛选；只需要 signing secret，不需要发信 API key。"""

    secret: SecretStr = Field(min_length=1, max_length=512, repr=False)
    name: str = Field(default="Resend", min_length=1, max_length=100)
    scope: AppKey = "resend"
    path: LocalPath = "/webhooks/resend"
    discord_username: DiscordUsername | None = None
    events: frozenset[EventType] | None = Field(default=None, max_length=100)

    @field_validator("secret")
    @classmethod
    def valid_secret(cls, value: SecretStr) -> SecretStr:
        """配置边界拒绝无效 Svix 密钥，避免接收请求后才发现验签无法工作。"""
        raw = value.get_secret_value()
        try:
            if not raw.startswith("whsec_") or len(base64.b64decode(raw[6:], validate=True)) < 16:
                raise ValueError
        except (ValueError, binascii.Error):
            raise ValueError("Resend requires a valid signing secret") from None
        return value


class EmailNotifyConfig(NotificationSettings):
    """组合邮件平台事件来源；未配置来源不注册路由或加载其 SDK。"""

    resend: ResendWebhookConfig | None = None
