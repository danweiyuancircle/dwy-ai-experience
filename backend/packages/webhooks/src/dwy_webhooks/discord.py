"""Discord 单次传输；消息内容、验签和重试账本不属于传输层。"""

import logging
import re
from contextlib import asynccontextmanager
from math import isfinite

import httpx
from discord_webhook import AsyncDiscordWebhook

from .errors import WebhookDeliveryError
from .validation import DEFAULT_DISCORD_USERNAME, validate_discord_username, validate_discord_webhook_url


class _WebhookCredentialsFilter(logging.Filter):
    """渲染后移除 token，正常 HTTP 请求日志继续保留。"""

    def filter(self, record: logging.LogRecord) -> bool:
        """修改已渲染消息并清空 args，避免日志格式化再次插入原始 token。"""
        message = record.getMessage()
        redacted = re.sub(
            r"(https://discord\.com/api/(?:v10/)?webhooks/[0-9]+/)[A-Za-z0-9_-]+",
            r"\1[REDACTED]", message,
        )
        if redacted != message:
            record.msg, record.args = redacted, ()
        return True


# 常驻安装，避免并发请求在临时添加/移除过滤器时出现脱敏空窗。
logging.getLogger("httpx").addFilter(_WebhookCredentialsFilter())


def discord_client() -> httpx.AsyncClient:
    """每次请求使用有界客户端，取消和异常时由上下文负责关闭。"""
    return httpx.AsyncClient(
        timeout=10, follow_redirects=False, headers={"User-Agent": "dwy-webhooks/0.4.0"}
    )


class _DiscordWebhook(AsyncDiscordWebhook):
    """复用成熟 SDK 的载荷和查询参数，只替换受控客户端。"""

    @property
    @asynccontextmanager
    async def http_client(self):
        """禁止跟随重定向，防止将凭据发送到另一地址。"""
        async with discord_client() as client:
            yield client


def _retry_after(response: httpx.Response) -> float | None:
    """Discord 延迟单位为秒；畸形值交给调用方的默认退避。"""
    try:
        body = response.json()
    except ValueError:
        body = None
    value = body.get("retry_after") if isinstance(body, dict) else None
    if value is None:
        value = response.headers.get("Retry-After")
    if isinstance(value, bool):
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return seconds if isfinite(seconds) and seconds >= 0 else None


class DiscordWebhookSender:
    """只发送一次并返回消息编号；不休眠、重发或保存领域状态。"""

    def __init__(self, webhook_url: str, *, username: str = DEFAULT_DISCORD_USERNAME):
        """公共包独立使用时也必须校验目标；异常不回显传入 URL。"""
        self._webhook_url = validate_discord_webhook_url(webhook_url)
        self._username = validate_discord_username(username)

    async def __call__(self, content: str, *, suppress_embeds: bool = False) -> str:
        """wait 确认实际消息；预览选项只映射 Discord 的原生消息标志。"""
        webhook = _DiscordWebhook(
            url=self._webhook_url, content=content, username=self._username, allowed_mentions={"parse": []},
            flags=4 if suppress_embeds else None, rate_limit_retry=False, timeout=10, wait=True,
        )
        try:
            # execute() 会记录原始错误正文；只复用 SDK 的单次请求入口。
            response = await webhook.api_post_request()
        except httpx.HTTPError:
            raise WebhookDeliveryError("discord_network_error") from None
        if response.status_code == 429:
            raise WebhookDeliveryError("discord_rate_limited", retry_after=_retry_after(response))
        if not 200 <= response.status_code < 300:
            raise WebhookDeliveryError("discord_http_error", permanent=300 <= response.status_code < 500)
        try:
            body = response.json()
        except ValueError:
            raise WebhookDeliveryError("discord_invalid_response") from None
        message_id = body.get("id") if isinstance(body, dict) else None
        if (not isinstance(message_id, str) or not message_id.isascii()
                or not message_id.isdigit() or len(message_id) > 128):
            raise WebhookDeliveryError("discord_invalid_response")
        return message_id
