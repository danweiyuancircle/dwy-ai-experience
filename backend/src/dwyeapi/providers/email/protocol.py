"""Email Provider Protocol。"""

from typing import Protocol


class EmailProvider(Protocol):
    """邮箱验证码服务抽象接口。

    内置与自定义走同一注册表;通过 `make_email_provider(settings.email)` 按名构造。
    业务可通过 `register_email_provider` 注入自定义实现,无需改 eapi。
    """

    async def send_code(self, target: str) -> bool:
        """生成并发送邮箱验证码。

        Args:
            target: 收件邮箱.发信用原地址;Redis key 走 ``canonicalize_email``.

        Returns:
            发送成功 True,失败 False(异常已记录日志)。
        """
        ...

    async def verify_code(self, target: str, code: str) -> bool:
        """校验邮箱验证码,成功后一次性删除。

        Args:
            target: 收件邮箱(Gmail 别名与发码时同一收件箱即可).
            code: 用户提交的验证码。

        Returns:
            匹配且未过期返回 True,否则 False。
        """
        ...
