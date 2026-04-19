"""SMS Provider 模块 -- 提供可插拔的短信验证码发送能力。

提供 Protocol 抽象 + 配置类 + 工厂函数 + 多种实现(mock/aliyun)。
业务项目通过 `pip install dwyeapi[sms-aliyun]` 等 extras 按需安装 provider 依赖。

典型用法:
    from dwyeapi.providers.sms import SmsSettings, make_sms_provider

    class Settings(DwyBaseSettings):
        sms: SmsSettings = SmsSettings()

    settings = Settings()
    provider = make_sms_provider(settings.sms)
    await provider.send_code("13800138000")
"""

from dwyeapi.providers.sms.base import SmsProviderBase
from dwyeapi.providers.sms.config import AliyunSmsConfig, SmsSettings
from dwyeapi.providers.sms.factory import make_sms_provider
from dwyeapi.providers.sms.protocol import SmsProvider

__all__ = [
    "AliyunSmsConfig",
    "SmsProvider",
    "SmsProviderBase",
    "SmsSettings",
    "make_sms_provider",
]
