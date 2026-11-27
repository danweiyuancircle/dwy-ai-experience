"""App Store Connect 审核模块的展示预设。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(
    username="应用审核通知", avatar_url=f"{ASSET_BASE_URL}/review.png",
)
