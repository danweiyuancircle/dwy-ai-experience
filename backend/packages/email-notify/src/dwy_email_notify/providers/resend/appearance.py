"""Resend 邮件事件的可覆盖通知展示预设。"""

from dwy_notify import NotificationAppearance

ASSET_BASE_URL = (
    "https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/"
    "8c86735ec6bcfeee24f101fdccbc900b9d7bc2dd/assets/notification-icons"
)
DEFAULT_APPEARANCE = NotificationAppearance(username="邮件通知", avatar_url=f"{ASSET_BASE_URL}/email.png")
