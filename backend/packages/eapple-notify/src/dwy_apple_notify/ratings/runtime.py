"""评分日报的显式资源装配与 FastAPI 生命周期。"""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass

from dwy_notify.integration import configured_notifier

from .appearance import DEFAULT_APPEARANCE
from .client import AppleRatingClient
from .delivery import RatingDeliveryQueue
from .service import RatingMonitor
from .storage import RatingStore


@dataclass(frozen=True)
class RatingRuntime:
    """公开单次监控与持久队列入口，供宿主健康检查和离线执行。"""

    monitor: RatingMonitor
    queue: RatingDeliveryQueue


def install_rating_monitor(
    app, config, sessions, tables, *, client=None, sender=None, clock=time.time
) -> RatingRuntime:
    """只装配、不迁移；外部会话、HTTP 客户端和发送器均由宿主管理。"""
    if hasattr(app.state, "dwy_rating_monitor"):
        raise ValueError("Rating monitor already installed")
    notifier = configured_notifier(config) if sender is None else None
    if sender is None and notifier is None:
        raise ValueError("Rating monitor requires notifications or sender")
    owned_client = client is None
    collector = AppleRatingClient(config) if owned_client else client
    store = RatingStore(sessions, tables, clock=clock)
    monitor = RatingMonitor(config, store, collector, clock=clock)
    queue = RatingDeliveryQueue(
        sessions,
        tables.deliveries,
        sender,
        notifier=notifier,
        app_ids=config.apps,
        appearance=DEFAULT_APPEARANCE,
        clock=clock,
    )
    runtime = RatingRuntime(monitor, queue)
    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        """先取消工作任务再释放宿主数据库，最后关闭库自建 HTTP 客户端。"""
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
    app.state.dwy_rating_monitor = runtime
    return runtime
