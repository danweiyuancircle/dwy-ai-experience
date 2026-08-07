"""Tests for dwyeapi.providers.email.base(验证码存取 + 一次性校验)。"""

from dwyeapi.providers.email.base import CODE_KEY_PREFIX, EmailProviderBase


class FakeEmailProvider(EmailProviderBase):
    """测试专用 -- 不实际发送邮件,只返回 True 让基类逻辑跑完。"""

    async def _send(self, target: str, code: str) -> bool:
        return True


class TestEmailProviderBase:
    async def test_send_code_stores_in_redis(self, fake_redis):
        provider = FakeEmailProvider(code_ttl=60, redis=fake_redis)
        ok = await provider.send_code("alice@example.com")
        assert ok is True

        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com")
        assert stored is not None
        assert len(stored) == 6
        assert stored.isdigit()

    async def test_send_code_respects_ttl(self, fake_redis):
        provider = FakeEmailProvider(code_ttl=120, redis=fake_redis)
        await provider.send_code("alice@example.com")
        ttl = await fake_redis.ttl(f"{CODE_KEY_PREFIX}alice@example.com")
        assert 0 < ttl <= 120

    async def test_send_code_respects_length(self, fake_redis):
        provider = FakeEmailProvider(code_length=4, redis=fake_redis)
        await provider.send_code("alice@example.com")
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com")
        assert len(stored) == 4

    async def test_verify_code_success_deletes_key(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        await provider.send_code("alice@example.com")
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com")

        assert await provider.verify_code("alice@example.com", stored) is True
        # 成功后 key 被删除,再次校验失败
        assert await provider.verify_code("alice@example.com", stored) is False

    async def test_verify_code_wrong_code_keeps_key(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        await provider.send_code("alice@example.com")

        assert await provider.verify_code("alice@example.com", "000000") is False
        # 错误的 code 不删除 key,正确的 code 仍可用
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com")
        assert stored is not None
        assert await provider.verify_code("alice@example.com", stored) is True

    async def test_verify_code_unknown_target_returns_false(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        assert await provider.verify_code("unknown@example.com", "123456") is False

    async def test_code_is_random(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        codes = set()
        for i in range(20):
            await provider.send_code(f"alice{i}@example.com")
            stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice{i}@example.com")
            codes.add(stored)
        # 20 次生成至少 10 个不同的码(低冲突)
        assert len(codes) > 10

    async def test_send_code_failure_does_not_store_key(self, fake_redis):
        """_send 失败时不应写入 Redis，避免用户未收到邮件却有可校验码。"""

        class FailingProvider(EmailProviderBase):
            async def _send(self, target: str, code: str) -> bool:
                return False

        provider = FailingProvider(redis=fake_redis)
        assert await provider.send_code("alice@example.com") is False
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com") is None
