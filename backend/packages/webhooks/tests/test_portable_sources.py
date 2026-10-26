"""独立来源适配器：不导入宿主，使用真实 Resend SDK 与原始字节 HMAC 验签。"""

import base64
import hashlib
import hmac
import json
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dwy_webhooks.config import (
    AppStoreConnectApp,
    AppStoreConnectWebhookConfig,
    ResendWebhookConfig,
)
from dwy_webhooks.errors import WebhookDeliveryError
from dwy_webhooks.providers.app_store_connect import create_asc_router
from dwy_webhooks.providers.resend import create_resend_router

RESEND_SECRET = "whsec_" + base64.b64encode(b"portable-resend-secret-32-bytes!!").decode()
ASC_SECRET = "portable-app-store-connect-secret-32-bytes"
APP_ID = "6777080682"


def resend_request(event=None, *, event_id="msg_portable", timestamp=None):
    """独立计算 Svix 格式签名，避免以被测 SDK 自证验签。"""
    payload = event if event is not None else {
        "type": "email.received",
        "data": {"email_id": "mail-portable", "subject": "private subject", "text": "private content"},
    }
    raw = json.dumps(payload).encode()
    stamp = str(int(time.time()) if timestamp is None else timestamp)
    digest = hmac.new(base64.b64decode(RESEND_SECRET[6:]),
                      f"{event_id}.{stamp}.".encode() + raw, hashlib.sha256).digest()
    return raw, {"svix-id": event_id, "svix-timestamp": stamp,
                 "svix-signature": "v1," + base64.b64encode(digest).decode()}


def asc_request(event=None, *, secret=ASC_SECRET):
    """签名覆盖原始字节；格式化变化也应被视为篡改。"""
    payload = event if event is not None else {
        "data": {"type": "appStoreVersionAppVersionStateUpdated", "id": "asc-portable", "version": 1,
                 "attributes": {"newValue": "IN_REVIEW", "oldValue": "WAITING_FOR_REVIEW"},
                 "relationships": {"instance": {"data": {"type": "appStoreVersions", "id": "version-1"}}}},
    }
    raw = json.dumps(payload).encode()
    digest = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return raw, {"x-apple-signature": "hmacsha256=" + digest}


@pytest.fixture
def relay():
    """新 FastAPI 项目只安装来源路由，不创建宿主、产品或数据库。"""
    events, outcomes = [], []

    async def sink(event):
        """记录已校验的中立事件，模拟调用方的接收/持久化语义。"""
        events.append(event)
        outcome = outcomes.pop(0) if outcomes else True
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    app = FastAPI()
    app.include_router(create_resend_router(ResendWebhookConfig(
        secret=RESEND_SECRET, name="Other Project Mail", scope="other-project",
        path="/hooks/mail", events=frozenset({"email.received"}),
    ), sink))
    app.include_router(create_asc_router(AppStoreConnectWebhookConfig(
        apps={APP_ID: AppStoreConnectApp(name="Other Project", secret=ASC_SECRET)},
        path="/hooks/apple/{app_id}",
    ), sink))
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, events, outcomes


def test_resend_is_portable_configurable_and_metadata_only(relay):
    """配置来源名、路由和作用域即可使用，秘密与邮件内容不会进入事件。"""
    client, events, outcomes = relay
    outcomes[:] = [True, False]
    raw, headers = resend_request()
    assert client.post("/hooks/mail", content=raw, headers=headers).json() == {
        "received": True, "duplicate": False,
    }
    assert client.post("/hooks/mail", content=raw, headers=headers).json()["duplicate"] is True
    event = events[0]
    assert (event.source, event.scope, event.event_id, event.event_type) == (
        "resend", "other-project", "msg_portable", "email.received",
    )
    assert "Other Project Mail" in event.content and "mail-portable" in event.content
    assert "private subject" not in event.content and "private content" not in event.content
    assert dict(event.data) == {"email_id": "mail-portable"}
    assert client.post("/webhooks/resend", content=raw, headers=headers).status_code == 404


