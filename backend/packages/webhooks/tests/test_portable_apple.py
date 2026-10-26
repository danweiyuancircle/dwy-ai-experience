"""独立 Apple 通知能力：官方验签边界、来源配置与可移植 HTTP 接入。"""

import asyncio
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI

from dwy_webhooks.config import AppleNotificationApp, AppleNotificationsConfig
from dwy_webhooks.errors import WebhookVerificationError
from dwy_webhooks.providers.apple import AppleNotificationVerifier, create_apple_router


async def test_injected_certificate_bytes_do_not_read_project_files(monkeypatch):
    """项目负责取得证书；基础库只消费字节，不能自行寻找或读取文件。"""
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

    captured = []

    def no_files(*args, **kwargs):
        raise AssertionError("Webhook library must not read project files")

    def sdk(self, roots, *args):
        captured.extend(roots)

    monkeypatch.setattr(Path, "read_bytes", no_files)
    monkeypatch.setattr(SignedDataVerifier, "__init__", sdk)
    config = SimpleNamespace(
        environment="Sandbox", app_apple_id=None, bundle_id="com.example.injected",
        verification_workers=1, enable_online_checks=False,
        root_certificates=(b"externally-injected-certificate",),
    )
    verifier = AppleNotificationVerifier(config)
    try:
        verifier._sdk()
        assert captured == [b"externally-injected-certificate"]
    finally:
        await verifier.aclose()


def app_config(root, **overrides):
    """与任何产品无关的 Sandbox 配置，不依赖 App Cloud 设置或数据库。"""
    return AppleNotificationApp(
        name="Other Project", bundle_id="com.example.other", environment="Sandbox",
        root_certificates=(root,), enable_online_checks=False, **overrides,
    )


@pytest.fixture
def official_facts(monkeypatch):
    """仅替换官方 SDK 的签名边界；返回真实 SDK 模型并记录嵌套验签。"""
    from appstoreserverlibrary.models.Data import Data
    from appstoreserverlibrary.models.Environment import Environment
    from appstoreserverlibrary.models.JWSRenewalInfoDecodedPayload import JWSRenewalInfoDecodedPayload
    from appstoreserverlibrary.models.JWSTransactionDecodedPayload import JWSTransactionDecodedPayload
    from appstoreserverlibrary.models.NotificationTypeV2 import NotificationTypeV2
    from appstoreserverlibrary.models.ResponseBodyV2DecodedPayload import ResponseBodyV2DecodedPayload
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

    now = int(datetime.now(UTC).timestamp() * 1000)
    notice = ResponseBodyV2DecodedPayload(
        notificationType=NotificationTypeV2.SUBSCRIBED, notificationUUID="notice-123", signedDate=now,
        data=Data(bundleId="com.example.other", environment=Environment.SANDBOX,
                  signedTransactionInfo="transaction-jws", signedRenewalInfo="renewal-jws"),
    )
    transaction = JWSTransactionDecodedPayload(
        transactionId="transaction-123", originalTransactionId="original-123",
        bundleId="com.example.other", environment=Environment.SANDBOX, productId="subscription.monthly",
        signedDate=now,
    )
    renewal = JWSRenewalInfoDecodedPayload(
        originalTransactionId="original-123", environment=Environment.SANDBOX,
    )
    calls = []

    def boundary(name, value):
        """不同 JWS 必须逐一经过官方接口，不能直接解码嵌套字段。"""
        def verify(self, signed):
            calls.append((name, signed))
            return value
        return verify

    for name, result in (
        ("verify_and_decode_notification", notice),
        ("verify_and_decode_signed_transaction", transaction),
        ("verify_and_decode_renewal_info", renewal),
    ):
        monkeypatch.setattr(SignedDataVerifier, name, boundary(name, result))
    return app_config(b"offline-sdk-boundary-certificate"), calls, notice, transaction, renewal


