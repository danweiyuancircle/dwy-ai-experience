"""独立账户、官方 Google 验签、短期应用 access token 与轮换 refresh token。"""

from .email_auth import (
    EapiEmailCodeSender,
    EmailAuthConfig,
    EmailCodeChallenge,
    EmailCodeSender,
    SessionPolicy,
)
from .google import OfficialGoogleVerifier
from .http import install_auth_routes
from .models import (
    AccountDeletion,
    AuthError,
    DevicePage,
    DeviceQuery,
    DeviceSummary,
    GoogleConfig,
    GoogleIdentity,
    GoogleVerifier,
    TokenResponse,
    UserProfile,
)
from .service import AuthService
from .storage import AuthTables, build_auth_tables

__all__ = [
    "AccountDeletion",
    "AuthError",
    "EmailAuthConfig",
    "EapiEmailCodeSender",
    "EmailCodeSender",
    "EmailCodeChallenge",
    "SessionPolicy",
    "AuthService",
    "AuthTables",
    "DevicePage",
    "DeviceQuery",
    "DeviceSummary",
    "GoogleConfig",
    "GoogleIdentity",
    "GoogleVerifier",
    "OfficialGoogleVerifier",
    "TokenResponse",
    "UserProfile",
    "build_auth_tables",
    "install_auth_routes",
]
