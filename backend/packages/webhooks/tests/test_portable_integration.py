"""全新 FastAPI 项目只依赖公共配置和注册入口，不导入 App Cloud。"""

import base64
import hashlib
import hmac
import json
import time
from contextlib import asynccontextmanager

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dwy_webhooks.config import WebhookConfig
from dwy_webhooks.events import WebhookEvent
from dwy_webhooks.fastapi import WebhookSinks, install_webhooks

URL = "https://discord.com/api/webhooks/123456/portable-project-token"
SECRET = "whsec_" + base64.b64encode(b"independent-resend-key-32-bytes").decode()


def signed_resend(event_id="new-project-event"):
    """独立计算提供方签名，不以被测验证函数生成测试证据。"""
    body = json.dumps({"type": "email.received", "data": {"email_id": "mail-123"}})
    stamp = str(int(time.time()))
    digest = hmac.new(base64.b64decode(SECRET[6:]), f"{event_id}.{stamp}.{body}".encode(), hashlib.sha256)
    return body, {"svix-id": event_id, "svix-timestamp": stamp,
                  "svix-signature": "v1," + base64.b64encode(digest.digest()).decode()}


def test_one_registration_handles_verified_events_and_preserves_lifespan(monkeypatch):
    """业务应用只安装模块并配置；相同事件去重，宿主生命周期不被覆盖。"""
    from dwy_webhooks import discord

    lifecycle, calls = [], []

    @asynccontextmanager
    async def lifespan(app):
        """记录原项目自身资源的启动和关闭。"""
        lifecycle.append("start")
        yield
        lifecycle.append("stop")

    def receive(request):
        """传输替身保证验收过程中不会向真实 Discord 发送。"""
        calls.append(request)
        return httpx.Response(200, json={"id": "123456"})

    monkeypatch.setattr(discord, "discord_client", lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(receive)))
    app = FastAPI(lifespan=lifespan)
    runtime = install_webhooks(app, WebhookConfig(
        discord_webhook_url=URL, resend={"secret": SECRET, "name": "Another Project"}))
    body, headers = signed_resend()
    with TestClient(app) as client:
        assert lifecycle == ["start"]
        first = client.post("/webhooks/resend", content=body, headers=headers)
        assert first.status_code == 200
        duplicate = client.post("/webhooks/resend", content=body, headers=headers)
        assert duplicate.status_code == 200 and duplicate.json()["duplicate"] is True
        assert len(calls) == 1
        assert "Another Project" in json.loads(calls[0].content)["content"]
        assert client.post("/webhooks/apple/unknown", json={}).status_code == 404
    assert lifecycle == ["start", "stop"] and runtime.closed


def test_configuration_is_explicit_even_when_project_environment_exists(monkeypatch, tmp_path):
    """环境与 dotenv 由项目解析，库只使用显式注入的值。"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("WEBHOOKS_DISCORD_WEBHOOK_URL=https://evil.example/token\n")
    monkeypatch.setenv("WEBHOOKS_DISCORD_WEBHOOK_URL", URL)
    monkeypatch.setenv("WEBHOOKS_RESEND", json.dumps({"secret": SECRET, "events": ["email.received"]}))
    monkeypatch.setenv("APP_CLOUD_ENVIRONMENT", "ignored-by-library")
    settings = WebhookConfig(discord_webhook_url=URL, resend={"secret": SECRET, "events": ["email.received"]})
    assert settings.discord_webhook_url.get_secret_value() == URL
    assert settings.resend.events == frozenset({"email.received"})
    assert "portable-project-token" not in repr(settings)


def test_custom_acceptance_sink_needs_no_management_database():
    """有自己账本的应用提供回调即可接管持久化，不需要 App Cloud 管理库。"""
    events = []

    async def accept(event: WebhookEvent) -> bool:
        """模拟业务项目自己的原子持久接收入口。"""
        events.append(event)
        return True

    app = FastAPI()
    install_webhooks(app, WebhookConfig(resend={"secret": SECRET}), sinks=WebhookSinks(resend=accept))
    body, headers = signed_resend()
    with TestClient(app) as client:
        assert client.post("/webhooks/resend", content=body, headers=headers).status_code == 200
    assert events[0].source == "resend" and events[0].event_id == "new-project-event"


def test_default_delivery_requires_a_target_but_disabled_sources_do_not():
    """配置不完整在启动接入时就失败，而不是静默接受并丢掉通知。"""
    install_webhooks(FastAPI(), WebhookConfig())
    with pytest.raises(ValueError, match="Discord"):
        install_webhooks(FastAPI(), WebhookConfig(resend={"secret": SECRET}))


def test_installing_twice_cannot_duplicate_routes_or_lifecycle():
    """同一应用的安装误用明确失败，避免重复外发。"""
    app = FastAPI()
    install_webhooks(app, WebhookConfig())
    with pytest.raises(ValueError):
        install_webhooks(app, WebhookConfig())


@pytest.mark.parametrize("settings", [
    {"resend": {"secret": "not-a-resend-key"}},
    {"discord_webhook_url": URL + "?unsafe=1"},
    {"app_store_connect": {"apps": {"not-a-numeric-id": {"name": "App", "secret": "x" * 32}}}},
    {"resend": {"secret": SECRET, "path": "https://evil.example/callback"}},
])
def test_portable_configuration_rejects_invalid_boundaries(settings):
    """可复用入口仍必须有显式字段和密钥/路径边界。"""
    with pytest.raises(ValidationError):
        WebhookConfig(**settings)
