"""Email Provider 模块 -- 提供可插拔的邮件验证码发送能力。

模块由 Protocol 抽象 + 抽象基类 + 配置类 + 工厂函数 + 内置 resend 实现组成。
内置仅 resend 一种 provider;业务项目可通过 `register_email_provider` 注入自定义 provider
(继承 `EmailProviderBase` 实现 `_send`,即可复用 Redis 验证码 + 品牌化模板)。

典型用法 -- 内置 resend:
    from dwyeapi.providers.email import EmailSettings, make_email_provider

    class Settings(DwyBaseSettings):
        email: EmailSettings = EmailSettings()

    settings = Settings()
    provider = make_email_provider(settings.email)
    await provider.send_code("user@example.com")

典型用法 -- 注册自定义 provider:
    from dwyeapi.providers.email import (
        EmailProvider,
        EmailProviderBase,
        EmailSettings,
        register_email_provider,
    )

    class TencentSesProvider(EmailProviderBase):
        async def _send(self, target: str, code: str) -> bool:
            html = self._render_code_html(code)
            text = self._render_code_text(code)
            # 调腾讯云 SES API 发送 ...
            return True

    def _build(s: EmailSettings) -> EmailProvider:
        from app.config import settings as app_settings
        return TencentSesProvider(
            secret_id=app_settings.tencent.secret_id,
            code_ttl=s.code_ttl,
            brand_name=s.brand_name,
            ...,
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
