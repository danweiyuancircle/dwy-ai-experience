"""Resend Email Provider -- 基于 resend-python SDK 的 async API。

需要 `pip install dwyeapi[email-resend]` 才能使用。
"""

import redis.asyncio as aioredis

from dwyeapi.logger import get_logger
from dwyeapi.providers.email.base import DEFAULT_CODE_LENGTH, DEFAULT_CODE_TTL, EmailProviderBase

logger = get_logger(__name__)


class ResendEmailProvider(EmailProviderBase):
    """基于 Resend SDK 的 Email Provider。

    使用 `resend.Emails.send_async` 原生 async API,底层 httpx 不阻塞事件循环。
    resend SDK 的 api_key 存在模块全局变量上,多实例会相互覆盖;装配层只实例化一次,不存在竞争。
    """

    def __init__(
        self,
        api_key: str,
        from_email: str,
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
        """初始化 Resend Provider。

        Args:
            api_key: Resend 控制台颁发的 API Key。
            from_email: 发件邮箱(必须使用 Resend 已验证的域名)。
            subject: 邮件主题。
            code_ttl: 验证码有效期(秒)。
            code_length: 验证码位数。
            brand_name: 品牌名,影响发件人显示名("brand_name <from_email>")与 HTML/text 模板。
            brand_tagline: 品牌副标语。
            brand_url: 品牌官网。
            brand_slogan: 页脚说明。
            support_email: 客服邮箱。
            redis: 可选显式注入的 Redis 连接。

        Raises:
            ImportError: 未安装 resend 包时抛出,提示用户安装对应 extra。
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
            import resend
        except ImportError as e:
            raise ImportError("使用 ResendEmailProvider 需要安装: pip install dwyeapi[email-resend]") from e
        resend.api_key = api_key
        self._resend = resend
        self._from = f"{brand_name} <{from_email}>" if brand_name else from_email
        self._subject = subject

    async def _send(self, target: str, code: str) -> bool:
        """调用 Resend API 发送邮件 -- 同时附 HTML 与 text,优化反垃圾评分。"""
        params = {
            "from": self._from,
            "to": [target],
            "subject": self._subject,
            "html": self._render_code_html(code),
            "text": self._render_code_text(code),
        }
        try:
            resp = await self._resend.Emails.send_async(params)
            logger.info("Resend email sent: target=%s message_id=%s", target, resp.get("id"))
            return True
        except Exception as e:
            logger.error("Resend email failed: target=%s error=%s", target, e)
            return False
