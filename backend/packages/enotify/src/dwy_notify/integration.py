"""来源无关的目标选择与历史 Discord 配置兼容；不持有业务展示预设。"""

import re
from typing import Annotated
from urllib.parse import quote, urlsplit

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, SecretStr, model_validator

from .delivery import NotificationDeliveryError
from .models import NotificationConfig, NotificationDelivery
from .notifier import Notifier

# 旧配置生成 URL 的历史字节必须保持，避免升级后待发记录的目标指纹变化。
DEFAULT_DISCORD_USERNAME = "Apple 应用通知"


def _display_name(value: str, maximum: int, message: str) -> str:
    """两个已使用的展示名称共享空白和控制字符约束，保留各自长度与稳定错误。"""
    if (not isinstance(value, str) or not 1 <= len(value) <= maximum or not value.strip()
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        raise ValueError(message)
    return value


def validate_discord_username(value: str) -> str:
    """Discord 发送名称最多 80 字符，错误不回显输入。"""
    return _display_name(value, 80, "Invalid Discord username")


def paths_overlap(left: str, right: str) -> bool:
    """已校验路径仅有末尾 app_id 参数，静态与模板同形时必须拒绝。"""
    first, second = left.split("/"), right.split("/")
    return len(first) == len(second) and all(
        a == b or a == "{app_id}" or b == "{app_id}" for a, b in zip(first, second, strict=True)
    )


def validate_discord_webhook_url(value: str) -> str:
    """只接受官方 HTTPS 地址，不回显无效输入中的凭据。"""
    if not isinstance(value, str) or re.fullmatch(
        r"https://discord\.com/api/(?:v10/)?webhooks/[0-9]+/[A-Za-z0-9_-]+", value
    ) is None:
        raise ValueError("discord_webhook_url requires an official Discord HTTPS webhook URL")
    return value


def _destination(value):
    if value is None or value == "":
        return None
    raw = value.get_secret_value() if isinstance(value, SecretStr) else value
    validate_discord_webhook_url(raw)
    return value


Destination = Annotated[SecretStr | None, BeforeValidator(_destination)]
DiscordUsername = Annotated[
    str, Field(min_length=1, max_length=80), BeforeValidator(validate_discord_username),
]


class NotificationSettings(BaseModel):
    """功能独立选择通知目标；旧 Discord 字段仅用于配置迁移。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    notifications: NotificationConfig | None = None
    discord_webhook_url: Destination = Field(default=None, max_length=2048, repr=False)
    discord_username: DiscordUsername = DEFAULT_DISCORD_USERNAME

    @model_validator(mode="after")
    def exclusive_destinations(self):
        """同一层只能有一种配置，避免升级时意外双发。"""
        if self.notifications is not None and self.discord_webhook_url is not None:
            raise ValueError("Configure notifications or legacy Discord destination, not both")
        return self


def legacy_discord_config(url: str, username: str = DEFAULT_DISCORD_USERNAME) -> NotificationConfig:
    """把已校验的历史配置转成渠道描述符，不保留第二套发送器。"""
    webhook_id, token = urlsplit(url).path.rstrip("/").split("/")[-2:]
    return NotificationConfig(targets={
        "discord": f"discord://{quote(username, safe='')}@{webhook_id}/{token}",
    })


def configured_notifier(options: NotificationSettings,
                        default: NotificationSettings | None = None) -> Notifier | None:
    """来源层显式选择优先；只有未选择时才继承宿主的全局默认。"""
    if options.notifications is not None:
        return Notifier(options.notifications)
    if options.discord_webhook_url is not None:
        return Notifier(legacy_discord_config(
            options.discord_webhook_url.get_secret_value(),
            options.discord_username or DEFAULT_DISCORD_USERNAME,
        ), url_appearance_is_default=(
            "discord_username" not in options.model_fields_set or options.discord_username is None
        ))
    if default is None:
        return None
    if default.notifications is not None:
        return Notifier(default.notifications)
    if default.discord_webhook_url is not None:
        # 保留旧 URL 和指纹，仅调整隐式历史默认名的展示优先级。
        source_explicit = (
            "discord_username" in options.model_fields_set and options.discord_username is not None
        )
        default_explicit = "discord_username" in default.model_fields_set
        username = options.discord_username if source_explicit else default.discord_username
        return Notifier(
            legacy_discord_config(default.discord_webhook_url.get_secret_value(), username),
            url_appearance_is_default=not (source_explicit or default_explicit),
        )
    return None


def delivery_error(delivery: NotificationDelivery) -> NotificationDeliveryError:
    """仅传递通知包自己的安全字段，保留队列的限流和永久失败语义。"""
    return NotificationDeliveryError(delivery.error_code or "notification_delivery_error",
                                retry_after=delivery.retry_after, permanent=delivery.permanent)
