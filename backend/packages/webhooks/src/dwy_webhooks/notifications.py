"""来源只处理配置选择；全部传输交给 dwy-notify。"""

from urllib.parse import quote, urlsplit

from dwy_notify import NotificationConfig, NotificationDelivery, Notifier

from .config import NotificationSettings
from .errors import WebhookDeliveryError
from .validation import DEFAULT_DISCORD_USERNAME


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
        ))
    if default is None:
        return None
    if default.notifications is not None:
        return Notifier(default.notifications)
    if default.discord_webhook_url is not None:
        username = (options.discord_username if options.discord_username is not None
                    else default.discord_username)
        return Notifier(legacy_discord_config(default.discord_webhook_url.get_secret_value(), username))
    return None


def delivery_error(delivery: NotificationDelivery) -> WebhookDeliveryError:
    """仅传递通知包自己的安全字段，保留队列的限流和永久失败语义。"""
    return WebhookDeliveryError(delivery.error_code or "notification_delivery_error",
                                retry_after=delivery.retry_after, permanent=delivery.permanent)
