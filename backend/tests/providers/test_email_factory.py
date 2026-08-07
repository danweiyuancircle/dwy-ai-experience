"""Tests for dwyeapi.providers.email.factory(内置 resend + 自定义注册)。"""

import pytest

from dwyeapi.providers.email import (
    EmailProvider,
    EmailProviderBase,
    EmailSettings,
    ResendConfig,
    make_email_provider,
    register_email_provider,
)
from dwyeapi.providers.email.factory import _PROVIDER_REGISTRY


class FakeProvider(EmailProviderBase):
    """测试专用 -- _send 不实际发送,直接返回 True。"""

    async def _send(self, target: str, code: str) -> bool:
        return True


@pytest.fixture(autouse=True)
def clear_registry():
    """每个用例前后清空注册表,避免相互污染。"""
    _PROVIDER_REGISTRY.clear()
    yield
    _PROVIDER_REGISTRY.clear()


class TestResendBuiltin:
    def test_resend_requires_api_key(self):
        settings = EmailSettings(provider="resend", resend=ResendConfig(api_key=""))
        with pytest.raises(ValueError, match="EMAIL__RESEND__API_KEY"):
            make_email_provider(settings)

    def test_resend_requires_from_email(self):
        settings = EmailSettings(
            provider="resend",
            resend=ResendConfig(api_key="re_test", from_email=""),
        )
        with pytest.raises(ValueError, match="EMAIL__RESEND__FROM_EMAIL"):
            make_email_provider(settings)

    def test_resend_with_api_key_constructs(self):
        pytest.importorskip("resend")
        settings = EmailSettings(
            provider="resend",
            resend=ResendConfig(api_key="re_test", from_email="a@b.com"),
        )
        provider = make_email_provider(settings)
        assert provider is not None


class TestCustomRegistration:
    def test_register_and_resolve(self):
        register_email_provider("fake", lambda s: FakeProvider(code_ttl=s.code_ttl))
        provider = make_email_provider(EmailSettings(provider="fake"))
        assert isinstance(provider, FakeProvider)

    def test_register_builtin_name_raises(self):
        with pytest.raises(ValueError, match="内置"):
            register_email_provider("resend", lambda s: FakeProvider())

    def test_register_empty_name_raises(self):
        with pytest.raises(ValueError, match="不能为空"):
            register_email_provider("", lambda s: FakeProvider())

    def test_register_duplicate_overrides(self):
        register_email_provider("dup", lambda s: FakeProvider(code_length=4))
        register_email_provider("dup", lambda s: FakeProvider(code_length=8))
        provider = make_email_provider(EmailSettings(provider="dup"))
        assert isinstance(provider, FakeProvider)
        assert provider._length == 8

    def test_unknown_provider_raises(self):
        settings = EmailSettings(provider="ghost")
        with pytest.raises(ValueError, match="未知 email provider"):
            make_email_provider(settings)

    def test_factory_receives_full_settings(self):
        captured: dict = {}

        def builder(s: EmailSettings) -> EmailProvider:
            captured["brand_name"] = s.brand_name
            captured["code_ttl"] = s.code_ttl
            return FakeProvider(code_ttl=s.code_ttl, brand_name=s.brand_name)

        register_email_provider("capture", builder)
        make_email_provider(EmailSettings(provider="capture", brand_name="X", code_ttl=120))
        assert captured == {"brand_name": "X", "code_ttl": 120}
