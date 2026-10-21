"""Google 官方库验证签名、issuer、audience、时间；网络请求在有界线程中。"""

import asyncio

from pydantic import ValidationError

from .models import AuthError, GoogleConfig, GoogleIdentity


class OfficialGoogleVerifier:
    """只信任指定应用 audience 的 Google 签名，不按邮件地址关联账户。"""

    def __init__(self, config: GoogleConfig | None):
        """缺配置时显式关闭登录；每应用最多四个外部验签工作线程。"""
        self.config = config
        self._workers = asyncio.Semaphore(4)

    async def verify(self, id_token: str) -> GoogleIdentity:
        """网络工作移出事件循环，请求取消也不提前释放未结束的线程名额。"""
        if self.config is None:
            raise AuthError("GOOGLE_NOT_CONFIGURED", "Google 登录尚未配置", 503)
        if not isinstance(id_token, str) or not 1 <= len(id_token) <= 16384:
            raise AuthError("GOOGLE_TOKEN_INVALID", "Google 凭据无效")
        async with self._workers:
            task = asyncio.create_task(asyncio.to_thread(self._verify, id_token))
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                # 取消请求仍等待有界网络任务结束，避免释放名额后无限累积线程。
                try:
                    await asyncio.shield(task)
                except Exception:
                    pass
                raise

    def _verify(self, token: str) -> GoogleIdentity:
        """官方库完成密码学验证；对外只返回最小用户资料和稳定 subject。"""
        from google.auth import exceptions
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        from requests import Session

        class BoundedRequest(Request):
            """官方证书读取限制连接与读取超时，避免登录线程长期占用。"""

            def __call__(self, *args, **kwargs):
                """覆盖官方较长默认值，不允许调用方绕过当前网络预算。"""
                kwargs["timeout"] = (3, 5)
                return super().__call__(*args, **kwargs)

        try:
            with Session() as session:
                claims = id_token.verify_oauth2_token(
                    token,
                    BoundedRequest(session=session),
                    audience=self.config.client_id,
                    clock_skew_in_seconds=0,
                )
            # Official verifier validates aud/exp/iat/signature/issuer. Subject must exist as well.
            if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
                raise ValueError("issuer")
            return GoogleIdentity(
                subject=claims.get("sub"),
                email=claims.get("email") if claims.get("email_verified") is True else None,
                display_name=claims.get("name"),
            )
        except exceptions.TransportError:
            raise AuthError("GOOGLE_UNAVAILABLE", "Google 验证服务暂不可用", 503) from None
        except (ValueError, exceptions.GoogleAuthError, ValidationError):
            raise AuthError("GOOGLE_TOKEN_INVALID", "Google 凭据无效") from None

    async def aclose(self) -> None:
        """每次验证的 requests Session 都在工作线程内关闭。"""
