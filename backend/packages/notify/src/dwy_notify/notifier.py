"""同步 SDK 在线程中执行，锁只覆盖同一实例内的同一个目标。"""

import asyncio
import hashlib
import threading
from collections.abc import Sequence

import requests

from ._logging import notification_http_active
from ._plugins import create_plugin
from .models import NotificationConfig, NotificationDelivery, NotificationResult


class Notifier:
    """显式配置的异步通知器；不读环境变量、不重试、不记录 URL 或正文。

    取消等待会向调用方传播；已开始的同步请求由超时结束，同目标锁直到请求结束才释放。
    """

    def __init__(self, config: NotificationConfig):
        """固定目标与安全配置；无效 URL 只抛出固定错误，不回显凭据。"""
        self._plugins = {
            name: create_plugin(url.get_secret_value(), config.timeout_seconds)
            for name, url in config.targets.items()
        }
        self._fingerprints = {
            name: hashlib.sha256(url.get_secret_value().encode()).hexdigest()
            for name, url in config.targets.items()
        }
        self._locks = {name: threading.Lock() for name in self._plugins}

    @property
    def targets(self) -> tuple[str, ...]:
        return tuple(self._plugins)

    def target_fingerprint(self, name: str) -> str:
        """返回目标 URL 的 SHA-256 摘要，用于队列检测接收方配置变更。"""
        return self._fingerprints[name]

    async def send(
        self, body: str, *, title: str = "", targets: Sequence[str] | None = None
    ) -> NotificationResult:
        """发送到全部或指定目标；结果保留顺序，未知或重复目标在网络调用前报错。"""
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
        deliveries = await asyncio.gather(
            *(asyncio.to_thread(self._send, name, body, title) for name in selected)
        )
        return NotificationResult(deliveries=tuple(deliveries))

    def _send(self, target: str, body: str, title: str) -> NotificationDelivery:
        with self._locks[target]:
            plugin = self._plugins[target]
            plugin.outcome = {}
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
            return NotificationDelivery(
                target=target,
                success=success,
                **(plugin.outcome if plugin.outcome else {} if success else {"error_code": "send_failed"}),
            )
