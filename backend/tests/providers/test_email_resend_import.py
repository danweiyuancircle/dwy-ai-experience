"""ResendEmailProvider:缺 extra 友好报错 + mock SDK 测 _send(不打真实网络)。"""

import sys
from unittest.mock import AsyncMock, patch

import pytest

from dwyeapi.providers.email.resend import ResendEmailProvider


class TestResendImportError:
    def test_missing_resend_package_raises_friendly_error(self):
        """模拟 `resend` 包未安装,构造 ResendEmailProvider 应抛 ImportError 并带安装提示。"""
        original = sys.modules.pop("resend", None)
        try:
            with (
                patch.dict(sys.modules, {"resend": None}),
                pytest.raises(ImportError, match=r"dwyeapi\[email-resend\]"),
            ):
                ResendEmailProvider(api_key="x", from_email="a@b.com", subject="t")
        finally:
            if original is not None:
                sys.modules["resend"] = original


class TestResendSend:
    async def test_send_code_calls_resend_async_api(self, fake_redis):
        """内置 provider 必须真正调 SDK;用 mock 代替网络,断言信封字段。"""
        provider = ResendEmailProvider(
            api_key="re_test",
            from_email="from@example.com",
            subject="验证码",
            redis=fake_redis,
        )
        provider._resend.Emails.send_async = AsyncMock(return_value={"id": "msg_1"})

        ok = await provider.send_code("User+tag@Gmail.com")
        assert ok is True
        provider._resend.Emails.send_async.assert_awaited_once()
        params = provider._resend.Emails.send_async.await_args.args[0]
        assert params["from"] == "from@example.com"
        assert params["to"] == ["User+tag@Gmail.com"]
        assert params["subject"] == "验证码"
        assert "html" in params
        assert "text" in params

    async def test_send_failure_returns_false_and_skips_redis(self, fake_redis):
        """SDK 失败时不写验证码 key,避免用户没收到信却能验码。"""
        from dwyeapi.providers.email.base import CODE_KEY_PREFIX

        provider = ResendEmailProvider(
            api_key="re_test",
            from_email="from@example.com",
            redis=fake_redis,
        )
        provider._resend.Emails.send_async = AsyncMock(side_effect=RuntimeError("network"))

        ok = await provider.send_code("alice@example.com")
        assert ok is False
        assert await fake_redis.get(f"{CODE_KEY_PREFIX}alice@example.com") is None
