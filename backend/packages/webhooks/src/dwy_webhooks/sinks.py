"""缺省同步转发及有界去重；需要持久接收的项目可以注入自己的 sink。"""

import asyncio
from collections import OrderedDict
from typing import Protocol

from dwy_notify import Notifier

from .events import WebhookEvent
from .notifications import delivery_error
from .validation import DEFAULT_DISCORD_USERNAME

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


class NotificationRelay:
    """逐目标确认成功；来源重投只重试尚未确认的目标。"""

    def __init__(self, notifier: Notifier, receipts: ReceiptStore | None = None):
        """默认去重仅在实例内；跨重启持久确认由宿主注入接收账本。"""
        self.notifier = notifier
        self.receipts = receipts if receipts is not None else MemoryReceiptStore()
        self._lock = asyncio.Lock()

    async def __call__(self, event: WebhookEvent) -> bool:
        """一个目标失败不阻止其他目标；只记录已实际成功的投递。"""
        accepted, failure = False, None
        async with self._lock:
            for target in self.notifier.targets:
                identity = f"{event.source}:{target}:{self.notifier.target_fingerprint(target)}"
                key = (identity, event.scope, event.event_id)
                if await self.receipts.contains(key):
                    continue
                result = await self.notifier.send(event.content, targets=(target,))
                delivery = result.deliveries[0]
                if delivery.success:
                    await self.receipts.add(key)
                    accepted = True
                elif failure is None:
                    failure = delivery_error(delivery)
            if failure is not None:
                raise failure
        return accepted


class DiscordRelay(NotificationRelay):
    """发送成功才接受事件；网络故障由接收端返回失败供提供方重试。"""

    def __init__(self, webhook_url: str, receipts: ReceiptStore | None = None, *,
                 username: str = DEFAULT_DISCORD_USERNAME):
        """锁和去重状态属于当前集成，不存在跨项目的模块全局状态。"""
        from .notifications import legacy_discord_config
        from .validation import validate_discord_webhook_url

        super().__init__(Notifier(legacy_discord_config(validate_discord_webhook_url(webhook_url), username)),
                         receipts)
