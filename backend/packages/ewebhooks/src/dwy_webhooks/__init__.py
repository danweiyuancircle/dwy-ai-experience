"""基于 EAPI 的 Webhook 集成；配置由项目注入，平台 SDK 按需加载。"""

from .config import WebhookConfig
from .errors import WebhookDeliveryError
from .events import WebhookEvent
from .fastapi import WebhookRuntime, WebhookSinks, install_webhooks
from .validation import validate_discord_webhook_url

__all__ = [
    "DiscordWebhookSender", "WebhookConfig", "WebhookDeliveryError", "WebhookEvent",
    "WebhookRuntime", "WebhookSinks", "install_webhooks", "validate_discord_webhook_url",
]


def __getattr__(name: str):
    """核心导入不强制安装 Discord SDK；只有使用发送能力才加载该 extra。"""
    if name == "DiscordWebhookSender":
        from .discord import DiscordWebhookSender

        return DiscordWebhookSender
    raise AttributeError(name)
