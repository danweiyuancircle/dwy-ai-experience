"""Tests for dwyeapi.providers.email.factory(内置 resend + 自定义注册)。"""

import pytest
from pydantic import ValidationError

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
        from dwyeapi.providers.email.resend import ResendEmailProvider

        settings = EmailSettings(
            provider="resend",
            resend=ResendConfig(api_key="re_test", from_email="a@b.com"),
        )
        provider = make_email_provider(settings)
        assert isinstance(provider, ResendEmailProvider)

    def test_resend_forwards_domain_policy(self):
        """工厂必须把白名单开关和 extra_allow 传进 provider,不能只靠基类默认值。"""
        settings = EmailSettings(
            provider="resend",
            require_common_domain=False,
            extra_allow_domains="yanbofund.com",
            allow_edu_cn=False,
            resend=ResendConfig(api_key="re_test", from_email="a@b.com"),
        )
        provider = make_email_provider(settings)
        assert provider._require_common_domain is False
        assert provider._extra_allow == ("yanbofund.com",)
        assert provider._allow_edu_cn is False

    def test_resend_resolves_from_same_registry(self):
        """内置 resend 必须进 _REGISTRY,不能走工厂硬编码 if。"""
        settings = EmailSettings(
            provider="resend",
            resend=ResendConfig(api_key="re_test", from_email="a@b.com"),
        )
        make_email_provider(settings)
        assert "resend" in _PROVIDER_REGISTRY

    def test_cleared_registry_reseeds_resend(self):
        """测试清空注册表后,再次 make 仍能懒加载内置 resend。"""
        from dwyeapi.providers.email.resend import ResendEmailProvider

        _PROVIDER_REGISTRY.clear()
        settings = EmailSettings(
            provider="resend",
            resend=ResendConfig(api_key="re_test", from_email="a@b.com"),
        )
        provider = make_email_provider(settings)
        assert isinstance(provider, ResendEmailProvider)


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


class TestEmailDomainSettings:
    def test_extra_allow_domain_list_splits_and_strips(self):
        settings = EmailSettings(extra_allow_domains=" yanbofund.com, contek.io ,")
        assert settings.extra_allow_domain_list() == ("yanbofund.com", "contek.io")
        assert settings.require_common_domain is True
        assert settings.allow_edu_cn is True

    def test_extra_allow_rejects_oversized_segment(self):
        too_long = "a" * 254
        with pytest.raises(ValidationError, match="253"):
            EmailSettings(extra_allow_domains=too_long)
