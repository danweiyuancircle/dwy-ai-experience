"""邮件平台事件通知；供应商 SDK 仅在安装其事件路由时加载。"""

from .config import EmailNotifyConfig, ResendWebhookConfig
from .fastapi import EmailNotifyRuntime, install_email_notifications

__all__ = [
    "EmailNotifyConfig", "EmailNotifyRuntime", "ResendWebhookConfig", "install_email_notifications",
]