async def test_nested_jws_are_verified_and_only_safe_metadata_is_returned(official_facts):
    """通知、交易、续订分别验签；事件不携带任何原始 JWS。"""
    config, calls, _, _, _ = official_facts
    verifier = AppleNotificationVerifier(config)
    try:
        result = await verifier.verify("notification-jws")
    finally:
        await verifier.aclose()
    assert result.notification_id == "notice-123"
    assert result.notification_type == "SUBSCRIBED"
    assert result.bundle_id == config.bundle_id
    assert result.product_id == "subscription.monthly"
    assert result.transaction_id == "transaction-123"
    assert calls == [
        ("verify_and_decode_notification", "notification-jws"),
        ("verify_and_decode_signed_transaction", "transaction-jws"),
        ("verify_and_decode_renewal_info", "renewal-jws"),
    ]
    assert "-jws" not in repr(result)


async def test_mismatched_renewal_is_rejected_without_leaking_jws(official_facts):
    """已经验签的交易与续订仍必须属于相同原始交易。"""
    config, _, _, _, renewal = official_facts
    renewal.originalTransactionId = "another-original"
    verifier = AppleNotificationVerifier(config)
    try:
        with pytest.raises(WebhookVerificationError) as caught:
            await verifier.verify("secret-jws")
        assert caught.value.status_code == 401
        assert "secret-jws" not in str(caught.value)
    finally:
        await verifier.aclose()


async def test_missing_original_ids_cannot_count_as_a_matching_renewal(official_facts):
    """两个缺失字段不能因为 None 相等就冒充已验证的交易关系。"""
    config, _, _, transaction, renewal = official_facts
    transaction.originalTransactionId = renewal.originalTransactionId = None
    verifier = AppleNotificationVerifier(config)
    try:
        with pytest.raises(WebhookVerificationError):
            await verifier.verify("notification-jws")
    finally:
        await verifier.aclose()


async def test_real_official_sdk_rejects_forged_unsigned_payload():
    """用真实 SDK 与本地根证书拒绝 alg=none，不让测试替代实际签名校验。"""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID

    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Portable webhook test root")])
    now = datetime.now(UTC)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(1).not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=1)).sign(key, hashes.SHA256()))
    verifier = AppleNotificationVerifier(app_config(cert.public_bytes(serialization.Encoding.DER)))
    try:
        with pytest.raises(WebhookVerificationError) as caught:
            await verifier.verify("eyJhbGciOiJub25lIn0.e30.")
        assert caught.value.status_code == 401
        assert caught.value.__suppress_context__ is True
    finally:
        await verifier.aclose()


async def test_online_verification_failure_is_retryable_without_exception_text(official_facts, monkeypatch):
    """线上证书服务临时不可用是 503，不能误报成永久伪造。"""
    from appstoreserverlibrary.signed_data_verifier import (
        SignedDataVerifier,
        VerificationException,
        VerificationStatus,
    )

    def unavailable(self, signed):
        """模拟官方可重试分类，不访问证书服务。"""
        raise VerificationException(VerificationStatus.RETRYABLE_VERIFICATION_FAILURE)

    monkeypatch.setattr(SignedDataVerifier, "verify_and_decode_notification", unavailable)
    verifier = AppleNotificationVerifier(official_facts[0])
    try:
        with pytest.raises(WebhookVerificationError) as caught:
            await verifier.verify("private-signed-payload")
        assert caught.value.status_code == 503
        assert "private-signed-payload" not in str(caught.value)
    finally:
        await verifier.aclose()


async def test_closed_verifier_cannot_accept_new_work(official_facts):
    """宿主生命周期关闭后不向已关闭的线程池追加工作。"""
    verifier = AppleNotificationVerifier(official_facts[0])
    await verifier.aclose()
    with pytest.raises(WebhookVerificationError) as caught:
        await verifier.verify("signed")
    assert caught.value.status_code == 503


async def test_portable_router_uses_configuration_brand_scope_and_shared_sink(official_facts):
    """只注册公共 router 即可在其他 FastAPI 工程接收，事件没有 ADBox 依赖。"""
    config = official_facts[0]
    verifier = AppleNotificationVerifier(config)
    events = []

    async def sink(event):
        """接收已验签事件，模拟项目自有持久队列或默认转发器。"""
        events.append(event)
        return len(events) == 1

    app = FastAPI()
    app.include_router(create_apple_router(AppleNotificationsConfig(apps={"other": config}), sink,
                                          {"other": verifier}))
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://other"
        ) as client:
            result = await client.post("/webhooks/apple/other", json={"signedPayload": "notification-jws"})
            duplicate = await client.post("/webhooks/apple/other", json={"signedPayload": "notification-jws"})
            assert result.json() == {"received": True, "duplicate": False}
            assert duplicate.json() == {"received": True, "duplicate": True}
            assert (await client.post("/webhooks/apple/unconfigured", json={})).status_code == 404
        event = events[0]
        assert (event.source, event.scope, event.event_id) == ("apple_notifications", "other", "notice-123")
        assert "Other Project" in event.content and "ADBox" not in event.content
        assert event.data["bundle_id"] == config.bundle_id
        assert "jws" not in repr(event.data)
    finally:
        await verifier.aclose()


