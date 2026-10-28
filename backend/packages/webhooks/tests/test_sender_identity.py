"""发送者默认值与注入配置必须进入真实 SDK 载荷。"""

import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import MetaData

from dwy_webhooks import DiscordWebhookSender, discord
from dwy_webhooks.config import ResendWebhookConfig, WebhookConfig
from dwy_webhooks.events import WebhookEvent
from dwy_webhooks.fastapi import _sink
from dwy_webhooks.reviews import AppleReviewsConfig, build_review_tables, install_review_monitor
from dwy_webhooks.sinks import MemoryReceiptStore

URL = "https://discord.com/api/webhooks/123456789/identity-test-token"


@pytest.fixture
def payloads(monkeypatch):
    """仅替代网络边界，保留 SDK 构造与发送。"""
    received = []

    def capture(request):
        received.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "123456789"})

    monkeypatch.setattr(discord, "discord_client", lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(capture),
    ))
    return received


@pytest.mark.parametrize("options,expected", [
    ({}, "Apple 应用通知"),
    ({"username": "团队评分通知"}, "团队评分通知"),
])
async def test_sender_name_is_injected_into_discord_payload(payloads, options, expected):
    assert await DiscordWebhookSender(URL, **options)("hello") == "123456789"
    assert payloads[0]["username"] == expected


@pytest.mark.parametrize("username", ["", " ", "x" * 81, "name\nsecond", "name\x00", 123])
def test_invalid_sender_name_is_rejected_without_echoing_input(username):
    with pytest.raises(ValueError, match="Invalid Discord username") as error:
        DiscordWebhookSender(URL, username=username)
    assert str(error.value) == "Invalid Discord username"


@pytest.mark.parametrize("global_name,source_name,expected", [
    ("Apple 应用通知", None, "Apple 应用通知"),
    ("团队应用通知", None, "团队应用通知"),
    ("团队应用通知", "邮件通知", "邮件通知"),
])
async def test_source_name_overrides_global_name_in_payload(payloads, global_name, source_name, expected):
    source = ResendWebhookConfig(
        secret="whsec_dGVzdC1zaWduaW5nLWtleS0zMi1ieXRlcw==", discord_username=source_name,
    )
    config = WebhookConfig(discord_webhook_url=URL, discord_username=global_name, resend=source)
    relay = _sink(source, config, None, MemoryReceiptStore())
    await relay(WebhookEvent(source="resend", scope="resend", event_id="event-1", event_type="email.sent",
                             content="Mail sent"))
    assert payloads[0]["username"] == expected


@pytest.mark.parametrize("options,expected", [
    ({}, "Apple 应用通知"),
    ({"discord_username": "独立项目评分通知"}, "独立项目评分通知"),
])
async def test_review_config_passes_sender_name_to_sdk(payloads, options, expected):
    config = AppleReviewsConfig(
        apps={"123": {"name": "Demo"}}, issuer_id="11111111-1111-1111-1111-111111111111",
        key_id="ABCDEFGHIJ", private_key="not-used-by-injected-client", discord_webhook_url=URL, **options,
    )
    runtime = install_review_monitor(
        FastAPI(), config, None, build_review_tables(MetaData()), client=SimpleNamespace(),
    )
    assert await runtime.queue.sender("Review") == "123456789"
    assert payloads[0]["username"] == expected
