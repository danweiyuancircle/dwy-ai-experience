"""Email Provider 配置模型。"""

from typing import Literal

from pydantic import BaseModel


class ResendConfig(BaseModel):
    """Resend Email Provider 配置。"""

    api_key: str = ""
    from_email: str = "noreply@example.com"
    subject: str = "验证码"


class AliyunEmailConfig(BaseModel):
    """阿里云邮件推送 Provider 配置。"""

    access_key_id: str = ""
    access_key_secret: str = ""
    account_name: str = ""
    from_alias: str = ""
    subject: str = "验证码"


class EmailSettings(BaseModel):
    """Email 模块配置 -- 业务项目嵌入 Settings 的入口。

    用法:
        class Settings(DwyBaseSettings):
            email: EmailSettings = EmailSettings()

    `.env` 自动识别(双下划线嵌套):
        EMAIL__PROVIDER=resend
        EMAIL__RESEND__API_KEY=re_xxx
    """

    provider: Literal["mock", "resend", "aliyun"] = "mock"
    code_ttl: int = 300
    code_length: int = 6
    resend: ResendConfig = ResendConfig()
    aliyun: AliyunEmailConfig = AliyunEmailConfig()
