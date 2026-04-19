"""Mock Email Provider -- 开发/测试环境使用,日志打印验证码不真实发送。"""

from dwyeapi.logger import get_logger
from dwyeapi.providers.email.base import EmailProviderBase

logger = get_logger(__name__)


class MockEmailProvider(EmailProviderBase):
    """Mock 邮箱验证码 Provider。"""

    async def _send(self, target: str, code: str) -> bool:
        """打印验证码到日志,始终返回 True。"""
        logger.info("Mock Email sent: target=%s code=%s", target, code)
        return True
