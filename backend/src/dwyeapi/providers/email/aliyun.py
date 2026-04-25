"""阿里云邮件推送 Email Provider -- 占位实现。

需要 `pip install dwyeapi[email-aliyun]` 才能使用。实际调用待首次接入项目时补全。
"""

import redis.asyncio as aioredis

from dwyeapi.providers.email.base import DEFAULT_CODE_LENGTH, DEFAULT_CODE_TTL, EmailProviderBase


class AliyunEmailProvider(EmailProviderBase):
    """基于阿里云邮件推送的 Email Provider(占位)。

    首次接入项目时基于 `alibabacloud_dm20151123` SDK 实现 `_send()`,
    调用时使用 `self._render_code_html(code)` / `self._render_code_text(code)` 复用品牌模板。
    """

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        account_name: str,
        from_alias: str = "",
        subject: str = "验证码",
        code_ttl: int = DEFAULT_CODE_TTL,
        code_length: int = DEFAULT_CODE_LENGTH,
        brand_name: str = "",
        brand_tagline: str = "",
        brand_url: str = "",
        brand_slogan: str = "",
        support_email: str = "",
        redis: aioredis.Redis | None = None,
    ) -> None:
        """初始化。

        Raises:
            ImportError: 未安装 alibabacloud_dm20151123 时抛出。
        """
        super().__init__(
            code_ttl=code_ttl,
            code_length=code_length,
            brand_name=brand_name,
            brand_tagline=brand_tagline,
            brand_url=brand_url,
            brand_slogan=brand_slogan,
            support_email=support_email,
            redis=redis,
        )
        try:
            import alibabacloud_dm20151123  # noqa: F401
        except ImportError as e:
            raise ImportError("使用 AliyunEmailProvider 需要安装: pip install dwyeapi[email-aliyun]") from e
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._account_name = account_name
        self._from_alias = from_alias or brand_name
        self._subject = subject

    async def _send(self, target: str, code: str) -> bool:
        """调用阿里云 DirectMail API 发送邮件。"""
        raise NotImplementedError("AliyunEmailProvider 暂未实现,首次接入项目时补全 _send")
