"""Email Provider 模块 -- 提供可插拔的邮件验证码发送能力。

模块由 Protocol 抽象 + 抽象基类 + 配置类 + 工厂函数 + 内置 resend 实现组成。
内置与自定义走同一注册表;`make_email_provider` 只按名查表。
业务可通过 `register_email_provider` 注入自定义 provider
(继承 `EmailProviderBase` 实现 `_send`,即可复用 Redis 验证码 + 品牌化模板,无需改 eapi)。

典型用法 -- 内置 resend:
    from dwyeapi.providers.email import EmailSettings, make_email_provider

    class Settings(DwyBaseSettings):
        email: EmailSettings = EmailSettings()

    settings = Settings()
    provider = make_email_provider(settings.email)
    await provider.send_code("user@qq.com", language="zh")

语言约定:
    language 由宿主将 Accept-Language 归一化为 zh / en 后逐次传入。
    未传语言时默认英文;英文主题通过 EMAIL__RESEND__SUBJECT_EN 配置。
    中文副标语/页脚不会自动用于英文邮件,可分别配置 EMAIL__BRAND_TAGLINE_EN /
    EMAIL__BRAND_SLOGAN_EN。品牌名、官网与客服邮箱保持原配置。
    自定义 provider 的 _send 必须接受 keyword-only language 并透传到模板。

典型用法 -- 注册自定义 provider:
    from dwyeapi.providers.email import (
        EmailProvider,
        EmailProviderBase,
        EmailSettings,
        register_email_provider,
    )

    class TencentSesProvider(EmailProviderBase):
        async def _send(self, target: str, code: str, *, language="en") -> bool:
            html = self._render_code_html(code, language=language)
            text = self._render_code_text(code, language=language)
            # 调腾讯云 SES API 发送 ...
            return True

    def _build(s: EmailSettings) -> EmailProvider:
        from app.config import settings as app_settings
        return TencentSesProvider(
            secret_id=app_settings.tencent.secret_id,
            code_ttl=s.code_ttl,
            brand_name=s.brand_name,
            require_common_domain=s.require_common_domain,
            extra_allow_domains=s.extra_allow_domain_list(),
            allow_edu=s.allow_edu,
            allow_edu_cn=s.allow_edu_cn,
        )

    register_email_provider("tencent_ses", _build)
    # .env: EMAIL__PROVIDER=tencent_ses
"""

from dwyeapi.providers.email.base import EmailProviderBase
from dwyeapi.providers.email.config import EmailSettings, ResendConfig
from dwyeapi.providers.email.factory import (
    EmailProviderFactory,
    make_email_provider,
    register_email_provider,
)
from dwyeapi.providers.email.protocol import EmailProvider

__all__ = [
    "EmailProvider",
    "EmailProviderBase",
    "EmailProviderFactory",
    "EmailSettings",
    "ResendConfig",
    "make_email_provider",
    "register_email_provider",
]
