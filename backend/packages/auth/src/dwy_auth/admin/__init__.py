"""管理员 Cookie 认证入口，与 Google 用户会话独立。"""

from .config import AdminAuthConfig
from .http import AdminAuthBinding, install_admin_auth
from .service import COOKIE_NAME, AdminAuth, AdminSession

__all__ = [
    "COOKIE_NAME",
    "AdminAuth",
    "AdminAuthBinding",
    "AdminAuthConfig",
    "AdminSession",
    "install_admin_auth",
]
