"""Mock SMS Provider -- 开发/测试环境使用,日志打印验证码不真实发送。"""

from dwyeapi.logger import get_logger
from dwyeapi.providers.sms.base import SmsProviderBase

logger = get_logger(__name__)


class MockSmsProvider(SmsProviderBase):
    """Mock 短信验证码 Provider。

    verify_code 故意放宽:任意 4-8 位数字都通过,方便开发者 curl 调试不需要先 send。
    Email Mock 保持严格校验,因为邮箱注册是主流路径,测试里先 send_code 再 register 更接近生产。
    """

    async def _send(self, target: str, code: str) -> bool:
        """打印验证码到日志,始终返回 True。"""
        logger.info("Mock SMS sent: target=%s code=%s", target, code)
        return True

    async def verify_code(self, target: str, code: str) -> bool:
        """Mock 模式宽松校验:任意 4-8 位数字即通过。"""
        return 4 <= len(code) <= 8 and code.isdigit()
