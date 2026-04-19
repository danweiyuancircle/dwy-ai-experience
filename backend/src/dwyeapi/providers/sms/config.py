"""SMS Provider 配置模型。"""

from typing import Literal

from pydantic import BaseModel


class AliyunSmsConfig(BaseModel):
    """阿里云短信 Provider 配置。"""

    access_key_id: str = ""
    access_key_secret: str = ""
    sign_name: str = ""
    template_code: str = ""
    region_id: str = "cn-hangzhou"


class SmsSettings(BaseModel):
    """SMS 模块配置 -- 业务项目嵌入 Settings 的入口。

    用法:
        class Settings(DwyBaseSettings):
            sms: SmsSettings = SmsSettings()

    `.env` 自动识别(双下划线嵌套):
        SMS__PROVIDER=aliyun
        SMS__ALIYUN__ACCESS_KEY_ID=LTAI...
    """

    provider: Literal["mock", "aliyun"] = "mock"
    code_ttl: int = 300
    code_length: int = 6
    aliyun: AliyunSmsConfig = AliyunSmsConfig()
