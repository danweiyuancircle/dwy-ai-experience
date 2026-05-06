"""Email Provider 配置模型。"""

from pydantic import BaseModel, Field


class ResendConfig(BaseModel):
    """Resend Email Provider 配置。

    EMAIL__PROVIDER=resend 时生效;空串默认仅为 pydantic 嵌套实例化需要,
    真正启用时 api_key / from_email 必须通过 .env 显式提供。
    """

    api_key: str = Field(
        default="",
        description="[必填: resend] Resend API Key,形如 re_xxx",
    )
    from_email: str = Field(
        default="",
        description="[必填: resend] 发件人邮箱,必须是已在 Resend 验证过的域名邮箱",
    )
    subject: str = Field(
        default="验证码",
        description="验证码邮件主题",
    )


class EmailSettings(BaseModel):
    """Email 模块配置 -- 业务项目嵌入 Settings 的入口。

    用法:
        class Settings(DwyBaseSettings):
            email: EmailSettings = EmailSettings()

    `.env` 自动识别(双下划线嵌套):
        EMAIL__PROVIDER=resend
        EMAIL__BRAND_NAME=宽舟科技
        EMAIL__BRAND_URL=https://quantzone.tech
        EMAIL__SUPPORT_EMAIL=support@quantzone.tech
        EMAIL__RESEND__API_KEY=re_xxx
    """

    provider: str = Field(
        default="resend",
        description=(
            "Email Provider 名称。内置仅支持 'resend';"
            "业务可通过 register_email_provider(name, factory) 注册自定义 provider 后填入对应名称"
        ),
    )
    code_ttl: int = Field(
        default=300,
        description="验证码有效期(秒),默认 5 分钟",
    )
    code_length: int = Field(
        default=6,
        description="验证码位数,默认 6 位数字",
    )
    brand_name: str = Field(
        default="",
        description="品牌名,展示在邮件页眉与页脚版权,留空则使用通用模板",
    )
    brand_tagline: str = Field(
        default="",
        description="品牌副标语(英文/口号),展示在页眉右上,留空则不显示",
    )
    brand_url: str = Field(
        default="",
        description="品牌官网,展示在页脚链接,留空则不显示",
    )
    brand_slogan: str = Field(
        default="",
        description="页脚版权下方一行说明文案,留空则不显示",
    )
    support_email: str = Field(
        default="",
        description="客服邮箱,展示在邮件正文底部,留空则不显示",
    )
    resend: ResendConfig = Field(
        default_factory=ResendConfig,
        description="Resend 配置,provider=resend 时必填",
    )
