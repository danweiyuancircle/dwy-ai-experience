"""审核事件按具体版本补齐平台和版本，查询不覆盖事件原始状态。"""

import hashlib
import hmac
import json
from types import SimpleNamespace

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI

from dwy_apple_notify import config as configs
from dwy_apple_notify.config import AppStoreConnectWebhookConfig
from dwy_apple_notify.providers.app_store_connect import create_asc_router

APP_ID = "6777080682"
VERSION_ID = "3fae277f-6076-425d-935e-7aca631a2a3b"
SECRET = "offline-asc-webhook-signing-secret-32-bytes"


@pytest.fixture
def api_config():
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    return configs.AppStoreConnectAPIConfig(
        issuer_id="11111111-1111-1111-1111-111111111111", key_id="ABCDEFGHIJ", private_key=pem,
    )


def signed_event(*, event_type="appStoreVersionAppVersionStateUpdated", state="IN_REVIEW"):
    attributes = {"newValue": state, "oldValue": "WAITING_FOR_REVIEW"}
    resource_type = "appStoreVersions"
    if event_type == "buildUploadStateUpdated":
        attributes = {"newState": "COMPLETE"}
        resource_type = "buildUploads"
    payload = {"data": {
        "type": event_type, "id": "notification-1", "version": 1, "attributes": attributes,
        "relationships": {"instance": {"data": {"type": resource_type, "id": VERSION_ID}}},
    }}
    raw = json.dumps(payload).encode()
    signature = hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return raw, {"x-apple-signature": "hmacsha256=" + signature}


def version_payload(platform="MAC_OS", version="2.3.1"):
    return {"data": {
        "type": "appStoreVersions", "id": VERSION_ID,
        "attributes": {"platform": platform, "versionString": version, "appVersionState": "REJECTED"},
        "relationships": {"app": {"data": {"type": "apps", "id": APP_ID}}},
    }}


async def post_event(lookup=None, *, api=None, raw=None, headers=None):
    events = []

    async def sink(event):
        events.append(event)
        return True

    app = FastAPI()
    options = {} if lookup is None else {"version_client": lookup}
    app.include_router(create_asc_router(AppStoreConnectWebhookConfig(
        apps={APP_ID: {"name": "ADBox", "secret": SECRET}}, api=api,
    ), sink, **options))
    if raw is None:
        raw, headers = signed_event()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="https://test.example",
    ) as client:
        response = await client.post(f"/webhooks/app-store-connect/{APP_ID}", content=raw, headers=headers)
    return response, events


@pytest.mark.parametrize("platform,label", [("MAC_OS", "macOS"), ("IOS", "iOS"), ("VISION_OS", "visionOS")])
async def test_review_notice_uses_exact_version_metadata_and_original_state(api_config, platform, label):
    from dwy_apple_notify.providers.asc_versions import AppStoreVersionClient

    calls = []

    def receive(request):
        calls.append(request)
        return httpx.Response(200, json=version_payload(platform))

    async with httpx.AsyncClient(transport=httpx.MockTransport(receive)) as http:
        response, events = await post_event(AppStoreVersionClient(api_config, client=http))
        assert not http.is_closed
    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0].url.path == f"/v1/appStoreVersions/{VERSION_ID}"
    assert set(calls[0].url.params["fields[appStoreVersions]"].split(",")) == {
        "platform", "versionString", "app",
    }
    assert calls[0].url.params["include"] == "app"
    assert calls[0].headers["authorization"].startswith("Bearer ")
    notice = events[0]
    assert f"平台：{label}" in notice.content and "版本：2.3.1" in notice.content
    assert "状态：审核中 (IN_REVIEW)" in notice.content
    assert "状态：审核被拒" not in notice.content
    assert notice.data["platform"] == platform and notice.data["version_string"] == "2.3.1"
    assert "版本：1\n" not in notice.content


async def test_explicit_api_config_creates_bounded_client_and_closes_it(api_config, monkeypatch):
    original, clients, options = httpx.AsyncClient, [], []

    def client_factory(**kwargs):
        if "transport" in kwargs:
            return original(**kwargs)
        options.append(kwargs)
        client = original(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=version_payload()),
        ), **kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(httpx, "AsyncClient", client_factory)
    response, events = await post_event(api=api_config)
    assert response.status_code == 200 and "平台：macOS" in events[0].content
    assert len(clients) == 1 and clients[0].is_closed
    assert options == [{"timeout": 10, "follow_redirects": False, "trust_env": False}]


async def test_without_api_credentials_marks_missing_metadata_without_guessing():
    response, events = await post_event()
    assert response.status_code == 200
    assert "平台：未查询" in events[0].content
    assert "版本：未查询" in events[0].content
    assert "未配置 ASC API" in events[0].content


@pytest.mark.parametrize("mode", ["http", "redirect", "network", "json", "wrong_app", "wrong_version",
                                  "missing_version", "invalid_platform", "too_large"])
async def test_lookup_failure_is_safe_retryable_and_never_acknowledged(api_config, mode):
    from dwy_apple_notify.providers.asc_versions import AppStoreVersionClient

    calls = []

    def receive(request):
        calls.append(request)
        if mode == "network":
            raise httpx.ConnectError("private-api-details")
        if mode == "http":
            return httpx.Response(403, json={"error": "private-api-details"})
        if mode == "redirect":
            return httpx.Response(302, headers={"Location": "https://evil.example/credentials"})
        if mode == "json":
            return httpx.Response(200, content=b"not-json")
        if mode == "too_large":
            return httpx.Response(200, content=b"x" * (65536 + 1))
        payload = version_payload()
        if mode == "wrong_app":
            payload["data"]["relationships"]["app"]["data"]["id"] = "123"
        if mode == "wrong_version":
            payload["data"]["id"] = "different-version"
        if mode == "missing_version":
            del payload["data"]["attributes"]["versionString"]
        if mode == "invalid_platform":
            payload["data"]["attributes"]["platform"] = "macOS\nforged"
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(receive), follow_redirects=True) as http:
        response, events = await post_event(AppStoreVersionClient(api_config, client=http))
    assert response.status_code == 502
    assert len(calls) == 1 and not events
    assert "private-api-details" not in response.text


@pytest.mark.parametrize("mode", ["unsigned", "malformed", "build"])
async def test_unverified_invalid_or_build_event_does_not_query_version(mode):
    calls = []

    async def lookup(app_id, version_id):
        calls.append((app_id, version_id))
        raise AssertionError("unexpected metadata lookup")

    raw, headers = signed_event(event_type="buildUploadStateUpdated" if mode == "build"
                                else "appStoreVersionAppVersionStateUpdated", state="" if mode == "malformed"
                                else "IN_REVIEW")
    if mode == "unsigned":
        headers = {}
    response, events = await post_event(SimpleNamespace(lookup=lookup), raw=raw, headers=headers)
    assert response.status_code == {"unsigned": 401, "malformed": 400, "build": 200}[mode]
    assert not calls
    assert bool(events) is (mode == "build")
