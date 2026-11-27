"""Resend 邮件事件模块的展示预设。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL

DEFAULT_APPEARANCE = NotificationAppearance(username="邮件通知", avatar_url=f"{ASSET_BASE_URL}/email.png")
