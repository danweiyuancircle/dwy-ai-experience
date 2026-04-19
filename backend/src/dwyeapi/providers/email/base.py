"""Email Provider 基类 -- 封装 Redis 验证码存取逻辑。"""

import secrets
from abc import ABC, abstractmethod

import redis.asyncio as aioredis

from dwyeapi.cache import get_redis

CODE_KEY_PREFIX = "dwyeapi:email:code:"
DEFAULT_CODE_TTL = 300
DEFAULT_CODE_LENGTH = 6


class EmailProviderBase(ABC):
    """Email Provider 抽象基类。

    共享验证码生成 + Redis 存取 + 一次性校验逻辑;子类只实现 `_send()` 发送动作。
    """

    def __init__(
        self,
        code_ttl: int = DEFAULT_CODE_TTL,
        code_length: int = DEFAULT_CODE_LENGTH,
        redis: aioredis.Redis | None = None,
    ) -> None:
        """初始化。

        Args:
            code_ttl: 验证码有效期(秒),默认 300。
            code_length: 验证码位数,默认 6。
            redis: 可选显式注入的 Redis 连接;为 None 时 fallback 到 dwyeapi.cache.get_redis()。
        """
        self._ttl = code_ttl
        self._length = code_length
        self._redis = redis

    async def _get_redis(self) -> aioredis.Redis:
        """获取 Redis 连接,优先使用注入的,否则取全局单例。"""
        if self._redis is not None:
            return self._redis
        return await get_redis()

    def _generate_code(self) -> str:
        """生成指定位数的数字验证码。"""
        return "".join(secrets.choice("0123456789") for _ in range(self._length))

    async def send_code(self, target: str) -> bool:
        """生成验证码存 Redis 并调用 `_send()` 发送。"""
        code = self._generate_code()
        redis = await self._get_redis()
        await redis.set(f"{CODE_KEY_PREFIX}{target}", code, ex=self._ttl)
        return await self._send(target, code)

    async def verify_code(self, target: str, code: str) -> bool:
        """从 Redis 读取存储的验证码比对,成功则删除 key(一次性)。"""
        redis = await self._get_redis()
        key = f"{CODE_KEY_PREFIX}{target}"
        stored = await redis.get(key)
        if stored is None:
            return False
        stored_str = stored if isinstance(stored, str) else stored.decode()
        if stored_str != code:
            return False
        await redis.delete(key)
        return True

    @abstractmethod
    async def _send(self, target: str, code: str) -> bool:
        """子类实现发送动作。"""
        ...
