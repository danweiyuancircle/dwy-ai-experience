"""把独立经营采集和公共投递队列安装到宿主生命周期。"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial

from ..delivery import SQLAlchemyDeliveryQueue
from .client import AppleAnalyticsClient
from .service import AnalyticsMonitor
from .storage import AnalyticsStore


@dataclass(frozen=True)
class AnalyticsRuntime:
    """公开组件供宿主监控和手动执行；资源仍归宿主所有。"""

    monitor: AnalyticsMonitor
    queue: SQLAlchemyDeliveryQueue


def install_analytics_monitor(
    app, config, sessions, tables, *, client=None, sender=None, feedback=None
) -> AnalyticsRuntime:
    """不建表、不迁移；注入客户端不关闭，自有客户端在任务和宿主资源之后关闭。"""
    if hasattr(app.state, "dwy_analytics_monitor"):
        raise ValueError("Analytics monitor already installed")
    if sender is None:
        if config.discord_webhook_url is None:
            raise ValueError("Analytics monitor requires a Discord destination or sender")
        from ..discord import DiscordWebhookSender

        sender = partial(
            DiscordWebhookSender(
                config.discord_webhook_url.get_secret_value(), username=config.discord_username
            ),
            suppress_embeds=True,
        )
    owned_client = client is None
    collector = AppleAnalyticsClient(config) if owned_client else client
    store = AnalyticsStore(sessions, tables)
    monitor = AnalyticsMonitor(config, store, collector, feedback=feedback)
    queue = SQLAlchemyDeliveryQueue(sessions, tables.deliveries, sender, source="app_store_analytics")
    runtime = AnalyticsRuntime(monitor, queue)
    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        try:
            async with previous_lifespan(application) as state:
                async with asyncio.TaskGroup() as group:
                    tasks = [group.create_task(monitor.run()), group.create_task(queue.run())]
                    try:
                        yield state
                    finally:
                        for task in tasks:
                            task.cancel()
        finally:
            if owned_client:
                await collector.aclose()

    app.router.lifespan_context = lifespan
    app.state.dwy_analytics_monitor = runtime
    return runtime
