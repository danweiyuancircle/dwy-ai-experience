"""Resend 邮件事件的可覆盖通知展示预设。"""

from dwy_notify import NotificationAppearance

ASSET_BASE_URL = (
    "https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/"
    "091ad4fea18ed3840fec83dc833f18b759256ca7/backend/packages/webhooks/assets"
)
DEFAULT_APPEARANCE = NotificationAppearance(username="邮件通知", avatar_url=f"{ASSET_BASE_URL}/email.png")
