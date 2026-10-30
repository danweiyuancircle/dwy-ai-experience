"""真实 Svix 签名覆盖官方事件接入，通知 HTTP 完全由测试替代。"""

import base64
import hashlib
import hmac
import json
import subprocess
import sys
import time
from contextlib import asynccontextmanager

import pytest
import requests
from dwy_notify import NotificationAppearance, NotificationConfig
from dwy_notify.delivery import NotificationDeliveryError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dwy_email_notify import EmailNotifyConfig, ResendWebhookConfig, install_email_notifications
from dwy_email_notify.providers.resend.appearance import DEFAULT_APPEARANCE

SECRET = "whsec_" + base64.b64encode(b"portable-resend-secret-32-bytes!!").decode()


def signed_event(event=None, *, event_id="resend-notify-test", timestamp=None):
    payload = event if event is not None else {
        "type": "email.received",
        "data": {"email_id": "mail-1", "subject": "private subject", "text": "private body"},
    }
    raw = json.dumps(payload).encode()
    stamp = str(int(time.time()) if timestamp is None else timestamp)
    digest = hmac.new(base64.b64decode(SECRET[6:]),
                      f"{event_id}.{stamp}.".encode() + raw, hashlib.sha256).digest()
    return raw, {"svix-id": event_id, "svix-timestamp": stamp,
                 "svix-signature": "v1," + base64.b64encode(digest).decode()}


@pytest.fixture
def accepted():
    events, outcomes = [], []

    async def sink(event):
        events.append(event)
        outcome = outcomes.pop(0) if outcomes else True
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    app = FastAPI()
    install_email_notifications(app, EmailNotifyConfig(resend=ResendWebhookConfig(
        secret=SECRET, name="Other Project Mail", scope="project-1", path="/hooks/mail",
        events=frozenset({"email.received"}),
    )), sink=sink)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, events, outcomes


def test_signed_event_is_portable_and_metadata_only(accepted):
    client, events, outcomes = accepted
    outcomes[:] = [True, False]
    raw, headers = signed_event()
    assert client.post("/hooks/mail", content=raw, headers=headers).json() == {
        "received": True, "duplicate": False,
    }
    assert client.post("/hooks/mail", content=raw, headers=headers).json()["duplicate"] is True
    event = events[0]
    assert (event.source, event.scope, event.event_id, event.event_type) == (
        "resend", "project-1", "resend-notify-test", "email.received",
    )
    assert "Other Project Mail" in event.content and "mail-1" in event.content
    assert "private subject" not in event.content and "private body" not in event.content
    assert dict(event.data) == {"email_id": "mail-1"}
    assert client.post("/webhooks/resend", content=raw, headers=headers).status_code == 404


@pytest.mark.parametrize("mode", ["unsigned", "tampered", "expired", "future", "wrong", "long_id"])
def test_untrusted_events_never_reach_the_sink(accepted, mode):
    client, events, _ = accepted
    stamp = int(time.time()) + {"expired": -600, "future": 600}.get(mode, 0)
    raw, headers = signed_event(timestamp=stamp)
    if mode == "unsigned":
        headers = {}
    elif mode == "tampered":
        raw += b" "
    elif mode == "wrong":
        headers["svix-signature"] = "v1,invalid"
    elif mode == "long_id":
        headers["svix-id"] = "x" * 257
    assert client.post("/hooks/mail", content=raw, headers=headers).status_code == 401
    assert not events


def test_filtered_events_are_acknowledged_without_parsing_unrelated_data(accepted):
    client, events, _ = accepted
    raw, headers = signed_event({"type": "email.failed", "data": []})
    assert client.post("/hooks/mail", content=raw, headers=headers).json() == {
        "received": True, "ignored": True,
    }
    assert not events


@pytest.mark.parametrize("event", [{"data": {}}, {"type": "email.received", "data": []},
                                  {"type": "email.received", "data": {"email_id": 123}}])
def test_malformed_signed_events_are_rejected(accepted, event):
    client, events, _ = accepted
    raw, headers = signed_event(event)
    assert client.post("/hooks/mail", content=raw, headers=headers).status_code == 400
    assert not events


def test_payload_limit_applies_to_actual_stream_bytes(accepted):
    client, events, _ = accepted
    assert client.post("/hooks/mail", content=b"x" * 65537).status_code == 413
    assert not events


@pytest.mark.parametrize("failure,status", [
    (NotificationDeliveryError("notification_delivery_error"), 502),
    (NotificationDeliveryError("discord_invalid_response"), 502),
    (RuntimeError("private failure"), 500),
    (None, 500),
])
def test_failed_acceptance_never_returns_success(accepted, failure, status):
    client, _, outcomes = accepted
    outcomes[:] = [failure]
    raw, headers = signed_event()
    response = client.post("/hooks/mail", content=raw, headers=headers)
    assert response.status_code == status
    assert "private failure" not in response.text