async def test_unselected_event_is_verified_but_not_forwarded(official_facts):
    """订阅过滤不能成为绕过验签的确认通道。"""
    config, calls, _, _, _ = official_facts
    verifier = AppleNotificationVerifier(config)

    async def forbidden(event):
        """未选中的事件不应交给接收目标。"""
        raise AssertionError("must not forward")

    app = FastAPI()
    app.include_router(create_apple_router(
        AppleNotificationsConfig(apps={"other": config}, events=frozenset({"DID_RENEW"})), forbidden,
        {"other": verifier},
    ))
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://other"
        ) as client:
            response = await client.post("/webhooks/apple/other", json={"signedPayload": "notification-jws"})
            assert response.json() == {"received": True, "ignored": True}
        assert calls
    finally:
        await verifier.aclose()


@pytest.mark.parametrize("body,status", [(b"x" * 262145, 413), (b"not-json", 400), (b"{}", 400)])
async def test_router_rejects_large_or_malformed_body_before_crypto(official_facts, body, status):
    """在读取过程中限制体积，畸形请求不进入签名线程池。"""
    config = official_facts[0]

    async def unexpected(signed):
        """本用例的无效请求不得调用 verifier。"""
        raise AssertionError("crypto must not run")

    app = FastAPI()
    app.include_router(create_apple_router(
        AppleNotificationsConfig(apps={"other": config}), unexpected,
        {"other": SimpleNamespace(verify=unexpected)},
    ))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://other") as client:
        assert (await client.post("/webhooks/apple/other", content=body)).status_code == status


@pytest.mark.parametrize("method", ["verify_and_decode_signed_transaction", "verify_and_decode_renewal_info"])
async def test_invalid_nested_signature_cannot_produce_a_verified_event(official_facts, monkeypatch, method):
    """外层通知有效也不能直接信任嵌套 JWS 的字段。"""
    from appstoreserverlibrary.signed_data_verifier import (
        SignedDataVerifier,
        VerificationException,
        VerificationStatus,
    )

    def invalid(self, signed):
        """模拟官方对某一嵌套签名的拒绝，保留其他边界真实调用路径。"""
        raise VerificationException(VerificationStatus.VERIFICATION_FAILURE)

    monkeypatch.setattr(SignedDataVerifier, method, invalid)
    verifier = AppleNotificationVerifier(official_facts[0])
    try:
        with pytest.raises(WebhookVerificationError) as caught:
            await verifier.verify("notification-jws")
        assert caught.value.status_code == 401
    finally:
        await verifier.aclose()


async def test_cancelled_waiter_does_not_release_running_crypto_budget(official_facts, monkeypatch):
    """取消 HTTP 等待不能让仍运行的签名任务突破配置的并发预算。"""
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

    config, _, notice, _, _ = official_facts
    config = config.model_copy(update={"verification_workers": 1})
    entered, release = threading.Event(), threading.Event()
    calls = []

    def blocking(self, signed):
        """阻塞唯一签名线程，直到用例明确释放。"""
        calls.append(signed)
        entered.set()
        assert release.wait(3)
        return notice

    monkeypatch.setattr(SignedDataVerifier, "verify_and_decode_notification", blocking)
    verifier = AppleNotificationVerifier(config)
    first = asyncio.create_task(verifier.verify("first"))
    try:
        assert await asyncio.to_thread(entered.wait, 1)
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        second = asyncio.create_task(verifier.verify("second"))
        await asyncio.sleep(0.02)
        assert calls == ["first"]
        release.set()
        assert (await asyncio.wait_for(second, timeout=2)).notification_id == "notice-123"
        assert calls == ["first", "second"]
    finally:
        release.set()
        await verifier.aclose()
