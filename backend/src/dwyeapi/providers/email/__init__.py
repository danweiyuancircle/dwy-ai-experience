"""Email Provider 模块 -- 提供可插拔的邮件验证码发送能力。

提供 Protocol 抽象 + 配置类 + 工厂函数 + 多种实现(mock/resend/aliyun)。
业务项目通过 `pip install dwyeapi[email-resend]` 等 extras 按需安装 provider 依赖。

典型用法:
    from dwyeapi.providers.email import EmailSettings, make_email_provider

    class Settings(DwyBaseSettings):
        email: EmailSettings = EmailSettings()

    settings = Settings()
    provider = make_email_provider(settings.email)
    await provider.send_code("user@example.com")
"""

from dwyeapi.providers.email.base import EmailProviderBase
from dwyeapi.providers.email.config import AliyunEmailConfig, EmailSettings, ResendConfig
from dwyeapi.providers.email.factory import make_email_provider
from dwyeapi.providers.email.protocol import EmailProvider

__all__ = [
    "AliyunEmailConfig",
    "EmailProvider",
    "EmailProviderBase",
    "EmailSettings",
    "ResendConfig",
    "make_email_provider",
]
