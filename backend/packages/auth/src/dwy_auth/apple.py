"""Apple 登录验证、授权码兑换与撤销；不管理应用挑战或业务会话。"""

import hmac
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import anyio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jose import JOSEError, jwt
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from .models import AuthError
from .providers import ExternalIdentity

_ISSUER = "https://appleid.apple.com"
_MAX_RESPONSE = 65536
_EVENTS = {"email-enabled", "email-disabled", "consent-revoked", "account-deleted"}
AppleRequest = Callable[[str, str, dict | None], Awaitable[dict]]


class AppleSignInConfig(BaseModel):
    """每应用单一 audience 与专用登录私钥；加密密钥供持久化服务使用。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    client_id: str = Field(min_length=1, max_length=255, pattern=r"^[A-Za-z0-9][A-Za-z0-9.-]*$")
    team_id: str = Field(pattern=r"^[A-Z0-9]{10}$")
    key_id: str = Field(pattern=r"^[A-Z0-9]{10}$")
    private_key: SecretStr = Field(repr=False)
    token_encryption_key: SecretStr = Field(repr=False)

    @field_validator("private_key")
    @classmethod
    def signing_key(cls, value: SecretStr) -> SecretStr:
        """仅接受 Apple 登录使用的 P-256 私钥，错误不能带出密钥。"""
        try:
            raw = value.get_secret_value()
            if not 1 <= len(raw) <= 16384:
                raise ValueError
            key = serialization.load_pem_private_key(raw.encode(), password=None)
            if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(key.curve, ec.SECP256R1):
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("Apple signing key is invalid") from None
        return value

    @field_validator("token_encryption_key")
    @classmethod
    def encryption_key(cls, value: SecretStr) -> SecretStr:
        """提前拒绝不可用的 Fernet key，避免兑换后才发现无法保存撤销材料。"""
        try:
            Fernet(value.get_secret_value().encode("ascii"))
        except (ValueError, UnicodeError):
            raise ValueError("Apple token encryption key is invalid") from None
        return value


@dataclass(frozen=True)
class AppleAuthorization:
    """已验证身份与服务端撤销材料；refresh token 不得返回客户端或日志。"""

    identity: ExternalIdentity
    refresh_token: str = field(repr=False)
    client_id: str


class AppleRevocationRequired(AuthError):
    """兑换失败且补偿撤销未完成；宿主必须加密持久化撤销材料后再返回错误。"""

    def __init__(self, refresh_token: str, client_id: str):
        """异常文字及 repr 不含令牌；仅服务端 outbox 可读取 SecretStr 原文。"""
        super().__init__("APPLE_REVOCATION_REQUIRED", "Apple 授权未完成，撤销待重试", 503)
        self.revocation_token = SecretStr(refresh_token)
        self.client_id = client_id


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class AppleGateway:
    """仅访问固定 Apple HTTPS 端点；实例应按应用复用以共享公钥缓存与并发预算。"""

    def __init__(self, config: AppleSignInConfig, *, request: AppleRequest | None = None, now=None):
        """传输注入仅用于可信宿主；默认阻塞网络在线程内执行且取消不释放活跃线程。"""
        self.config = config
        self._request = request
        self._now = now or time.time
        self._workers = anyio.Semaphore(4)
        self._keys_lock = anyio.Lock()
        self._keys: dict[str, dict] = {}
        self._keys_until = 0
        self._retry_after = 0

    async def authorize(
        self,
        identity_token: str,
        authorization_code: str,
        nonce: str,
        display_name: str | None = None,
    ) -> AppleAuthorization:
        """验签后兑换一次性 code；挑战一次性消费及中断恢复由宿主事务负责。"""
        self._text(authorization_code, 4096)
        self._text(nonce, 512)
        if display_name is not None and (not isinstance(display_name, str) or len(display_name) > 255):
            raise self._invalid()
        claims = await self._verify(identity_token)
        received_nonce = claims.get("nonce")
        if (
            not isinstance(received_nonce, str)
            or not received_nonce.isascii()
            or not nonce.isascii()
            or not hmac.compare_digest(received_nonce, nonce)
        ):
            raise self._invalid()
        identity = self._identity(claims, display_name)
        response = await self._send(
            "POST",
            "/auth/token",
            {
                "client_id": self.config.client_id,
                "client_secret": self._client_secret(),
                "code": authorization_code,
                "grant_type": "authorization_code",
            },
        )
        refresh = response.get("refresh_token")
        self._text(refresh, 16384)
        try:
            exchanged = await self._verify(response.get("id_token"))
            if exchanged.get("sub") != claims["sub"] or exchanged.get("nonce") != nonce:
                raise self._invalid()
        except BaseException:
            # 兑换已发生，拒绝登录或取消也必须撤销已取得的材料，失败交给宿主 outbox。
            with anyio.CancelScope(shield=True):
                try:
                    await self.revoke(refresh)
                except AuthError:
                    raise AppleRevocationRequired(refresh, self.config.client_id) from None
            raise
        return AppleAuthorization(identity, refresh, self.config.client_id)

    async def revoke(self, refresh_token: str, client_id: str | None = None) -> None:
        """撤销当前应用 refresh token；失败交由宿主持久化重试，不丢弃唯一材料。"""
        self._text(refresh_token, 16384)
        if client_id is not None and client_id != self.config.client_id:
            raise self._invalid()
        await self._send(
            "POST",
            "/auth/revoke",
            {
                "client_id": self.config.client_id,
                "client_secret": self._client_secret(),
                "token": refresh_token,
                "token_type_hint": "refresh_token",
            },
        )

    async def verify_notification(self, payload: str) -> dict:
        """验证账号变更通知并统一 events 为对象；jti 的持久化去重由宿主负责。"""
        claims = await self._verify(payload, notification=True)
        self._text(claims.get("jti"), 255)
        event = claims.get("events")
        if isinstance(event, str):
            try:
                event = json.loads(event)
            except (ValueError, RecursionError):
                raise self._invalid() from None
        if (
            not isinstance(event, dict)
            or not isinstance(event.get("type"), str)
            or event["type"] not in _EVENTS
        ):
            raise self._invalid()
        self._subject(event.get("sub"))
        timestamp = event.get("event_time")
        # Apple 历史通知有毫秒值；统一时间比较，不改变交给宿主的原始事件字段。
        if type(timestamp) is not int or timestamp <= 0:
            raise self._invalid()
        seconds = timestamp / 1000 if timestamp > 100_000_000_000 else timestamp
        if seconds > self._now() or seconds > claims["iat"] + 300:
            raise self._invalid()
        claims["events"] = event
        return claims

    async def _verify(self, token: str, *, notification: bool = False) -> dict:
        self._text(token, 16384)
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            self._text(kid, 255)
            if header.get("alg") != "RS256" or header.get("crit"):
                raise self._invalid()
            key = await self._key(kid)
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=_ISSUER,
                audience=self.config.client_id,
                options={"verify_exp": False, "verify_iat": False, "verify_at_hash": False},
            )
            now = self._now()
            issued, expires = claims.get("iat"), claims.get("exp")
            if claims.get("aud") != self.config.client_id or type(issued) is not int or not 0 < issued <= now:
                raise self._invalid()
            if "exp" in claims or not notification:
                if type(expires) is not int or expires <= now or expires <= issued:
                    raise self._invalid()
            if notification:
                if issued < now - 86400:
                    raise self._invalid()
            else:
                self._subject(claims.get("sub"))
            return claims
        except (JOSEError, ValueError, TypeError, KeyError, RecursionError):
            raise self._invalid() from None

    async def _key(self, kid: str) -> dict:
        async with self._keys_lock:
            now = self._now()
            if now < self._keys_until and kid in self._keys:
                return self._keys[kid]
            if now < self._retry_after:
                raise self._invalid()
            had_keys = bool(self._keys)
            self._retry_after = now + 30
            response = await self._send("GET", "/auth/keys", None)
            keys = response.get("keys")
            if not isinstance(keys, list) or not 1 <= len(keys) <= 16:
                raise self._invalid()
            parsed = {}
            for key in keys:
                if not isinstance(key, dict) or key.get("kty") != "RSA" or key.get("alg") != "RS256":
                    raise self._invalid()
                self._text(key.get("kid"), 255)
                if key.get("use") != "sig" or key["kid"] in parsed:
                    raise self._invalid()
                self._text(key.get("n"), 2048)
                self._text(key.get("e"), 16)
                parsed[key["kid"]] = key
            self._keys, self._keys_until = parsed, now + 3600
            if kid not in parsed:
                raise self._invalid()
            if not had_keys:
                self._retry_after = 0
            return parsed[kid]

    def _client_secret(self) -> str:
        now = int(self._now())
        try:
            return jwt.encode(
                {
                    "iss": self.config.team_id,
                    "iat": now,
                    "exp": now + 300,
                    "aud": _ISSUER,
                    "sub": self.config.client_id,
                },
                self.config.private_key.get_secret_value(),
                algorithm="ES256",
                headers={"kid": self.config.key_id},
            )
        except (JOSEError, ValueError, TypeError):
            raise AuthError("APPLE_UNAVAILABLE", "Apple 登录服务暂不可用", 503) from None

    async def _send(self, method: str, path: str, data: dict | None) -> dict:
        try:
            async with self._workers:
                with anyio.fail_after(8):
                    if self._request is not None:
                        response = await self._request(method, _ISSUER + path, data)
                    else:
                        response = await anyio.to_thread.run_sync(self._http, method, _ISSUER + path, data)
            if not isinstance(response, dict) or "error" in response:
                raise self._invalid()
            return response
        except AuthError:
            raise
        except Exception:
            # 传输是外部信任边界，不能把 HTTP、JSON 或自定义传输异常原文交给宿主日志。
            raise AuthError("APPLE_UNAVAILABLE", "Apple 登录服务暂不可用", 503) from None

    @staticmethod
    def _http(method: str, url: str, data: dict | None) -> dict:
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        request = urllib.request.Request(
            url, data=body, method=method, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            with urllib.request.build_opener(_NoRedirect()).open(request, timeout=5) as reply:
                raw = reply.read(_MAX_RESPONSE + 1)
            if len(raw) > _MAX_RESPONSE:
                raise ValueError
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            if error.code < 500 and error.code != 429:
                raise AppleGateway._invalid() from None
            raise AuthError("APPLE_UNAVAILABLE", "Apple 登录服务暂不可用", 503) from None

    @staticmethod
    def _invalid() -> AuthError:
        return AuthError("APPLE_TOKEN_INVALID", "Apple 凭据无效")

    @staticmethod
    def _text(value, maximum: int) -> None:
        if not isinstance(value, str) or not 1 <= len(value) <= maximum:
            raise AppleGateway._invalid()

    @staticmethod
    def _subject(value) -> None:
        AppleGateway._text(value, 255)
        if not re.fullmatch(r"[^\x00-\x20\x7f]+", value):
            raise AppleGateway._invalid()

    @staticmethod
    def _identity(claims: dict, display_name: str | None) -> ExternalIdentity:
        verified = claims.get("email_verified")
        email = claims.get("email") if verified is True or verified == "true" else None
        return ExternalIdentity(_ISSUER, claims["sub"], email, display_name)
