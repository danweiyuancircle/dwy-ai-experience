"""评论提醒沿用系统通知；应用与单次调用仍可覆盖名称和头像。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(username="系统通知", avatar_url=f"{ASSET_BASE_URL}/general.png")
