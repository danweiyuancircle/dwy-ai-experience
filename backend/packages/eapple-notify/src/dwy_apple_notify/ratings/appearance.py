"""每日评分日报的默认展示；宿主和单次调用仍可覆盖。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(username="评分日报", avatar_url=f"{ASSET_BASE_URL}/report.png")
