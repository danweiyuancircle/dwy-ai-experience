"""持久化计划驱动的轻量轮询；运行资源由消费项目拥有。"""

import asyncio

from dwyeapi.logger import get_logger


class ReviewMonitor:
    """只编排完整采集与原子提交；与 Discord 投递消费者独立执行。"""

    def __init__(self, config, store, client):
        """配置、时钟驱动的存储和客户端全部显式注入。"""
        self.config, self.store, self.client = config, store, client

    async def run_once(self) -> int:
        """先清理历史，再检查到期应用；一次错误不影响其它应用。"""
        await self.store.cleanup(self.config.retention_days)
        completed = 0
        for app_id, application in self.config.apps.items():
            token = await self.store.claim(app_id, poll_interval_seconds=self.config.poll_interval_seconds)
            if token is None:
                continue
            try:
                # 小于持久租约 300 秒；超时的部分分页不能推进同步基线。
                async with asyncio.timeout(120):
                    reviews = await self.client.list_reviews(app_id)
                    accepted = await self.store.complete(
                        app_id, token, reviews, app_name=application.name,
                        poll_interval_seconds=self.config.poll_interval_seconds,
                        retention_days=self.config.retention_days,
                    )
                completed += int(accepted)
            except asyncio.CancelledError:
                await self.store.release(app_id, token)
                raise
            except Exception:
                # 错误对象可能包含认证头或评论，日志仅输出固定状态码。
                get_logger(__name__).error("Apple review collection failed code=REVIEW_COLLECTION_FAILED")
                await self.store.release(app_id, token)
        return completed

    async def run(self) -> None:
        """一分钟仅检查数据库计划，实际 Apple 请求遵守配置的小时周期。"""
        while True:
            try:
                await self.run_once()
            except Exception:
                get_logger(__name__).error("Apple review monitor failed code=REVIEW_MONITOR_FAILED")
            await asyncio.sleep(min(60, self.config.poll_interval_seconds))
