"""用实际离线 HTTP 验证业务预设、应用覆盖与持久重试。"""

import json
from unittest.mock import Mock

import pytest
import requests
from dwy_notify import NotificationAppearance, NotificationConfig, Notifier

from dwy_webhooks.appearance import notification_appearance
from dwy_webhooks.delivery import DeliveryPolicy
from dwy_webhooks.events import WebhookEvent
from dwy_webhooks.notification_delivery import deliver_notifications
from dwy_webhooks.sinks import NotificationRelay

DISCORD = "discord://123456789012345678/offline-appearance-token"


@pytest.fixture
def post(monkeypatch):
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"id": "123456789012345679"}'
    mocked = Mock(return_value=response)
    monkeypatch.setattr("dwy_notify._transport.post", mocked)
    return mocked


@pytest.mark.parametrize("source,event_type,username,icon", [
    ("apple_notifications", "DID_RENEW", "购买通知", "purchase"),
    ("app_store_connect", "appStoreVersionAppVersionStateUpdated", "应用审核通知", "review"),
    ("app_store_analytics", "analytics.daily", "经营报表", "report"),
    ("app_store_analytics", "analytics.weekly", "经营报表", "report"),
    ("resend", "email.delivered", "邮件通知", "email"),
    ("app_store_reviews", "review.created", "系统通知", "general"),
    ("other", "unknown", "系统通知", "general"),
])
async def test_direct_events_use_module_owned_appearance(post, source, event_type, username, icon):
    relay = NotificationRelay(Notifier(NotificationConfig(targets={"ops": DISCORD})))
    assert await relay(WebhookEvent(source, "app", "event", event_type, "正文"))
    payload = post.call_args.kwargs["json"]
    assert payload["username"] == username
    assert payload["avatar_url"].endswith(f"/{icon}.png")
    assert payload["avatar_url"].startswith("https://raw.githubusercontent.com/")
    assert payload["content"] == "正文"


async def test_application_can_override_name_and_clear_module_avatar(post):
    relay = NotificationRelay(Notifier(NotificationConfig(
        targets={"ops": DISCORD}, appearance={"username": "ADBox", "avatar_url": None},
    )))
    assert await relay(WebhookEvent("apple_notifications", "app", "event", "SUBSCRIBED", "正文"))
    assert post.call_args.kwargs["json"]["username"] == "ADBox"
    assert "avatar_url" not in post.call_args.kwargs["json"]


@pytest.mark.parametrize("global_target", [False, True])
@pytest.mark.parametrize("username", [None, "自定义邮件通知", "Apple 应用通知"])
async def test_legacy_destination_keeps_module_name_unless_username_is_explicit(
    post, global_target, username,
):
    from dwy_webhooks.config import ResendWebhookConfig, WebhookConfig
    from dwy_webhooks.fastapi import _sink
    from dwy_webhooks.sinks import MemoryReceiptStore

    values = {"discord_webhook_url": "https://discord.com/api/webhooks/123456/offline-token"}
    if username is not None:
        values["discord_username"] = username
    source = ResendWebhookConfig(
        secret="whsec_dGVzdC1zaWduaW5nLWtleS0zMi1ieXRlcw==", **({} if global_target else values),
    )
    config = WebhookConfig(**(values if global_target else {}))
    relay = _sink(source, config, None, MemoryReceiptStore())
    assert await relay(WebhookEvent("resend", "mail", "event", "email.delivered", "正文"))
    assert post.call_args.kwargs["json"]["username"] == (username or "邮件通知")


async def test_legacy_retry_target_fingerprint_survives_default_name_upgrade(post):
    from dwy_webhooks.config import ResendWebhookConfig
    from dwy_webhooks.notifications import configured_notifier, legacy_discord_config

    url = "https://discord.com/api/webhooks/123456/offline-token"
    old = Notifier(legacy_discord_config(url))
    new = configured_notifier(ResendWebhookConfig(
        secret="whsec_dGVzdC1zaWduaW5nLWtleS0zMi1ieXRlcw==", discord_webhook_url=url,
    ))
    payload = {"content": "旧消息", "notifications": {"discord": {
        "fingerprint": old.target_fingerprint("discord"), "status": "retry", "attempts": 1,
        "next_attempt_at": 0, "error_code": "http_error", "message_id": None,
    }}}

    async def checkpoint(**values):
        return True

    result = await deliver_notifications(
        new, payload, policy=DeliveryPolicy(), clock=lambda: 100,
        checkpoint=checkpoint, appearance=notification_appearance("resend"),
    )
    assert result["status"] == "sent"
    assert old.target_fingerprint("discord") == new.target_fingerprint("discord")
    assert post.call_args.kwargs["json"]["username"] == "邮件通知"


@pytest.mark.parametrize("username", [None, "自定义"])
async def test_legacy_direct_relay_uses_module_defaults_or_explicit_name(post, username):
    from dwy_webhooks.sinks import DiscordRelay

    options = {} if username is None else {"username": username}
    relay = DiscordRelay("https://discord.com/api/webhooks/123456/offline-token", **options)
    assert await relay(WebhookEvent("resend", "mail", "event", "email.delivered", "正文"))
    assert post.call_args.kwargs["json"]["username"] == (username or "邮件通知")


async def test_module_appearance_is_persisted_before_send_and_reused_on_retry(post):
    notifier = Notifier(NotificationConfig(targets={"ops": DISCORD}))
    state = {}

    async def checkpoint(**values):
        if "payload" in values:
            state.update(json.loads(json.dumps(values["payload"])))
        return True

    post.return_value.status_code = 503
    first = await deliver_notifications(
        notifier, {"content": "日报"}, policy=DeliveryPolicy(), clock=lambda: 100,
        checkpoint=checkpoint, appearance=notification_appearance("app_store_analytics"),
    )
    assert first["status"] == "retry"
    assert state["appearance"]["username"] == "经营报表"
    post.return_value.status_code = 200
    result = await deliver_notifications(
        notifier, first["payload"], policy=DeliveryPolicy(), clock=lambda: 1000,
        checkpoint=checkpoint, appearance=NotificationAppearance(username="已变更的默认名称"),
    )
    assert result["status"] == "sent"
    assert post.call_args.kwargs["json"]["username"] == "经营报表"


async def test_queue_uses_source_preset_for_legacy_rows(tmp_path, post):
    from dwyeapi.database import create_async_engine_factory, create_session_factory
    from sqlalchemy import MetaData

    from dwy_webhooks.delivery import SQLAlchemyDeliveryQueue, build_delivery_table

    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'appearance.db'}")
    metadata = MetaData()
    table = build_delivery_table(metadata)
    async with engine.begin() as db:
        await db.run_sync(metadata.create_all)
    try:
        queue = SQLAlchemyDeliveryQueue(
            create_session_factory(engine), table, source="app_store_connect",
            notifier=Notifier(NotificationConfig(targets={"ops": DISCORD})),
        )
        await queue.enqueue("app", "event", "appStoreVersionAppVersionStateUpdated", "正文")
        assert await queue.process_pending() == 1
        assert post.call_args.kwargs["json"]["username"] == "应用审核通知"
    finally:
        await engine.dispose()
