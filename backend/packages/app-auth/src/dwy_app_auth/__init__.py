"""独立认证核心；旧 EAPI 服务/HTTP 入口按需加载，不成为核心的反向依赖。"""

from importlib import import_module

from .contracts import AuthPrincipal, SessionBackend, SessionTokens, VerifiedIdentity
from .email_auth import (
    EapiEmailCodeSender,
    EmailAuthConfig,
    EmailCodeChallenge,
    EmailCodeSender,
    SessionPolicy,
)
from .google import OfficialGoogleVerifier
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
from .session_backend import JWTSessionBackend
from .session_storage import SessionTables, register_session_tables
from .storage import AuthTables, build_auth_tables

# 兼容旧消费者的显式导入；import dwy_app_auth 不隐式加载 EAPI/FastAPI。
_LAZY_EXPORTS = {
    "AuthService": (".service", "AuthService"),
    "install_auth_routes": (".http", "install_auth_routes"),
    "AuthRuntime": (".runtime", "AuthRuntime"),
    "RuntimeTables": (".runtime_storage", "RuntimeTables"),
    "build_runtime_tables": (".runtime_storage", "build_runtime_tables"),
    "SubjectAdapter": (".subjects", "SubjectAdapter"),
    "SubjectRegistration": (".subjects", "SubjectRegistration"),
    "ExternalIdentity": (".providers", "ExternalIdentity"),
    "ExternalIdentityProvider": (".providers", "ExternalIdentityProvider"),
    "GoogleIdentityProvider": (".providers", "GoogleIdentityProvider"),
}


def __getattr__(name: str):
    """保留既有入口；新 runtime 使用独立合同，不依赖旧业务用户表。"""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(name)
    module, attribute = target
    value = getattr(import_module(module, __name__), attribute)
    globals()[name] = value
    return value


__all__ = [
    "AuthPrincipal",
    "AuthRuntime",
    "ExternalIdentity",
    "ExternalIdentityProvider",
    "GoogleIdentityProvider",
    "JWTSessionBackend",
    "RuntimeTables",
    "SessionBackend",
    "SessionTables",
    "SessionTokens",
    "SubjectAdapter",
    "SubjectRegistration",
    "VerifiedIdentity",
    "build_runtime_tables",
    "register_session_tables",
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
