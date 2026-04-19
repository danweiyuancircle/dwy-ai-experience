"""Tests for dwyeapi.providers.sms.factory。"""

import pytest

from dwyeapi.providers.sms import AliyunSmsConfig, SmsSettings, make_sms_provider
from dwyeapi.providers.sms.mock import MockSmsProvider


class TestMakeSmsProvider:
    def test_mock_provider_zero_config(self):
        settings = SmsSettings()
        provider = make_sms_provider(settings)
        assert isinstance(provider, MockSmsProvider)

    def test_mock_provider_custom_ttl(self):
        settings = SmsSettings(code_ttl=60, code_length=4)
        provider = make_sms_provider(settings)
        assert provider._ttl == 60
        assert provider._length == 4

    def test_aliyun_provider_missing_ak_raises(self):
        settings = SmsSettings(provider="aliyun", aliyun=AliyunSmsConfig())
        with pytest.raises(ValueError, match="SMS__ALIYUN__ACCESS_KEY"):
            make_sms_provider(settings)

    def test_unknown_provider_raises(self):
        settings = SmsSettings.model_construct(provider="unknown")
        with pytest.raises(ValueError, match="未知 sms provider"):
            make_sms_provider(settings)
