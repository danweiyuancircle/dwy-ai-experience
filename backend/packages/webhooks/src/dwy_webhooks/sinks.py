"""缺省同步转发及有界去重；需要持久接收的项目可以注入自己的 sink。"""

import asyncio
from collections import OrderedDict
from typing import Protocol

from .events import WebhookEvent

EventKey = tuple[str, str, str]


class ReceiptStore(Protocol):
    """可替换的已送达记录；不能把尚未送达的消息提前记作成功。"""

    async def contains(self, key: EventKey) -> bool:
        """查询来源、应用、通知编号组成的完整隔离键。"""
        ...

    async def add(self, key: EventKey) -> None:
        """仅在目标确认发送成功后记录。"""
        ...


class MemoryReceiptStore:
    """实例内有界 LRU；重启后上游重投可能再次发送，不承诺持久去重。"""

    def __init__(self, capacity: int = 4096):
        """限制内存增长；共享多进程去重需由调用方提供原子持久接收入口。"""
        if not 1 <= capacity <= 100000:
            raise ValueError("Receipt capacity must be between 1 and 100000")
        self.capacity = capacity
        self._items: OrderedDict[EventKey, None] = OrderedDict()

    async def contains(self, key: EventKey) -> bool:
        """不执行阻塞 I/O；由 relay 的锁保护检查到提交之间的竞态。"""
        if key not in self._items:
            return False
        self._items.move_to_end(key)
        return True

    async def add(self, key: EventKey) -> None:
        """淘汰最旧的成功记录，不保存签名、消息正文或密钥。"""
        self._items[key] = None
        self._items.move_to_end(key)
        if len(self._items) > self.capacity:
            self._items.popitem(last=False)


class DiscordRelay:
    """发送成功才接受事件；网络故障由接收端返回失败供提供方重试。"""

    def __init__(self, webhook_url: str, receipts: ReceiptStore | None = None):
        """锁和去重状态属于当前集成，不存在跨项目的模块全局状态。"""
        from .discord import DiscordWebhookSender

        self.sender = DiscordWebhookSender(webhook_url)
        self.receipts = receipts if receipts is not None else MemoryReceiptStore()
        self._lock = asyncio.Lock()

    async def __call__(self, event: WebhookEvent) -> bool:
        """所有提供方按完整身份去重；失败和取消都不会提交已送达记录。"""
        key = (event.source, event.scope, event.event_id)
        async with self._lock:
            if await self.receipts.contains(key):
                return False
            await self.sender(event.content, suppress_embeds=True)
            await self.receipts.add(key)
            return True
