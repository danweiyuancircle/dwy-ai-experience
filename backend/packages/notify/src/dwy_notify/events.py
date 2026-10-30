"""跨来源的已验证通知，不包含签名、凭据或原始邮件内容。"""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class NotificationEvent:
    """scope 隔离同一提供方的不同应用；data 仅携带适配器筛选后的元数据。"""

    source: str
    scope: str
    event_id: str
    event_type: str
    content: str
    data: Mapping[str, object] = field(default_factory=dict, repr=False)


# True 表示本次接受，False 表示已接受的重复；异常必须阻止 HTTP 成功确认。
EventSink = Callable[[NotificationEvent], Awaitable[bool]]
