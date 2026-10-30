"""展示参数只属于当前同步发送上下文，避免并发消息修改共享插件配置。"""

from contextvars import ContextVar

active_appearance: ContextVar[dict[str, str | None] | None] = ContextVar(
    "dwy_notify_appearance", default=None,
)
