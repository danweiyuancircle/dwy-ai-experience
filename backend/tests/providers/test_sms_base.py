"""Tests for dwyeapi.providers.sms.base(验证码存取 + 一次性校验)。

注:`MockSmsProvider.verify_code` 故意重写为宽松校验(任意 4-8 位数字通过),
用来方便 curl 调试,不代表基类行为。本文件要验证基类 `SmsProviderBase`
的严格一次性校验,所以用本地 `_StrictSmsProvider` 继承基类但不重写 verify_code。
"""

from dwyeapi.providers.sms.base import CODE_KEY_PREFIX, SmsProviderBase
from dwyeapi.providers.sms.mock import MockSmsProvider


class _StrictSmsProvider(SmsProviderBase):
    """仅用于测试:继承基类但不重写 verify_code,暴露严格的一次性校验语义。"""

    async def _send(self, target: str, code: str) -> bool:
        return True


class TestSmsProviderBase:
    async def test_send_code_stores_in_redis(self, fake_redis):
        provider = MockSmsProvider(redis=fake_redis)
        ok = await provider.send_code("13800138000")
        assert ok is True

        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}13800138000")
        assert stored is not None
        assert len(stored) == 6
        assert stored.isdigit()

    async def test_verify_code_success_deletes_key(self, fake_redis):
        provider = _StrictSmsProvider(redis=fake_redis)
        await provider.send_code("13800138000")
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}13800138000")

        assert await provider.verify_code("13800138000", stored) is True
        assert await provider.verify_code("13800138000", stored) is False

    async def test_verify_code_wrong_code_keeps_key(self, fake_redis):
        provider = _StrictSmsProvider(redis=fake_redis)
        await provider.send_code("13800138000")

        assert await provider.verify_code("13800138000", "000000") is False
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}13800138000")
        assert stored is not None

    async def test_email_and_sms_use_different_key_prefix(self, fake_redis):
        """email 和 sms 使用独立的 key 前缀,同一 target 不会互相污染。"""
        from dwyeapi.providers.email.mock import MockEmailProvider

        email_provider = MockEmailProvider(redis=fake_redis)
        sms_provider = MockSmsProvider(redis=fake_redis)

        await email_provider.send_code("alice")
        await sms_provider.send_code("alice")

        email_keys = await fake_redis.keys("dwyeapi:email:code:*")
        sms_keys = await fake_redis.keys("dwyeapi:sms:code:*")
        assert len(email_keys) == 1
        assert len(sms_keys) == 1
