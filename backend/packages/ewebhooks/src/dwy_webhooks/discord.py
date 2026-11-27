"""旧 Discord 入口的兼容层；唯一发送实现位于 dwy-notify。"""

from dwy_notify import Notifier

from .errors import WebhookDeliveryError
from .notifications import legacy_discord_config
from .validation import DEFAULT_DISCORD_USERNAME, validate_discord_username, validate_discord_webhook_url


class DiscordWebhookSender:
    """保留历史真实消息 ID 契约；新调用方直接使用 dwy-notify。"""

    def __init__(self, webhook_url: str, *, username: str = DEFAULT_DISCORD_USERNAME):
        """旧配置仍执行原边界校验，不能转成任意 HTTP 接收方。"""
        url = validate_discord_webhook_url(webhook_url)
        name = validate_discord_username(username)
        self.notifier = Notifier(legacy_discord_config(url, name))

    async def __call__(self, content: str, *, suppress_embeds: bool = False) -> str:
        """兼容旧签名；新发送策略统一禁用 mention 和链接预览。"""
        result = await self.notifier.send(content)
        delivery = result.deliveries[0]
        if not delivery.success:
            code = delivery.error_code or "delivery_error"
            code = "discord_" + code.removeprefix("notification_").removeprefix("discord_")
            if code == "discord_redirect_rejected":
                code = "discord_http_error"
            raise WebhookDeliveryError(code, retry_after=delivery.retry_after,
                                       permanent=delivery.permanent) from None
        message_id = delivery.message_id
        if (not isinstance(message_id, str) or not message_id.isascii()
                or not message_id.isdigit() or len(message_id) > 128):
            raise WebhookDeliveryError("discord_invalid_response")
        return message_id
