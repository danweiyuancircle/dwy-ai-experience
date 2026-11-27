"""经营日报和周报共用的展示预设。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(username="经营报表", avatar_url=f"{ASSET_BASE_URL}/report.png")
