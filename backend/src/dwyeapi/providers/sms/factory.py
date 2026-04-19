"""SMS Provider 工厂 -- 根据配置选择实现。"""

from dwyeapi.providers.sms.config import SmsSettings
from dwyeapi.providers.sms.protocol import SmsProvider


def make_sms_provider(settings: SmsSettings) -> SmsProvider:
    """根据 `settings.provider` 构造对应的 SMS Provider 实例。

    Args:
        settings: SMS 模块配置(项目 Settings 的嵌套字段)。

    Returns:
        实现了 `SmsProvider` Protocol 的实例。

    Raises:
        ValueError: 未知 provider 或必填配置缺失。
        ImportError: provider 对应的 extra 未安装。
    """
    common = {"code_ttl": settings.code_ttl, "code_length": settings.code_length}

    match settings.provider:
        case "mock":
            from dwyeapi.providers.sms.mock import MockSmsProvider

            return MockSmsProvider(**common)

        case "aliyun":
            from dwyeapi.providers.sms.aliyun import AliyunSmsProvider

            if not settings.aliyun.access_key_id or not settings.aliyun.access_key_secret:
                raise ValueError("SMS__ALIYUN__ACCESS_KEY_ID/SECRET 未配置")
            return AliyunSmsProvider(
                access_key_id=settings.aliyun.access_key_id,
                access_key_secret=settings.aliyun.access_key_secret,
                sign_name=settings.aliyun.sign_name,
                template_code=settings.aliyun.template_code,
                region_id=settings.aliyun.region_id,
                **common,
            )

        case _:
            raise ValueError(f"未知 sms provider: {settings.provider}")
