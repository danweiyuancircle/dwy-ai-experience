"""宿主注入四个功能各自的通知目标；不读取环境或要求同时启用所有功能。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dwy_notify import NotificationConfig
from pydantic import SecretStr

from dwy_webhooks import WebhookConfig
from dwy_webhooks.config import AppleNotificationApp, AppleNotificationsConfig, ResendWebhookConfig

if TYPE_CHECKING:
    from dwy_webhooks.analytics import AppleAnalyticsConfig
    from dwy_webhooks.reviews import AppleReviewsConfig


def webhook_config(
    *, resend_secret: SecretStr, apple_apps: dict[str, AppleNotificationApp],
    discord_url: SecretStr, wecom_url: SecretStr,
) -> WebhookConfig:
    """Resend 发 Discord，Apple 内购发企业微信；宿主决定是否安装这些来源。"""
    return WebhookConfig(
        resend=ResendWebhookConfig(
            secret=resend_secret,
            notifications=NotificationConfig(targets={"mail": discord_url}),
        ),
        apple_notifications=AppleNotificationsConfig(
            apps=apple_apps,
            notifications=NotificationConfig(targets={"purchases": wecom_url}),
        ),
    )


def review_config(
    *, apps: dict[str, dict[str, str]], issuer_id: str, key_id: str, private_key: SecretStr,
    discord_url: SecretStr,
) -> AppleReviewsConfig:
    """评论只发 Discord；可单独传给 install_review_monitor。"""
    from dwy_webhooks.reviews import AppleReviewsConfig

    return AppleReviewsConfig(
        apps=apps, issuer_id=issuer_id, key_id=key_id, private_key=private_key,
        notifications=NotificationConfig(targets={"reviews": discord_url}),
    )


def analytics_config(
    *, apps: dict[str, dict[str, str]], issuer_id: str, key_id: str, private_key: SecretStr,
    discord_url: SecretStr, wecom_url: SecretStr,
) -> AppleAnalyticsConfig:
    """日报同时发两个目标；可单独传给 install_analytics_monitor。"""
    from dwy_webhooks.analytics import AppleAnalyticsConfig

    return AppleAnalyticsConfig(
        apps=apps, issuer_id=issuer_id, key_id=key_id, private_key=private_key,
        notifications=NotificationConfig(targets={"daily": discord_url, "operations": wecom_url}),
    )
