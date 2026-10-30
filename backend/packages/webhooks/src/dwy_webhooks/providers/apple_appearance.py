"""Apple 购买模块的展示预设，应用配置可按字段覆盖。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(username="购买通知", avatar_url=f"{ASSET_BASE_URL}/purchase.png")
