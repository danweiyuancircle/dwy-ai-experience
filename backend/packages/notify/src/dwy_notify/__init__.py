"""独立多目标通知；公开 API 仅包含本包拥有的配置、结果和发送器。"""

from .models import NotificationAppearance, NotificationConfig, NotificationDelivery, NotificationResult
from .notifier import Notifier

__all__ = [
    "NotificationAppearance", "NotificationConfig", "NotificationDelivery", "NotificationResult", "Notifier",
]
