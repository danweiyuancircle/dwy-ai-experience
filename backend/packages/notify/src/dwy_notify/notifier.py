"""同步 SDK 在线程中执行，锁只覆盖同一实例内的同一个目标。"""

import asyncio
import hashlib
import threading
from collections.abc import Sequence

import requests

from ._appearance import active_appearance
from ._logging import notification_http_active
from ._plugins import create_plugin
from .models import NotificationAppearance, NotificationConfig, NotificationDelivery, NotificationResult


class Notifier:
    """显式配置的异步通知器；不读环境变量、不重试、不记录 URL 或正文。

    取消等待会向调用方传播；已开始的同步请求由超时结束，同目标锁直到请求结束才释放。
    """

    def __init__(self, config: NotificationConfig, *, url_appearance_is_default: bool = False):
        """固定目标；兼容层生成的隐式 URL 展示可降为默认值，不改变旧目标指纹。"""
        self._plugins = {
            name: create_plugin(url.get_secret_value(), config.timeout_seconds)
            for name, url in config.targets.items()
        }
        self._fingerprints = {
            name: hashlib.sha256(url.get_secret_value().encode()).hexdigest()
            for name, url in config.targets.items()
        }
        self._locks = {name: threading.Lock() for name in self._plugins}
        self._appearance = config.appearance
        self._url_appearance_is_default = url_appearance_is_default

    @property
    def targets(self) -> tuple[str, ...]:
        return tuple(self._plugins)

    def target_fingerprint(self, name: str) -> str:
        """返回目标 URL 的 SHA-256 摘要，用于队列检测接收方配置变更。"""
        return self._fingerprints[name]

    async def send(
        self, body: str, *, title: str = "", targets: Sequence[str] | None = None,
        appearance: NotificationAppearance | None = None,
        default_appearance: NotificationAppearance | None = None,
    ) -> NotificationResult:
        """逐目标发送；展示按单次、应用配置、URL 显式配置、调用方预设的顺序覆盖。

        合并后每个目标必须有发送者名称，缺少时在任何网络请求前拒绝。
        头像可显式 None 使用平台默认；正文 title 不代替发送者名称。
        """
        if not isinstance(body, str) or not body.strip():
            raise ValueError("invalid_body")
        if not isinstance(title, str):
            raise ValueError("invalid_title")
        if targets is not None and (isinstance(targets, (str, bytes)) or not targets):
            raise ValueError("invalid_targets")
        selected = self.targets if targets is None else tuple(targets)
        if any(not isinstance(name, str) for name in selected):
            raise ValueError("invalid_targets")
        if any(name not in self._plugins for name in selected):
            raise ValueError("unknown_target")
        if len(selected) != len(set(selected)):
            raise ValueError("duplicate_target")
        displays = {}
        for name in selected:
            display = {}
            url_display = getattr(self._plugins[name], "notification_appearance", {})
            if self._url_appearance_is_default:
                display.update(url_display)
            if default_appearance is not None:
                display.update(default_appearance.model_dump(exclude_unset=True))
            if not self._url_appearance_is_default:
                display.update(url_display)
            display.update(self._appearance.model_dump(exclude_unset=True))
            if appearance is not None:
                display.update(appearance.model_dump(exclude_unset=True))
            if display.get("username") is None:
                raise ValueError("missing_username")
            displays[name] = display
        deliveries = await asyncio.gather(
            *(asyncio.to_thread(self._send, name, body, title, displays[name])
              for name in selected)
        )
        return NotificationResult(deliveries=tuple(deliveries))

    def _send(self, target, body, title, display) -> NotificationDelivery:
        with self._locks[target]:
            plugin = self._plugins[target]
            plugin.outcome = {}
            display_token = active_appearance.set(display)
            token = notification_http_active.set(True)
            try:
                success = bool(plugin.notify(body=body, title=title))
            except requests.Timeout:
                return NotificationDelivery(target=target, success=False, error_code="timeout")
            except requests.RequestException:
                return NotificationDelivery(target=target, success=False, error_code="network_error")
            except Exception:
                # 第三方插件可能把响应正文放入异常；在 SDK 边界只返回固定错误码。
                return NotificationDelivery(target=target, success=False, error_code="provider_error")
            finally:
                notification_http_active.reset(token)
                active_appearance.reset(display_token)
            return NotificationDelivery(
                target=target,
                success=success,
                **(plugin.outcome if plugin.outcome else {} if success else {"error_code": "send_failed"}),
            )
