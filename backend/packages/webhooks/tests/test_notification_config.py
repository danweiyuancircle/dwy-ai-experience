"""来源各自选择通知目标，配置不会隐式串到其他功能。"""

from types import SimpleNamespace

import pytest
from dwy_notify import NotificationConfig, NotificationDelivery, NotificationResult
from pydantic import ValidationError

from dwy_webhooks.config import ResendWebhookConfig, WebhookConfig
from dwy_webhooks.errors import WebhookDeliveryError
from dwy_webhooks.events import WebhookEvent
from dwy_webhooks.fastapi import _sink
from dwy_webhooks.sinks import MemoryReceiptStore, NotificationRelay

SECRET = "whsec_dGVzdC1zaWduaW5nLWtleS0zMi1ieXRlcw=="


def test_source_notifications_override_defaults_without_sharing_targets():
    source = ResendWebhookConfig(
        secret=SECRET,
        notifications={"targets": {"mail": "discord://123456/mail-token"}},
    )
    config = WebhookConfig(
        notifications={"targets": {"default": "wecombot://default-key"}}, resend=source,
    )
    relay = _sink(source, config, None, MemoryReceiptStore())
    assert relay.notifier.targets == ("mail",)
    other = _sink(ResendWebhookConfig(secret=SECRET), config, None, MemoryReceiptStore())
    assert other.notifier.targets == ("default",)


def test_source_can_select_legacy_discord_over_new_global_defaults():
    source = ResendWebhookConfig(
        secret=SECRET, discord_webhook_url="https://discord.com/api/webhooks/123456/legacy-token",
    )
    relay = _sink(source, WebhookConfig(notifications={"targets": {"ops": "wecombot://key"}}),
                  None, MemoryReceiptStore())
    assert relay.notifier.targets == ("discord",)


@pytest.mark.parametrize("model,extra", [(WebhookConfig, {}), (ResendWebhookConfig, {"secret": SECRET})])
def test_same_level_legacy_and_new_destinations_are_rejected(model, extra):
    with pytest.raises(ValidationError):
        model(**extra, notifications={"targets": {"ops": "wecombot://key"}},
              discord_webhook_url="https://discord.com/api/webhooks/123456/legacy-token")


async def test_relay_only_retries_failed_targets_and_isolates_event_scope():
    calls = []

    async def send(body, *, targets, default_appearance=None):
        name = targets[0]
        calls.append(name)
        return NotificationResult((NotificationDelivery(
            target=name, success=name != "ops" or calls.count("ops") > 1,
            error_code="notification_network_error" if name == "ops" and calls.count("ops") == 1 else None,
        ),))

    notifier = SimpleNamespace(targets=("dev", "ops"), target_fingerprint=lambda name: name, send=send)
    relay = NotificationRelay(notifier, MemoryReceiptStore())
    event = WebhookEvent("resend", "app-a", "same-id", "email.sent", "message")
    with pytest.raises(WebhookDeliveryError):
        await relay(event)
    assert await relay(event) is True
    assert calls == ["dev", "ops", "ops"]
    assert await relay(event) is False
    assert await relay(WebhookEvent("resend", "app-b", "same-id", "email.sent", "message")) is True
    assert calls[-2:] == ["dev", "ops"]


def test_notification_config_hides_credentials():
    config = NotificationConfig(targets={"ops": "wecombot://private-bot-key"})
    assert "private-bot-key" not in repr(config)


def test_resend_and_apple_can_choose_different_channels():
    config = WebhookConfig(
        resend={"secret": SECRET, "notifications": {
            "targets": {"mail-discord": "discord://123456/mail-token"},
        }},
        apple_notifications={
            "apps": {"demo": {"bundle_id": "com.example.demo", "environment": "Sandbox",
                               "root_certificates": [b"offline-test-certificate"]}},
            "notifications": {"targets": {"purchase-wecom": "wecombot://purchase-key"}},
        },
    )
    receipts = MemoryReceiptStore()
    assert _sink(config.resend, config, None, receipts).notifier.targets == ("mail-discord",)
    assert _sink(config.apple_notifications, config, None, receipts).notifier.targets == ("purchase-wecom",)
