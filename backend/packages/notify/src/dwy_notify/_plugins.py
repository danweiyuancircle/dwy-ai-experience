"""固定版本 Apprise 的窄适配；保留上游解析、分段和 Discord 消息构造。"""

import importlib
import logging
from urllib.parse import parse_qs, urlsplit, urlunsplit

import requests
from apprise import AppriseAsset, NotifyFormat, NotifyType
from apprise.plugins import N_MGR
from apprise.plugins.discord import NotifyDiscord
from apprise.plugins.wecombot import NotifyWeComBot

from . import _transport
from ._appearance import active_appearance
from .models import NotificationAppearance


class _QuietLogger(logging.Logger):
    def trace(self, *args, **kwargs):
        pass


# 插件调试日志会包含 URL 和正文；只隔离本包子类，不能修改宿主的 logger。
_quiet_logger = _QuietLogger("dwy_notify.apprise", level=100)
_quiet_logger.propagate = False
_quiet_logger.addHandler(logging.NullHandler())


class _Discord(NotifyDiscord):
    logger = _quiet_logger

    def _send(self, payload, attach=None, params=None, **kwargs):
        if self.outcome.get("error_code"):
            return False
        payload.pop("allow_mentions", None)
        payload["allowed_mentions"] = {"parse": []}
        payload["flags"] = payload.get("flags", 0) | 4
        for key, value in active_appearance.get().items():
            if value is None:
                payload.pop(key, None)
            else:
                payload[key] = value
        response = _transport.send(
            self,
            f"{self.notify_url}/{self.webhook_id}/{self.webhook_token}",
            payload,
            params={**(params or {}), "wait": "true"},
        )
        if response is None:
            return False
        try:
            data = response.json()
        except ValueError:
            data = None
        message_id = data.get("id") if isinstance(data, dict) else None
        if (
            not isinstance(message_id, str)
            or not 1 <= len(message_id) <= 128
            or not message_id.isascii()
            or not message_id.isdecimal()
        ):
            self.outcome = {"error_code": "invalid_response"}
            return False
        self.outcome = {"message_id": message_id}
        return True


class _WeComBot(NotifyWeComBot):
    logger = _quiet_logger

    def send(self, body, title="", **kwargs):
        response = _transport.send(
            self,
            self.api_url,
            {"msgtype": "text", "text": {"content": f"{title}\r\n{body}" if title else body}},
        )
        if response is None:
            return False
        try:
            data = response.json()
        except ValueError:
            data = None
        if not isinstance(data, dict) or type(data.get("errcode")) is not int or data["errcode"] != 0:
            self.outcome = {"error_code": "provider_error"}
            return False
        return True


def create_plugin(url: str, timeout: float):
    parsed = urlsplit(url)
    if parsed.scheme == "https" and parsed.hostname in {"discord.com", "discordapp.com"}:
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "webhooks"] and not parsed.username:
            url = urlunsplit(("discord", parts[2], "/" + parts[3], parsed.query, ""))
            parsed = urlsplit(url)
    if parsed.scheme not in N_MGR:
        raise ValueError("invalid_target")
    base = N_MGR[parsed.scheme]
    if base.__module__.split(".")[2] in {"fluxer", "revolt", "matrix", "sparkpost", "sendpulse"}:
        # 这些固定版本插件有绕过 retry=0 的内部重试，不能兑现单次发送约定。
        raise ValueError("unsupported_transport")
    # 只接受上游基于 requests 的 HTTPS 渠道；SMTP、本地命令等不共享 HTTP 安全约束。
    if getattr(importlib.import_module(base.__module__), "requests", None) is not requests:
        raise ValueError("unsupported_transport")
    protocols = base.secure_protocol
    if isinstance(protocols, str):
        protocols = (protocols,)
    if not protocols or parsed.scheme not in protocols or not base.enabled:
        raise ValueError("unsupported_transport")
    plugin_type = {NotifyDiscord: _Discord, NotifyWeComBot: _WeComBot}.get(base)
    if plugin_type is None:
        plugin_type = type(f"_Safe{base.__name__}", (base,), {"logger": _quiet_logger})
    try:
        options = plugin_type.parse_url(url)
        if options is None:
            raise ValueError("invalid_target")
        options.update(
            verify=True,
            redirect=False,
            retry=0,
            optional=False,
            cto=timeout,
            rto=timeout,
            secure=True,
            asset=AppriseAsset(secure_logging=True, http_redirects=False),
        )
        plugin = plugin_type(**options)
    except (TypeError, ValueError, AttributeError):
        raise ValueError("invalid_target") from None
    if not plugin.enabled:
        raise ValueError("invalid_target")
    if isinstance(plugin, _Discord):
        plugin.notify_format = NotifyFormat.TEXT
        plugin.notification_appearance = {}
        if plugin.user:
            plugin.notification_appearance.update(
                NotificationAppearance(username=plugin.user).model_dump(exclude_unset=True),
            )
        if plugin.avatar_url:
            plugin.notification_appearance["avatar_url"] = plugin.avatar_url
        avatar_explicit = "avatar" in parse_qs(parsed.query)
        if avatar_explicit:
            plugin.notification_appearance["avatar_url"] = (
                (plugin.avatar_url or plugin.image_url(NotifyType.INFO)) if plugin.avatar else None
            )
        # 默认头像归平台；只保留用户显式要求的 Apprise 头像行为。
        if not avatar_explicit:
            plugin.avatar = bool(plugin.avatar_url)
    return plugin
