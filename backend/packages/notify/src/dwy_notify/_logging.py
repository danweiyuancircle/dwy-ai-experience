"""只过滤当前通知工作线程的原始 HTTP 调试日志，不改变宿主日志级别。"""

import logging
from contextvars import ContextVar

notification_http_active: ContextVar[bool] = ContextVar("dwy_notify_http_active", default=False)


class _NotificationHTTPFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not notification_http_active.get()


# urllib3 会在 DEBUG 输出包含凭据的请求路径；过滤器只作用于通知的同步 HTTP 区间。
for _name in (
    "urllib3.connectionpool",
    "urllib3.util.retry",
    "requests.packages.urllib3.connectionpool",
    "requests.packages.urllib3.util.retry",
):
    logging.getLogger(_name).addFilter(_NotificationHTTPFilter())
