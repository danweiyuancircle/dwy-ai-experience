"""SMS Provider 配置模型。"""

from typing import Literal

from pydantic import BaseModel, Field


class AliyunSmsConfig(BaseModel):
    """阿里云短信 Provider 配置。

    SMS__PROVIDER=aliyun 时生效;空串默认仅为 pydantic 嵌套实例化需要,
    provider=mock 场景下不会读取,真正启用时四项凭证必须通过 .env 显式提供。
    """

    access_key_id: str = Field(
        default="",
        description="[必填: aliyun] 阿里云 AccessKey ID",
    )
    access_key_secret: str = Field(
        default="",
        description="[必填: aliyun] 阿里云 AccessKey Secret",
    )
    sign_name: str = Field(
        default="",
        description="[必填: aliyun] 短信签名(需在阿里云控制台预先申请)",
    )
    template_code: str = Field(
        default="",
        description="[必填: aliyun] 短信模板 code,例 SMS_123456789",
    )
    region_id: str = Field(
        default="cn-hangzhou",
        description="阿里云地域 ID,默认 cn-hangzhou",
    )


class SmsSettings(BaseModel):
    """SMS 模块配置 -- 业务项目嵌入 Settings 的入口。

    用法:
        class Settings(DwyBaseSettings):
            sms: SmsSettings = SmsSettings()

    `.env` 自动识别(双下划线嵌套):
        SMS__PROVIDER=aliyun
        SMS__ALIYUN__ACCESS_KEY_ID=LTAI...
    """

    provider: Literal["mock", "aliyun"] = Field(
        default="mock",
        description='SMS Provider 选择:"mock"(dev 限定,打印到日志)/ "aliyun"(生产)',
    )
    code_ttl: int = Field(
        default=300,
        description="验证码有效期(秒),默认 5 分钟",
    )
    code_length: int = Field(
        default=6,
        description="验证码位数,默认 6 位数字",
    )
    aliyun: AliyunSmsConfig = Field(
        default_factory=AliyunSmsConfig,
        description="阿里云短信凭证,provider=aliyun 时必填",
    )
