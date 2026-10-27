"""把评论采集和持久投递安装到调用项目的 FastAPI 生命周期。"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial

from .client import AppleReviewClient
from .delivery import ReviewDeliveryQueue
from .service import ReviewMonitor
from .storage import ReviewStore


@dataclass(frozen=True)
class ReviewRuntime:
    """公开显式运行组件，便于项目监控或手动执行一次同步。"""

    monitor: ReviewMonitor
    queue: ReviewDeliveryQueue


def install_review_monitor(app, config, sessions, tables, *, client=None, sender=None) -> ReviewRuntime:
    """只装配，不连接或迁移数据库；外部注入客户端不由当前运行时关闭。"""
    if hasattr(app.state, "dwy_review_monitor"):
        raise ValueError("Review monitor already installed")
    if sender is None:
        if config.discord_webhook_url is None:
            raise ValueError("Review monitor requires a Discord destination or sender")
        from ..discord import DiscordWebhookSender

        sender = partial(
            DiscordWebhookSender(
                config.discord_webhook_url.get_secret_value(), username=config.discord_username,
            ),
            suppress_embeds=True,
        )
    owned_client = client is None
    collector = AppleReviewClient(config) if owned_client else client
    store = ReviewStore(sessions, tables)
    monitor = ReviewMonitor(config, store, collector)
    queue = ReviewDeliveryQueue(sessions, tables.deliveries, sender, retention_days=config.retention_days)
    runtime = ReviewRuntime(monitor, queue)
    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        """先停止后台任务，再让宿主释放引擎，最后关闭自有 HTTP 客户端。"""
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
    app.state.dwy_review_monitor = runtime
    return runtime
