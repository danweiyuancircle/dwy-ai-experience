"""按已验证来源选择模块预设；基础通知包不承担业务分类。"""

from dwy_notify import NotificationAppearance

from ._assets import ASSET_BASE_URL
from .analytics.appearance import DEFAULT_APPEARANCE as ANALYTICS_APPEARANCE
from .providers.apple_appearance import DEFAULT_APPEARANCE as APPLE_APPEARANCE
from .providers.asc_appearance import DEFAULT_APPEARANCE as ASC_APPEARANCE
from .providers.resend_appearance import DEFAULT_APPEARANCE as RESEND_APPEARANCE

DEFAULT_APPEARANCE = NotificationAppearance(username="系统通知", avatar_url=f"{ASSET_BASE_URL}/general.png")
_PRESETS = {
    "apple_notifications": APPLE_APPEARANCE,
    "app_store_connect": ASC_APPEARANCE,
    "app_store_analytics": ANALYTICS_APPEARANCE,
    "resend": RESEND_APPEARANCE,
}


def notification_appearance(source: str) -> NotificationAppearance:
    """供直接转发及宿主自有队列使用；未专设展示的来源共用系统通知。"""
    return _PRESETS.get(source, DEFAULT_APPEARANCE)
