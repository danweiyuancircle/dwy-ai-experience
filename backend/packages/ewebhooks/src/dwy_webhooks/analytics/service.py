"""北京时间发送边界驱动有界重查；网络任务不占用数据库事务。"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from dwyeapi.logger import get_logger

from .formatting import apple_business_digest_content
from .models import AnalyticsValue


class AnalyticsMonitor:
    """只编排采集、同口径比较和原子 outbox，发送重试复用公共队列。"""

    def __init__(self, config, store, client, *, feedback=None):
        """反馈是可选 async(app_id, UTC 创建日) 回调，不依赖评论扩展。"""
        self.config, self.store, self.client, self.feedback = config, store, client, feedback

    async def run_once(self) -> int:
        """发送边界后仅生成当前日报及周一周报，启动时不补发历史日期。"""
        config = self.config
        await self.store.cleanup(config.issuer_id, config.retention_days)
        now = datetime.fromtimestamp(self.store.clock(), ZoneInfo(config.timezone))
        boundary = now.replace(hour=config.send_hour, minute=config.send_minute, second=0, microsecond=0)
        if now < boundary:
            return 0
        # Apple UTC 日报存在生成延迟，早间只读取发送日期前两天的数据。
        target = now.date() - timedelta(days=2)
        start = target - timedelta(days=6)
        next_poll = int((boundary + timedelta(days=1)).timestamp())
        completed = 0
        for app_id, application in config.apps.items():
            token = await self.store.claim(config.issuer_id, app_id, target)
            if token is None:
                continue
            try:
                # 采集预算小于 300 秒租约，超时不能提交部分日期。
                async with asyncio.timeout(240):
                    snapshots = []
                    for index in range(7):
                        day = start + timedelta(days=index)
                        snapshot = await self.client.collect(app_id, day)
                        if snapshot.app_id != app_id or snapshot.report_date != day:
                            raise ValueError("Analytics client returned a mismatched scope or date")
                        if self.feedback is not None:
                            try:
                                counts = await self.feedback(app_id, day)
                            except Exception:
                                # 可选评论源暂时失败不应阻断官方经营数据；取消仍向外传播。
                                counts = {}
                            if not isinstance(counts, dict):
                                counts = {}
                            metrics = dict(snapshot.metrics)
                            for key in ("review_count", "low_star_reviews"):
                                value = counts.get(key)
                                valid = type(value) is int and value >= 0
                                metrics[key] = AnalyticsValue(
                                    value=Decimal(value) if valid else None,
                                    status="available" if valid else "unavailable",
                                    source="App Store Reviews（UTC 创建日）",
                                )
                            snapshot = snapshot.model_copy(update={"metrics": metrics})
                        snapshots.append(snapshot)
                    historical = await self.store.load(
                        config.issuer_id, app_id, start - timedelta(days=7), start - timedelta(days=1)
                    )
                    # 重查后的前一天优先于旧版本；更早一周只使用已持久化历史。
                    daily_previous = [snapshots[-2]]
                    messages = [
                        (
                            "daily",
                            target,
                            target,
                            apple_business_digest_content(
                                application.name,
                                [snapshots[-1]],
                                comparison=daily_previous,
                                week_comparison=[
                                    snap
                                    for snap in historical
                                    if snap.report_date == target - timedelta(days=7)
                                ],
                            ),
                        )
                    ]
                    if now.weekday() == 0:
                        messages.append(
                            (
                                "weekly",
                                start,
                                target,
                                apple_business_digest_content(
                                    application.name, snapshots, period="weekly", comparison=historical
                                ),
                            )
                        )
                    completed += int(
                        await self.store.complete(
                            config.issuer_id,
                            app_id,
                            token,
                            snapshots,
                            report_date=target,
                            messages=messages,
                            next_poll_at=next_poll,
                        )
                    )
            except asyncio.CancelledError:
                await self.store.release(config.issuer_id, app_id, token)
                raise
            except Exception:
                get_logger(__name__).error(
                    "Apple analytics collection failed code=ANALYTICS_COLLECTION_FAILED"
                )
                await self.store.fail(config.issuer_id, app_id, token, target, app_name=application.name)
        return completed

    async def run(self) -> None:
        """每分钟检查持久计划，失败或重启由数据库调度接续。"""
        while True:
            try:
                await self.run_once()
            except Exception:
                get_logger(__name__).error("Apple analytics monitor failed code=ANALYTICS_MONITOR_FAILED")
            await asyncio.sleep(60)
