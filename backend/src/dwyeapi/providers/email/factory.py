"""Email Provider 工厂 -- 根据配置选择实现。"""

from dwyeapi.providers.email.config import EmailSettings
from dwyeapi.providers.email.protocol import EmailProvider


def make_email_provider(settings: EmailSettings) -> EmailProvider:
    """根据 `settings.provider` 构造对应的 Email Provider 实例。

    Args:
        settings: Email 模块配置(项目 Settings 的嵌套字段)。

    Returns:
        实现了 `EmailProvider` Protocol 的实例。

    Raises:
        ValueError: 未知 provider 或必填配置缺失。
        ImportError: provider 对应的 extra 未安装。
    """
    common = {"code_ttl": settings.code_ttl, "code_length": settings.code_length}

    match settings.provider:
        case "mock":
            from dwyeapi.providers.email.mock import MockEmailProvider

            return MockEmailProvider(**common)

        case "resend":
            from dwyeapi.providers.email.resend import ResendEmailProvider

            if not settings.resend.api_key:
                raise ValueError("EMAIL__RESEND__API_KEY 未配置")
            return ResendEmailProvider(
                api_key=settings.resend.api_key,
                from_email=settings.resend.from_email,
                subject=settings.resend.subject,
                **common,
            )

        case "aliyun":
            from dwyeapi.providers.email.aliyun import AliyunEmailProvider

            if not settings.aliyun.access_key_id or not settings.aliyun.access_key_secret:
                raise ValueError("EMAIL__ALIYUN__ACCESS_KEY_ID/SECRET 未配置")
            return AliyunEmailProvider(
                access_key_id=settings.aliyun.access_key_id,
                access_key_secret=settings.aliyun.access_key_secret,
                account_name=settings.aliyun.account_name,
                from_alias=settings.aliyun.from_alias,
                subject=settings.aliyun.subject,
                **common,
            )

        case _:
            raise ValueError(f"未知 email provider: {settings.provider}")
