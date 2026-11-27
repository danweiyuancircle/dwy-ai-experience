"""独立的每日评分调度；失败结果定稿后只重试通知投递。"""

import asyncio
import time
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from dwyeapi.logger import get_logger

from .models import RatingCollectionError


class RatingMonitor:
    """按本地日期领取一次跨应用、地区采集计划，不补造停机期间历史。"""

    def __init__(self, config, store, client, *, clock: Callable[[], float] = time.time):
        self.config, self.store, self.client, self.clock = config, store, client, clock

    async def run_once(self) -> int:
        """生成日报返回 1，未到期或已执行返回 0；各地区失败不阻塞其余项目。"""
        config = self.config
        now = datetime.fromtimestamp(self.clock(), ZoneInfo(config.timezone))
        day = now.date()
        await self.store.cleanup(config, day)
        if (now.hour, now.minute) < (config.send_hour, config.send_minute):
            return 0
        token = await self.store.claim(config.timezone, day)
        if token is None:
            return 0
        try:
            results = dict.fromkeys(
                (app_id, territory) for app_id in config.apps for territory in config.territories
            )
            for app_id, territory in results:
                if not await self.store.renew(config.timezone, day, token):
                    return 0
                if datetime.fromtimestamp(self.clock(), ZoneInfo(config.timezone)).date() > day:
                    break
                try:
                    async with asyncio.timeout(25):
                        results[(app_id, territory)] = await self.client.get_rating(app_id, territory)
                except (RatingCollectionError, TimeoutError):
                    results[(app_id, territory)] = None
            if datetime.fromtimestamp(self.clock(), ZoneInfo(config.timezone)).date() > day:
                # shortcut: 跨日丢弃部分成功值，需保留时再引入逐项采集时间。
                results = dict.fromkeys(results)
            return int(await self.store.complete(config, day, token, results))
        finally:
            await self.store.release(config.timezone, day, token)

    async def run(self) -> None:
        """每分钟只检查数据库计划，不因投递失败或重复唤醒再次查询 Apple。"""
        while True:
            try:
                await self.run_once()
            except Exception:
                get_logger(__name__).error("Apple ratings monitor failed code=RATING_MONITOR_FAILED")
            await asyncio.sleep(60)
