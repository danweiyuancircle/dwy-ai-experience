"""FastAPI 一次注册入口；来源配置、去重与关闭生命周期都由模块装配。"""

from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass, field
from typing import Protocol

from dwyeapi.exceptions import register_exception_handlers
from fastapi import APIRouter, FastAPI

from .config import WebhookConfig, WebhookSourceConfig
from .events import EventSink
from .sinks import DiscordRelay, MemoryReceiptStore, ReceiptStore


class _CloseableVerifier(Protocol):
    """只约束安装器实际需要的关闭能力，不引入来源业务模型。"""

    async def aclose(self) -> None:
        """等待验证资源安全退出。"""
        ...


@dataclass(frozen=True, slots=True)
class WebhookSinks:
    """有自己账本的项目可按来源替换接收行为；缺省使用 DiscordRelay。"""

    resend: EventSink | None = None
    app_store_connect: EventSink | None = None
    apple_notifications: EventSink | None = None


@dataclass(slots=True)
class WebhookRuntime:
    """属于当前 FastAPI 实例的集成资源，不包含宿主配置或数据库。"""

    receipts: ReceiptStore
    verifiers: list[_CloseableVerifier] = field(default_factory=list, repr=False)
    closed: bool = False

    async def aclose(self) -> None:
        """幂等关闭全部验证器；即使某一关闭失败也继续释放其余资源。"""
        if self.closed:
            return
        try:
            async with AsyncExitStack() as stack:
                for verifier in self.verifiers:
                    stack.push_async_callback(verifier.aclose)
        finally:
            self.closed = True


def _sink(source: WebhookSourceConfig, config: WebhookConfig,
          override: EventSink | None, receipts: ReceiptStore) -> EventSink:
    """自定义接收优先；自动转发必须显式配置可信 Discord 目标。"""
    if override is not None:
        return override
    destination = source.discord_webhook_url or config.discord_webhook_url
    if destination is None:
        raise ValueError("Enabled webhook source requires a Discord target or a custom sink")
    username = source.discord_username if source.discord_username is not None else config.discord_username
    return DiscordRelay(destination.get_secret_value(), receipts, username=username)


def install_webhooks(app: FastAPI, config: WebhookConfig, *,
                     sinks: WebhookSinks | None = None,
                     receipts: ReceiptStore | None = None) -> WebhookRuntime:
    """注册全部已配置来源；复用原宿主 lifespan，公开 URL 可由独立配置选择。"""
    if hasattr(app.state, "dwy_webhooks"):
        raise ValueError("Webhooks already installed on this application")
    selected = sinks if sinks is not None else WebhookSinks()
    store = receipts if receipts is not None else MemoryReceiptStore()
    runtime = WebhookRuntime(store)
    router = APIRouter()
    # 先验证默认接收器，避免配置错误后留下已注册的半套路由。
    resend_sink = (_sink(config.resend, config, selected.resend, store)
                   if config.resend is not None else None)
    asc_sink = (_sink(config.app_store_connect, config, selected.app_store_connect, store)
                if config.app_store_connect is not None else None)
    apple_sink = (_sink(config.apple_notifications, config, selected.apple_notifications, store)
                  if config.apple_notifications is not None else None)
    if config.resend is not None:
        from .providers.resend import create_resend_router

        router.include_router(create_resend_router(config.resend, resend_sink))
    if config.app_store_connect is not None:
        from .providers.app_store_connect import create_asc_router

        router.include_router(create_asc_router(config.app_store_connect, asc_sink))
    if config.apple_notifications is not None:
        from .providers.apple import AppleNotificationVerifier, create_apple_router

        verifiers = {key: AppleNotificationVerifier(application)
                     for key, application in config.apple_notifications.apps.items()}
        runtime.verifiers.extend(verifiers.values())
        router.include_router(create_apple_router(config.apple_notifications, apple_sink, verifiers))
    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        """原项目启动失败或关闭异常时，也释放当前集成自己的资源。"""
        try:
            async with previous_lifespan(application) as state:
                yield state
        finally:
            await runtime.aclose()

    app.include_router(router)
    app.router.lifespan_context = lifespan
    app.state.dwy_webhooks = runtime
    return runtime


def create_app(config: WebhookConfig) -> FastAPI:
    """显式配置的独立 ASGI 应用；配置读取与密钥获取属于调用项目。"""
    app = FastAPI(title="Webhooks", docs_url=None, redoc_url=None, openapi_url=None)
    register_exception_handlers(app)
    install_webhooks(app, config)
    return app
