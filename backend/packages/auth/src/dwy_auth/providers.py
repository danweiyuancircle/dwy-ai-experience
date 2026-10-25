"""第三方适配只验证身份；绑定键使用配置名、已验证 issuer 和外部 subject。"""

from dataclasses import dataclass
from typing import Protocol

from .models import AuthError, GoogleVerifier


@dataclass(frozen=True)
class ExternalIdentity:
    """Provider 已完成验签后的身份；邮箱和姓名均不参与自动账号合并。"""

    issuer: str
    subject: str
    email: str | None = None
    display_name: str | None = None

    def __post_init__(self):
        """限定外部验证结果大小；字段仅作资料，不能据邮箱合并账号。"""
        if not isinstance(self.issuer, str) or not 1 <= len(self.issuer) <= 512:
            raise AuthError("EXTERNAL_IDENTITY_INVALID", "外部身份无效")
        if not isinstance(self.subject, str) or not 1 <= len(self.subject) <= 255:
            raise AuthError("EXTERNAL_IDENTITY_INVALID", "外部身份无效")
        if self.email is not None and (not isinstance(self.email, str) or len(self.email) > 254):
            raise AuthError("EXTERNAL_IDENTITY_INVALID", "外部身份无效")
        if self.display_name is not None and (
            not isinstance(self.display_name, str) or len(self.display_name) > 255
        ):
            raise AuthError("EXTERNAL_IDENTITY_INVALID", "外部身份无效")


class ExternalIdentityProvider(Protocol):
    """实现须验证签名、issuer、受众、时间及协议要求，不能信任请求自报身份。"""

    async def verify(self, credential: str) -> ExternalIdentity:
        """完成上游凭据验证后返回可信身份，失败须明确拒绝且不记录原文。"""
        ...


class GoogleIdentityProvider:
    """复用 Google 官方验证器；Google 的两种有效 issuer 归一为官方规范域。"""

    def __init__(self, verifier: GoogleVerifier):
        """注入官方验证器封装，不在适配器内建立第二套验签或账号关联逻辑。"""
        self.verifier = verifier

    async def verify(self, credential: str) -> ExternalIdentity:
        """底层只返回验证通过的 sub 及已验证邮箱。"""
        identity = await self.verifier.verify(credential)
        return ExternalIdentity(
            "https://accounts.google.com", identity.subject, identity.email, identity.display_name
        )

    async def aclose(self) -> None:
        """关闭本适配器拥有的验证器资源。"""
        closer = getattr(self.verifier, "aclose", None)
        if closer is not None:
            await closer()