@pytest.fixture
def notification_http(monkeypatch):
    payloads, statuses = [], []

    def post(url, **kwargs):
        payloads.append(kwargs["json"])
        response = requests.Response()
        response.status_code = statuses.pop(0) if statuses else 200
        response._content = b'{"id":"123456789012345678"}'
        response.headers["Content-Type"] = "application/json"
        return response

    monkeypatch.setattr("dwy_notify._transport.post", post)
    return payloads, statuses


def test_default_relay_retries_failed_event_then_deduplicates(notification_http):
    payloads, statuses = notification_http
    statuses[:] = [503, 200]
    app = FastAPI()
    runtime = install_email_notifications(app, EmailNotifyConfig(
        notifications=NotificationConfig(targets={"ops": "discord://123456789/test-token"}),
        resend=ResendWebhookConfig(secret=SECRET),
    ))
    assert app.state.dwy_email_notify is runtime
    with TestClient(app) as client:
        raw, headers = signed_event()
        assert client.post("/webhooks/resend", content=raw, headers=headers).status_code == 502
        assert client.post("/webhooks/resend", content=raw, headers=headers).json()["duplicate"] is False
        assert client.post("/webhooks/resend", content=raw, headers=headers).json()["duplicate"] is True
    assert len(payloads) == 2
    assert payloads[-1]["username"] == "邮件通知"
    assert payloads[-1]["avatar_url"] == DEFAULT_APPEARANCE.avatar_url


def test_application_can_override_module_name_and_clear_logo(notification_http):
    payloads, _ = notification_http
    app = FastAPI()
    install_email_notifications(app, EmailNotifyConfig(resend=ResendWebhookConfig(
        secret=SECRET, notifications=NotificationConfig(
            targets={"ops": "discord://123456789/test-token"},
            appearance=NotificationAppearance(username="我的邮件事件", avatar_url=None),
        ),
    )))
    with TestClient(app) as client:
        raw, headers = signed_event()
        assert client.post("/webhooks/resend", content=raw, headers=headers).status_code == 200
    assert payloads[0]["username"] == "我的邮件事件"
    assert "avatar_url" not in payloads[0]


def test_installation_preserves_host_lifespan_and_rejects_duplicate_routes():
    calls = []

    @asynccontextmanager
    async def lifespan(app):
        calls.append("start")
        yield
        calls.append("stop")

    app = FastAPI(lifespan=lifespan)
    config = EmailNotifyConfig()
    install_email_notifications(app, config)
    with pytest.raises(ValueError, match="already installed"):
        install_email_notifications(app, config)
    with TestClient(app) as client:
        assert client.post("/webhooks/resend").status_code == 404
    assert calls == ["start", "stop"]


def test_missing_destination_is_rejected_before_installing_routes():
    app = FastAPI()
    before = len(app.routes)
    with pytest.raises(ValueError, match="requires"):
        install_email_notifications(app, EmailNotifyConfig(resend=ResendWebhookConfig(secret=SECRET)))
    assert len(app.routes) == before
    assert not hasattr(app.state, "dwy_email_notify")


@pytest.mark.parametrize("settings", [
    {"secret": "invalid-private-secret"},
    {"secret": "whsec_eA=="},
    {"secret": SECRET, "scope": "../bad"},
    {"secret": SECRET, "path": "https://example.com/hook"},
    {"secret": SECRET, "events": ["unsafe event"]},
])
def test_configuration_rejects_invalid_external_boundaries(settings):
    with pytest.raises(ValidationError) as error:
        ResendWebhookConfig(**settings)
    assert "invalid-private-secret" not in str(error.value)


def test_default_preset_is_a_public_immutable_value():
    assert DEFAULT_APPEARANCE.username == "邮件通知"
    assert DEFAULT_APPEARANCE.avatar_url.endswith("/email.png")
    assert "/091ad4fea18ed3840fec83dc833f18b759256ca7/" in DEFAULT_APPEARANCE.avatar_url


def test_root_import_does_not_load_any_supplier_sdk_or_old_package(tmp_path):
    result = subprocess.run([sys.executable, "-c", """
import sys
from dwy_email_notify import EmailNotifyConfig
assert EmailNotifyConfig().resend is None
assert not any(name == 'resend' or name.startswith(('appstoreserverlibrary', 'dwy_webhooks'))
               for name in sys.modules)
"""], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
