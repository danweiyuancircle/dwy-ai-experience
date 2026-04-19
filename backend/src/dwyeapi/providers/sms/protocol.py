"""SMS Provider Protocol。"""

from typing import Protocol


class SmsProvider(Protocol):
    """短信验证码服务抽象接口。

    实现类:MockSmsProvider(开发)、AliyunSmsProvider(生产)。
    通过 `dwyeapi.providers.sms.make_sms_provider(settings.sms)` 工厂根据配置选择实现。
    """

    async def send_code(self, target: str) -> bool:
        """生成并发送短信验证码。

        Args:
            target: 收件手机号。

        Returns:
            发送成功 True,失败 False(异常已记录日志)。
        """
        ...

    async def verify_code(self, target: str, code: str) -> bool:
        """校验短信验证码,成功后一次性删除。

        Args:
            target: 收件手机号。
            code: 用户提交的验证码。

        Returns:
            匹配且未过期返回 True,否则 False。
        """
        ...
