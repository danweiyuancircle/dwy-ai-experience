"""外部注入的配置契约；不读取环境变量、dotenv 或任何项目设置。"""

import base64
import binascii
from itertools import combinations
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from .validation import (
    DEFAULT_DISCORD_USERNAME,
    paths_overlap,
    validate_apple_app_name,
    validate_discord_username,
    validate_discord_webhook_url,
)


def _destination(value):
    """共享官方目标校验；空环境值关闭目标，错误不得回显凭据。"""
    if value is None or value == "":
        return None
    raw = value.get_secret_value() if isinstance(value, SecretStr) else value
    validate_discord_webhook_url(raw)
    return value


Destination = Annotated[SecretStr | None, BeforeValidator(_destination)]
DiscordUsername = Annotated[
    str, Field(min_length=1, max_length=80), BeforeValidator(validate_discord_username),
]
EventType = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")]
AppKey = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
ASCAppID = Annotated[str, Field(min_length=1, max_length=20, pattern=r"^[0-9]+$")]
LocalPath = Annotated[str, Field(max_length=256, pattern=r"^/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+$")]
ScopedPath = Annotated[str, Field(max_length=256, pattern=r"^/(?:[A-Za-z0-9_-]+/)+\{app_id\}$")]


class WebhookSourceConfig(BaseModel):
    """已实际重复的来源选项：可覆盖发送目标，并按事件类型筛选。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    discord_webhook_url: Destination = Field(default=None, max_length=2048, repr=False)
    discord_username: DiscordUsername | None = None
    # None 使用提供方适配器自己的已知事件集，避免配置与事件格式维护两份列表。
    events: frozenset[EventType] | None = Field(default=None, max_length=100)


class ResendWebhookConfig(WebhookSourceConfig):
    """Resend 原文签名配置，不需要发送邮件的 API Key。"""

    secret: SecretStr = Field(min_length=1, max_length=512, repr=False)
    name: str = Field(default="Resend", min_length=1, max_length=100)
    scope: AppKey = "resend"
    path: LocalPath = "/webhooks/resend"

    @field_validator("secret")
    @classmethod
    def valid_secret(cls, value: SecretStr) -> SecretStr:
        """验证 Svix 密钥编码，不接受格式错误后在请求阶段静默失败。"""
        raw = value.get_secret_value()
        try:
            if not raw.startswith("whsec_") or len(base64.b64decode(raw[6:], validate=True)) < 16:
                raise ValueError
        except (ValueError, binascii.Error):
            raise ValueError("Resend requires a valid signing secret") from None
        return value


class AppStoreConnectApp(BaseModel):
    """每个 App 的显示名称与独立 HMAC 密钥。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1, max_length=128)
    secret: SecretStr = Field(min_length=32, max_length=512, repr=False)


class AppStoreConnectWebhookConfig(WebhookSourceConfig):
    """ASC 审核/构建通知；App ID 与签名密钥固定由项目配置。"""

    apps: dict[ASCAppID, AppStoreConnectApp] = Field(min_length=1, max_length=100)
    path: ScopedPath = "/webhooks/app-store-connect/{app_id}"


class AppleNotificationApp(BaseModel):
    """Server Notifications V2 身份及证书；不需要 App Cloud 商品目录。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: Annotated[str, BeforeValidator(validate_apple_app_name)] = Field(
        default="Apple", min_length=1, max_length=100,
    )
    bundle_id: str = Field(min_length=1, max_length=255)
    environment: Literal["Production", "Sandbox"] = "Production"
    app_apple_id: int | None = Field(default=None, ge=1)
    root_certificates: tuple[bytes, ...] = Field(min_length=1, max_length=8, repr=False)
    enable_online_checks: bool = True
    verification_workers: int = Field(default=2, ge=1, le=8)

    @model_validator(mode="after")
    def production_identity(self):
        """生产环境必须同时校验 Apple App ID；不能退回 Sandbox 验证。"""
        if self.environment == "Production" and self.app_apple_id is None:
            raise ValueError("Production Apple notifications require app_apple_id")
        return self


class AppleNotificationsConfig(WebhookSourceConfig):
    """多个独立 App 的 Server Notifications 接入配置。"""

    apps: dict[AppKey, AppleNotificationApp] = Field(min_length=1, max_length=100)
    path: ScopedPath = "/webhooks/apple/{app_id}"


class WebhookConfig(BaseModel):
    """由项目 Settings 显式组合；未配置来源不注册路由，不读取部署环境。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    discord_webhook_url: Destination = Field(default=None, max_length=2048, repr=False)
    discord_username: DiscordUsername = DEFAULT_DISCORD_USERNAME
    resend: ResendWebhookConfig | None = None
    app_store_connect: AppStoreConnectWebhookConfig | None = None
    apple_notifications: AppleNotificationsConfig | None = None

    @model_validator(mode="after")
    def unique_paths(self):
        """显式配置不同来源时，不能让相同路径静默遮蔽另一验签协议。"""
        paths = [source.path for source in
                 (self.resend, self.app_store_connect, self.apple_notifications) if source is not None]
        if any(paths_overlap(left, right) for left, right in combinations(paths, 2)):
            raise ValueError("Webhook source paths must not overlap")
        return self
