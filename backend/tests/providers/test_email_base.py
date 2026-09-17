"""Tests for dwyeapi.providers.email.base(验证码存取 + 一次性校验)。"""

import pytest

from dwyeapi.exceptions import BusinessError
from dwyeapi.providers.email.base import CODE_KEY_PREFIX, EmailProviderBase


class FakeEmailProvider(EmailProviderBase):
    """测试专用 -- 不实际发送邮件,只返回 True 让基类逻辑跑完。"""

    async def _send(self, target: str, code: str) -> bool:
        return True


class TestEmailProviderBase:
    async def test_send_code_stores_in_redis(self, fake_redis):
        provider = FakeEmailProvider(code_ttl=60, redis=fake_redis)
        ok = await provider.send_code("alice@gmail.com")
        assert ok is True

        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@gmail.com")
        assert stored is not None
        assert len(stored) == 6
        assert stored.isdigit()

    async def test_send_code_respects_ttl(self, fake_redis):
        provider = FakeEmailProvider(code_ttl=120, redis=fake_redis)
        await provider.send_code("alice@gmail.com")
        ttl = await fake_redis.ttl(f"{CODE_KEY_PREFIX}alice@gmail.com")
        assert 0 < ttl <= 120

    async def test_send_code_respects_length(self, fake_redis):
        provider = FakeEmailProvider(code_length=4, redis=fake_redis)
        await provider.send_code("alice@gmail.com")
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@gmail.com")
        assert len(stored) == 4

    async def test_verify_code_success_deletes_key(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        await provider.send_code("alice@gmail.com")
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@gmail.com")

        assert await provider.verify_code("alice@gmail.com", stored) is True
        # 成功后 key 被删除,再次校验失败
        assert await provider.verify_code("alice@gmail.com", stored) is False

    async def test_verify_code_wrong_code_keeps_key(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        await provider.send_code("alice@gmail.com")

        assert await provider.verify_code("alice@gmail.com", "000000") is False
        # 错误的 code 不删除 key,正确的 code 仍可用
        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice@gmail.com")
        assert stored is not None
        assert await provider.verify_code("alice@gmail.com", stored) is True

    async def test_verify_code_unknown_target_returns_false(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        assert await provider.verify_code("unknown@example.com", "123456") is False

    async def test_code_is_random(self, fake_redis):
        provider = FakeEmailProvider(redis=fake_redis)
        codes = set()
        for i in range(20):
            await provider.send_code(f"alice{i}@gmail.com")
            stored = await fake_redis.get(f"{CODE_KEY_PREFIX}alice{i}@gmail.com")
            codes.add(stored)
        # 20 次生成至少 10 个不同的码(低冲突)
        assert len(codes) > 10

    async def test_send_code_failure_does_not_store_key(self, fake_redis):
        """_send 失败时不应写入 Redis,避免用户未收到邮件却有可校验码."""

        class FailingProvider(EmailProviderBase):
            async def _send(self, target: str, code: str) -> bool:
                return False

        provider = FailingProvider(redis=fake_redis)
        assert await provider.send_code("alice@gmail.com") is False
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}alice@gmail.com") is None

    async def test_gmail_aliases_share_redis_key(self, fake_redis):
        """Gmail plus / 点 / googlemail 共用同一验证码 key,避免别名绕过冷却与校验."""
        provider = FakeEmailProvider(redis=fake_redis)
        ok = await provider.send_code("Bai.Wen+1@Gmail.com")
        assert ok is True

        stored = await fake_redis.get(f"{CODE_KEY_PREFIX}baiwen@gmail.com")
        assert stored is not None
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}Bai.Wen+1@Gmail.com") is None
        assert await provider.verify_code("baiwen+9@googlemail.com", stored) is True

    async def test_send_code_delivers_to_original_address(self, fake_redis):
        """发信信封用用户输入的地址;规范化只作用于 Redis key."""

        class CaptureProvider(EmailProviderBase):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.sent_to: str | None = None

            async def _send(self, target: str, code: str) -> bool:
                self.sent_to = target
                return True

        provider = CaptureProvider(redis=fake_redis)
        await provider.send_code("User+tag@Gmail.com")
        assert provider.sent_to == "User+tag@Gmail.com"
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}user@gmail.com") is not None

    async def test_send_code_rejects_uncommon_domain_before_send(self, fake_redis):
        """默认发码前拦一次性/未知域名,不调用 _send、不写 Redis。"""

        class CaptureProvider(EmailProviderBase):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.sent = False

            async def _send(self, target: str, code: str) -> bool:
                self.sent = True
                return True

        provider = CaptureProvider(redis=fake_redis)
        with pytest.raises(BusinessError) as exc_info:
            await provider.send_code("qz2d062021@uberip.com")
        assert exc_info.value.code == "EMAIL_DOMAIN_NOT_ALLOWED"
        assert "uberip" not in exc_info.value.message.lower()
        assert provider.sent is False
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}qz2d062021@uberip.com") is None

    async def test_send_code_allows_common_domain(self, fake_redis):
        """常见个人域默认可以发码。"""
        provider = FakeEmailProvider(redis=fake_redis)
        assert await provider.send_code("user@qq.com") is True
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}user@qq.com") is not None

    async def test_send_code_extra_allow_and_disable(self, fake_redis):
        """机构域靠 extra_allow;关闭开关后任意域可发码。"""
        allowed = FakeEmailProvider(redis=fake_redis, extra_allow_domains=("chances.com.cn",))
        assert await allowed.send_code("ops@chances.com.cn") is True

        edu = FakeEmailProvider(redis=fake_redis)
        assert await edu.send_code("a@columbia.edu") is True
        fake = FakeEmailProvider(redis=fake_redis)
        with pytest.raises(BusinessError) as exc_info:
            await fake.send_code("a@atlas.edu.kg")
        assert exc_info.value.code == "EMAIL_DOMAIN_NOT_ALLOWED"

        disabled = FakeEmailProvider(redis=fake_redis, require_common_domain=False)
        assert await disabled.send_code("alice@example.com") is True
