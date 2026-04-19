"""Tests for dwyeapi.providers.email.factory。"""

import pytest

from dwyeapi.config import set_current_environment
from dwyeapi.providers.email import (
    AliyunEmailConfig,
    EmailSettings,
    ResendConfig,
    make_email_provider,
)
from dwyeapi.providers.email.mock import MockEmailProvider


class TestMakeEmailProvider:
    def test_mock_provider_zero_config(self):
        settings = EmailSettings()
        provider = make_email_provider(settings)
        assert isinstance(provider, MockEmailProvider)

    def test_mock_provider_custom_ttl(self):
        settings = EmailSettings(code_ttl=60, code_length=4)
        provider = make_email_provider(settings)
        assert isinstance(provider, MockEmailProvider)
        assert provider._ttl == 60
        assert provider._length == 4

    def test_resend_provider_missing_api_key_raises(self):
        settings = EmailSettings(provider="resend", resend=ResendConfig(api_key=""))
        with pytest.raises(ValueError, match="EMAIL__RESEND__API_KEY"):
            make_email_provider(settings)

    def test_aliyun_provider_missing_ak_raises(self):
        settings = EmailSettings(provider="aliyun", aliyun=AliyunEmailConfig())
        with pytest.raises(ValueError, match="EMAIL__ALIYUN__ACCESS_KEY"):
            make_email_provider(settings)

    def test_unknown_provider_raises(self):
        settings = EmailSettings.model_construct(provider="unknown")
        with pytest.raises(ValueError, match="未知 email provider"):
            make_email_provider(settings)

    def test_mock_provider_forbidden_in_prod(self):
        set_current_environment("prod")
        settings = EmailSettings(provider="mock")
        with pytest.raises(ValueError, match="EMAIL__PROVIDER=mock"):
            make_email_provider(settings)

    def test_resend_provider_unaffected_in_prod(self):
        set_current_environment("prod")
        settings = EmailSettings(provider="resend", resend=ResendConfig(api_key="re_xxx"))
        provider = make_email_provider(settings)
        assert provider is not None
