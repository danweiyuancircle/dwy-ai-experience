"""单进程管理员会话：随机 cookie、内存撤销和固定窗口限速。"""

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass

from .config import AdminAuthConfig

COOKIE_NAME = "app_cloud_admin"


@dataclass(frozen=True)
class AdminSession:
    """只保存服务端摘要与到期时间，应用 token 永远不参与验证。"""

    username: str
    expires_at: float


class AdminAuth:
    """最小单管理员认证；重启撤销全部会话，部署应使用单宿主 worker。"""

    def __init__(self, settings: AdminAuthConfig):
        """密码只在启动时经 PBKDF2 派生，后续常量时间比较派生值。"""
        self.username = settings.username
        self.lifetime = settings.session_seconds
        self.salt = secrets.token_bytes(32)
        self.password_hash = self._derive(settings.password.get_secret_value())
        self.sessions: dict[str, AdminSession] = {}
        self.attempts: dict[str, tuple[float, int]] = {}

    def _derive(self, password: str) -> bytes:
        """复用标准库 PBKDF2，保持密码验证成本固定。"""
        return hashlib.pbkdf2_hmac("sha256", password.encode(), self.salt, 600_000)

    def allow_attempt(self, address: str) -> bool:
        """每来源五分钟最多五次；不信任可伪造的代理头，且限制内存键数。"""
        now = time.monotonic()
        self.attempts = {key: value for key, value in self.attempts.items() if value[0] > now}
        expiry, count = self.attempts.get(address, (now + 300, 0))
        if count >= 5 or (address not in self.attempts and len(self.attempts) >= 2048):
            return False
        self.attempts[address] = (expiry, count + 1)
        return True

    def authenticate(self, username: str, password: str) -> bool:
        """用户名不存在时也执行同等密码派生，不向调用方区分失败原因。"""
        valid_password = hmac.compare_digest(self.password_hash, self._derive(password))
        return hmac.compare_digest(username.encode(), self.username.encode()) and valid_password

    def create_session(self) -> str:
        """原始随机 token 只交给 cookie；会话总数有上限，避免内存无限增长。"""
        now = time.monotonic()
        self.sessions = {key: value for key, value in self.sessions.items() if value.expires_at > now}
        if len(self.sessions) >= 1024:
            del self.sessions[next(iter(self.sessions))]
        token = secrets.token_urlsafe(32)
        self.sessions[self._digest(token)] = AdminSession(self.username, now + self.lifetime)
        return token

    @staticmethod
    def _digest(token: str) -> str:
        """服务端仅索引 cookie 摘要；不保存可重放的原始会话值。"""
        return hashlib.sha256(token.encode()).hexdigest()

    def resolve(self, token: str) -> AdminSession | None:
        """拒绝无界或错误格式 cookie；到期即删除对应服务端状态。"""
        if len(token) != 43 or not all(c.isascii() and (c.isalnum() or c in "-_") for c in token):
            return None
        key = self._digest(token)
        session = self.sessions.get(key)
        if session is not None and session.expires_at <= time.monotonic():
            del self.sessions[key]
            return None
        return session

    def revoke(self, token: str) -> None:
        """退出同时撤销服务端状态，复制过的 cookie 也立即失效。"""
        self.sessions.pop(self._digest(token), None)
