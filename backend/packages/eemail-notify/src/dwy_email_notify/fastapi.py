"""组合邮件事件路由；通知传输和去重复用 dwy-notify。"""

from dataclasses import dataclass

from dwy_notify.events import EventSink
from dwy_notify.integration import configured_notifier
from dwy_notify.relay import MemoryReceiptStore, NotificationRelay, ReceiptStore
from fastapi import FastAPI

from .config import EmailNotifyConfig


@dataclass(frozen=True, slots=True)
class EmailNotifyRuntime:
    """当前应用的接收去重状态；不创建需要关闭的网络或数据库资源。"""

    receipts: ReceiptStore


def install_email_notifications(app: FastAPI, config: EmailNotifyConfig, *,
                                sink: EventSink | None = None,
                                receipts: ReceiptStore | None = None) -> EmailNotifyRuntime:
    """只注册已配置来源，接受自有持久化 sink；保持宿主 lifespan 和异常处理器。"""
    if hasattr(app.state, "dwy_email_notify"):
        raise ValueError("Email notifications already installed on this application")
    store = receipts if receipts is not None else MemoryReceiptStore()
    if config.resend is not None:
        from .providers.resend.appearance import DEFAULT_APPEARANCE
        from .providers.resend.webhooks import create_resend_router

        selected = sink
        if selected is None:
            notifier = configured_notifier(config.resend, config)
            if notifier is None:
                raise ValueError("Email webhook source requires notifications or a custom sink")
            selected = NotificationRelay(notifier, store, appearance=DEFAULT_APPEARANCE)
        app.include_router(create_resend_router(config.resend, selected))
    runtime = EmailNotifyRuntime(store)
    app.state.dwy_email_notify = runtime
    return runtime
