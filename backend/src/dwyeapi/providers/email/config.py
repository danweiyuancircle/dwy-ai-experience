"""Email Provider 配置模型。"""

from pydantic import BaseModel, Field, field_validator


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
        EMAIL__REQUIRE_COMMON_DOMAIN=true
        EMAIL__EXTRA_ALLOW_DOMAINS=chances.com.cn
        EMAIL__ALLOW_EDU=true
        EMAIL__ALLOW_EDU_CN=true
        EMAIL__BRAND_NAME=宽舟科技
        EMAIL__BRAND_URL=https://example.com
        EMAIL__SUPPORT_EMAIL=support@example.com
        EMAIL__RESEND__API_KEY=re_xxx
    """

    provider: str = Field(
        default="resend",
        description=(
            "Email Provider 名称。内置见工厂注册表(当前 resend);"
            "自定义先 register_email_provider(name, factory) 再填对应名称"
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
    require_common_domain: bool = Field(
        default=True,
        description="发码前校验常见个人邮箱域名.C 端保持 True;B2B 可关",
    )
    extra_allow_domains: str = Field(
        default="",
        max_length=2000,
        description="逗号分隔的额外放行域名,企业 / 机构邮箱用.示例:chances.com.cn",
    )
    allow_edu: bool = Field(
        default=True,
        description="是否放行美国 .edu TLD.默认 True.不放行 edu.kg 等国家教育后缀",
    )
    allow_edu_cn: bool = Field(
        default=True,
        description="是否放行 edu.cn / *.edu.cn.默认 True",
    )
    resend: ResendConfig = Field(
        default_factory=ResendConfig,
        description="Resend 配置,provider=resend 时必填",
    )

    def extra_allow_domain_list(self) -> tuple[str, ...]:
        """把 ``extra_allow_domains`` 折成去空白的域名元组.

        Returns:
            tuple[str, ...]: 额外放行域名.空配置为 ``()``.示例:``("chances.com.cn",)``.
        """
        return tuple(part.strip() for part in self.extra_allow_domains.split(",") if part.strip())

    @field_validator("extra_allow_domains")
    @classmethod
    def extra_allow_domains_must_be_domains(cls, value: str) -> str:
        """拒绝过长单段,防止把整段正文塞进配置.

        Args:
            value (str): 原始配置串.长度 ``[0, 2000]``.示例:``chances.com.cn``.

        Returns:
            str: 原样返回(已由 Field max_length 限长).

        Raises:
            ValueError: 单段超过 253 字符(DNS 域名上限).
        """
        for part in value.split(","):
            item = part.strip()
            if len(item) > 253:
                raise ValueError("extra_allow_domains 单段超过 253 字符")
        return value
