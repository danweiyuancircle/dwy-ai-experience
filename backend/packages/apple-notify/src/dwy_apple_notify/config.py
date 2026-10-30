"""外部注入的配置契约；不读取环境变量、dotenv 或任何项目设置。"""

from itertools import combinations
from typing import Annotated, Literal

from dwy_notify.integration import DiscordUsername, NotificationSettings, paths_overlap
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SecretStr,
    model_validator,
)

from .validation import validate_apple_app_name

EventType = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")]
AppKey = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
ASCAppID = Annotated[str, Field(min_length=1, max_length=20, pattern=r"^[0-9]+$")]
ScopedPath = Annotated[str, Field(max_length=256, pattern=r"^/(?:[A-Za-z0-9_-]+/)+\{app_id\}$")]


class WebhookSourceConfig(NotificationSettings):
    """来源可覆盖默认通知目标，并按事件类型筛选。"""

    discord_username: DiscordUsername | None = None
    # None 使用提供方适配器自己的已知事件集，避免配置与事件格式维护两份列表。
    events: frozenset[EventType] | None = Field(default=None, max_length=100)


class AppStoreConnectApp(BaseModel):
    """每个 App 的显示名称与独立 HMAC 密钥。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1, max_length=128)
    secret: SecretStr = Field(min_length=32, max_length=512, repr=False)


class AppStoreConnectAPIConfig(BaseModel):
    """只读查询版本详情的 ASC 账号凭据；与 Webhook HMAC 密钥分开配置。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    issuer_id: str = Field(min_length=36, max_length=36,
                           pattern=r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
    key_id: str = Field(min_length=10, max_length=10, pattern=r"^[A-Z0-9]{10}$")
    private_key: SecretStr = Field(min_length=1, max_length=16384, repr=False)


class AppStoreConnectWebhookConfig(WebhookSourceConfig):
    """ASC 审核/构建通知；App ID 与签名密钥固定由项目配置。"""

    apps: dict[ASCAppID, AppStoreConnectApp] = Field(min_length=1, max_length=100)
    api: AppStoreConnectAPIConfig | None = None
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


class AppleNotifyConfig(NotificationSettings):
    """由项目 Settings 显式组合；未配置来源不注册路由，不读取部署环境。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    app_store_connect: AppStoreConnectWebhookConfig | None = None
    apple_notifications: AppleNotificationsConfig | None = None

    @model_validator(mode="after")
    def unique_paths(self):
        """显式配置不同来源时，不能让相同路径静默遮蔽另一验签协议。"""
        paths = [source.path for source in
                 (self.app_store_connect, self.apple_notifications) if source is not None]
        if any(paths_overlap(left, right) for left, right in combinations(paths, 2)):
            raise ValueError("Webhook source paths must not overlap")
        return self
