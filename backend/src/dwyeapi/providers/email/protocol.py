"""Email Provider Protocol。"""

from typing import Protocol


class EmailProvider(Protocol):
    """邮箱验证码服务抽象接口。

    实现类:MockEmailProvider(开发)、ResendEmailProvider(生产)、AliyunEmailProvider(生产备选)。
    通过 `dwyeapi.providers.email.make_email_provider(settings.email)` 工厂根据配置选择实现。
    """

    async def send_code(self, target: str) -> bool:
        """生成并发送邮箱验证码。

        Args:
            target: 收件邮箱。

        Returns:
            发送成功 True,失败 False(异常已记录日志)。
        """
        ...

    async def verify_code(self, target: str, code: str) -> bool:
        """校验邮箱验证码,成功后一次性删除。

        Args:
            target: 收件邮箱。
            code: 用户提交的验证码。

        Returns:
            匹配且未过期返回 True,否则 False。
        """
        ...
