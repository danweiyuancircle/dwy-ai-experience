"""独立多目标通知；公开 API 仅包含本包拥有的配置、结果和发送器。"""

from .models import NotificationConfig, NotificationDelivery, NotificationResult
from .notifier import Notifier

__all__ = ["NotificationConfig", "NotificationDelivery", "NotificationResult", "Notifier"]
