"""阿里云短信 Provider -- 占位实现。

需要 `pip install dwyeapi[sms-aliyun]` 才能使用。实际调用待首次接入项目时补全。
"""

import redis.asyncio as aioredis

from dwyeapi.providers.sms.base import DEFAULT_CODE_LENGTH, DEFAULT_CODE_TTL, SmsProviderBase


class AliyunSmsProvider(SmsProviderBase):
    """基于阿里云 dysmsapi 的 SMS Provider(占位)。

    首次接入项目时基于 `alibabacloud_dysmsapi20170525` SDK 实现 `_send()`。
    """

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        sign_name: str,
        template_code: str,
        region_id: str = "cn-hangzhou",
        code_ttl: int = DEFAULT_CODE_TTL,
        code_length: int = DEFAULT_CODE_LENGTH,
        redis: aioredis.Redis | None = None,
    ) -> None:
        """初始化。

        Raises:
            ImportError: 未安装 alibabacloud_dysmsapi20170525 时抛出。
        """
        super().__init__(code_ttl=code_ttl, code_length=code_length, redis=redis)
        try:
            import alibabacloud_dysmsapi20170525  # noqa: F401
        except ImportError as e:
            raise ImportError("使用 AliyunSmsProvider 需要安装: pip install dwyeapi[sms-aliyun]") from e
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._sign_name = sign_name
        self._template_code = template_code
        self._region_id = region_id

    async def _send(self, target: str, code: str) -> bool:
        """调用阿里云短信 API 发送验证码。"""
        raise NotImplementedError("AliyunSmsProvider 暂未实现,首次接入项目时补全 _send")
