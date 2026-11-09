"""跨来源的已验证通知，不包含签名、凭据或原始邮件内容。"""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field

from .models import NotificationAppearance


@dataclass(frozen=True, slots=True)
class NotificationEvent:
    """scope 隔离应用，data 仅含安全元数据；appearance 是可被应用覆盖的事件默认展示。"""

    source: str
    scope: str
    event_id: str
    event_type: str
    content: str
    data: Mapping[str, object] = field(default_factory=dict, repr=False)
    appearance: NotificationAppearance | None = None


# True 表示本次接受，False 表示已接受的重复；异常必须阻止 HTTP 成功确认。
EventSink = Callable[[NotificationEvent], Awaitable[bool]]