@pytest.mark.parametrize("mode", ["unsigned", "tampered", "expired", "future", "wrong"])
def test_resend_rejects_untrusted_events_without_calling_sink(relay, mode):
    """缺失、篡改、错误和时间失效签名都在接收前拒绝。"""
    client, events, _ = relay
    stamp = int(time.time()) + {"expired": -600, "future": 600}.get(mode, 0)
    raw, headers = resend_request(timestamp=stamp)
    if mode == "unsigned":
        headers = {}
    elif mode == "tampered":
        raw += b" "
    elif mode == "wrong":
        headers["svix-signature"] = "v1,invalid"
    assert client.post("/hooks/mail", content=raw, headers=headers).status_code == 401
    assert not events


def test_resend_configured_filter_ignores_other_events(relay):
    """未选择事件先确认忽略，不依赖另一类事件的字段。"""
    client, events, _ = relay
    raw, headers = resend_request({"type": "email.failed", "data": []})
    assert client.post("/hooks/mail", content=raw, headers=headers).json() == {
        "received": True, "ignored": True,
    }
    assert not events


def test_asc_is_portable_and_keeps_the_app_scope(relay):
    """来自另一应用的原始 Apple 状态可直接转换为中立事件。"""
    client, events, outcomes = relay
    outcomes[:] = [True, False]
    raw, headers = asc_request()
    response = client.post(f"/hooks/apple/{APP_ID}", content=raw, headers=headers)
    assert response.status_code == 200 and response.json()["duplicate"] is False
    assert client.post(f"/hooks/apple/{APP_ID}", content=raw, headers=headers).json()["duplicate"] is True
    event = events[0]
    assert (event.source, event.scope, event.event_id) == ("app_store_connect", APP_ID, "asc-portable")
    assert "Other Project" in event.content and "审核中" in event.content
    assert f"https://appstoreconnect.apple.com/apps/{APP_ID}/distribution" in event.content


def test_asc_ping_and_unknown_events_are_distinguished(relay):
    """连通测试不冒充业务状态；未知未选择事件直接忽略。"""
    client, events, _ = relay
    raw, headers = asc_request({"data": {"type": "webhookPingCreated", "id": "ping-1"}})
    assert client.post(f"/hooks/apple/{APP_ID}", content=raw, headers=headers).status_code == 200
    assert "官方连通测试" in events[0].content
    raw, headers = asc_request({"data": {"type": "newUnknownEvent", "id": "unknown-1"}})
    assert client.post(f"/hooks/apple/{APP_ID}", content=raw, headers=headers).json()["ignored"] is True
    assert len(events) == 1


@pytest.mark.parametrize("mode,status", [("unsigned", 401), ("tampered", 401), ("wrong-app", 404)])
def test_asc_rejects_invalid_signatures_and_unconfigured_apps(relay, mode, status):
    """应用独立密钥只允许处理配置过的作用域。"""
    client, events, _ = relay
    raw, headers = asc_request()
    app_id = APP_ID
    if mode == "unsigned":
        headers = {}
    elif mode == "tampered":
        raw += b" "
    else:
        app_id = "1"
    assert client.post(f"/hooks/apple/{app_id}", content=raw, headers=headers).status_code == status
    assert not events


@pytest.mark.parametrize("source", ["resend", "asc"])
def test_both_sources_limit_streamed_payloads(relay, source):
    """限额不依赖 Content-Length，未验签的大请求不能进入接收端。"""
    client, events, _ = relay
    path = "/hooks/mail" if source == "resend" else f"/hooks/apple/{APP_ID}"
    assert client.post(path, content=b"x" * 65537, headers={"Content-Length": "1"}).status_code == 413
    assert not events


@pytest.mark.parametrize("source", ["resend", "asc"])
@pytest.mark.parametrize("failure,status", [
    (WebhookDeliveryError("discord_http_error", permanent=True), 502),
    (RuntimeError("sensitive storage detail"), 500),
])
def test_failed_sink_is_never_acknowledged_as_received(relay, source, failure, status):
    """发送或存储失败留给调用方重试，HTTP 响应不公开内部异常。"""
    client, _, outcomes = relay
    outcomes[:] = [failure]
    raw, headers = resend_request() if source == "resend" else asc_request()
    path = "/hooks/mail" if source == "resend" else f"/hooks/apple/{APP_ID}"
    response = client.post(path, content=raw, headers=headers)
    assert response.status_code == status
    assert "sensitive storage detail" not in response.text
