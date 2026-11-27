"""独立宿主安装 Apple 接入时保留原始签名、生命周期与通知展示合同。"""

import hashlib
import hmac
import json
from contextlib import asynccontextmanager

import httpx
import pytest
from dwy_notify import NotificationAppearance, NotificationConfig
from dwy_notify.delivery import NotificationDeliveryError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dwy_apple_notify import AppleNotifyConfig, AppleNotifySinks, install_apple_notifications

URL = "https://discord.com/api/webhooks/123456789/apple-notify-test-token"
APP_ID = "6777080682"
SECRET = "portable-app-store-connect-secret-32-bytes"


def asc_config(**values):
    return AppleNotifyConfig(app_store_connect={
        "apps": {APP_ID: {"name": "Other Project", "secret": SECRET}},
    }, **values)


def signed_event(event_type="appStoreVersionAppVersionStateUpdated", *, event_id="asc-portable"):
    event = {"type": event_type, "id": event_id}
    if event_type == "appStoreVersionAppVersionStateUpdated":
        event.update(
            version=1, attributes={"newValue": "IN_REVIEW", "oldValue": "WAITING_FOR_REVIEW"},
            relationships={"instance": {"data": {"type": "appStoreVersions", "id": "version-1"}}},
        )
    raw = json.dumps({"data": event}).encode()
    digest = hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return raw, {"x-apple-signature": "hmacsha256=" + digest}


@pytest.mark.parametrize("custom", [False, True])
def test_installed_asc_uses_module_preset_or_explicit_application_override(custom, capture_notification_http):
    calls, order = [], []

    def receive(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "123456789"})

    @asynccontextmanager
    async def lifespan(app):
        order.append("start")
        yield
        order.append("stop")

    capture_notification_http(receive)
    appearance = NotificationAppearance(username="团队审核", avatar_url=None) if custom else None
    notifications = NotificationConfig(targets={"alerts": URL})
    if appearance is not None:
        notifications = notifications.model_copy(update={"appearance": appearance})
    app = FastAPI(lifespan=lifespan)
    runtime = install_apple_notifications(app, asc_config(notifications=notifications))
    raw, headers = signed_event()
    with TestClient(app) as client:
        response = client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers)
        assert response.status_code == 200 and response.json()["duplicate"] is False
        assert client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers).json()[
            "duplicate"
        ] is True
        assert client.post("/webhooks/resend", content=b"{}").status_code == 404
    assert len(calls) == 1 and "Other Project" in calls[0]["content"]
    if custom:
        assert calls[0]["username"] == "团队审核" and "avatar_url" not in calls[0]
    else:
        assert calls[0]["username"] == "应用审核通知"
        assert calls[0]["avatar_url"].endswith("/review.png")
    assert order == ["start", "stop"] and runtime.closed


@pytest.fixture
def custom_sink():
    events, outcomes = [], []

    async def accept(event):
        events.append(event)
        outcome = outcomes.pop(0) if outcomes else True
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    app = FastAPI()
    install_apple_notifications(app, asc_config(), sinks=AppleNotifySinks(app_store_connect=accept))
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, events, outcomes


@pytest.mark.parametrize("mode,status", [("unsigned", 401), ("tampered", 401), ("wrong-app", 404)])
def test_asc_signature_and_scope_are_checked_before_sink(custom_sink, mode, status):
    client, events, _ = custom_sink
    raw, headers = signed_event()
    app_id = APP_ID
    if mode == "unsigned":
        headers = {}
    elif mode == "tampered":
        raw += b" "
    else:
        app_id = "1"
    response = client.post(f"/webhooks/app-store-connect/{app_id}", content=raw, headers=headers)
    assert response.status_code == status
    assert not events


def test_asc_event_filter_and_stream_limit(custom_sink):
    client, events, _ = custom_sink
    raw, headers = signed_event("webhookPingCreated", event_id="ping")
    response = client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers)
    assert response.status_code == 200
    assert "官方连通测试" in events[0].content and events[0].source == "app_store_connect"
    raw, headers = signed_event("unknownEvent", event_id="unknown")
    response = client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers)
    assert response.json()["ignored"]
    assert len(events) == 1
    assert client.post(f"/webhooks/app-store-connect/{APP_ID}", content=b"x" * 65537,
                       headers={"Content-Length": "1"}).status_code == 413
    assert len(events) == 1


@pytest.mark.parametrize("failure,status", [
    (NotificationDeliveryError("discord_http_error", permanent=True), 502),
    (RuntimeError("sensitive storage detail"), 500),
])
def test_failed_sink_is_not_acknowledged(custom_sink, failure, status):
    client, _, outcomes = custom_sink
    outcomes.append(failure)
    raw, headers = signed_event()
    response = client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers)
    assert response.status_code == status and "sensitive storage detail" not in response.text


def test_installation_and_configuration_fail_before_registering_partial_routes():
    app = FastAPI()
    with pytest.raises(ValueError, match="requires notifications"):
        install_apple_notifications(app, asc_config())
    assert not hasattr(app.state, "dwy_apple_notify")
    install_apple_notifications(app, AppleNotifyConfig())
    with pytest.raises(ValueError, match="already installed"):
        install_apple_notifications(app, AppleNotifyConfig())
    with pytest.raises(ValidationError):
        AppleNotifyConfig(app_store_connect={"apps": {"not-a-number": {"name": "App", "secret": SECRET}}})


def test_configuration_does_not_read_host_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("WEBHOOKS_DISCORD_WEBHOOK_URL=https://invalid.example/token\n")
    monkeypatch.setenv("WEBHOOKS_DISCORD_WEBHOOK_URL", URL)
    config = AppleNotifyConfig()
    assert config.discord_webhook_url is None and config.app_store_connect is None
