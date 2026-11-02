"""通过真实 SDK callback 验证签名、解密与通知边界，不访问网络。"""

import base64
import importlib
import json
import subprocess
import sys
import time

import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import FastAPI
from pydantic import ValidationError
from wechatpayv3.async_ import AsyncWeChatPay
from wechatpayv3.async_.type import WeChatPayType


def api():
    """动态导入使 RED 明确表现为公开来源包尚不存在。"""
    return importlib.import_module("dwy_wechatpay_notify")


@pytest.fixture(scope="module")
def key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def resource(event="TRANSACTION.SUCCESS"):
    common = {
        "mchid": "1900000001",
        "out_trade_no": "order_123456",
        "transaction_id": "wx123456",
        "amount": {"total": 12345, "currency": "CNY"},
    }
    if event == "TRANSACTION.SUCCESS":
        return {
            **common,
            "appid": "wx123",
            "trade_state": "SUCCESS",
            "trade_type": "NATIVE",
            "payer": {"openid": "PRIVATE_OPENID"},
        }
    return {
        **common,
        "out_refund_no": "refund_123456",
        "refund_id": "wxrefund123",
        "refund_status": event.split(".")[1],
        "amount": {
            "total": 12345,
            "refund": 300,
        },
    }


def envelope(key, *, event="TRANSACTION.SUCCESS", payload=None, aes_key=b"a" * 32):
    encrypted = AESGCM(aes_key).encrypt(
        b"123456789012", json.dumps(resource(event) if payload is None else payload).encode(), b"transaction"
    )
    body = json.dumps(
        {
            "id": "provider-event-123",
            "event_type": event,
            "resource_type": "encrypt-resource",
            "create_time": "2026-11-02T12:00:00+08:00",
            "resource": {
                "algorithm": "AEAD_AES_256_GCM",
                "nonce": "123456789012",
                "associated_data": "transaction",
                "ciphertext": base64.b64encode(encrypted).decode(),
            },
        }
    ).encode()
    timestamp, nonce = str(int(time.time())), "testnonce"
    signature = key.sign(
        timestamp.encode() + b"\n" + nonce.encode() + b"\n" + body + b"\n",
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return {
        "Wechatpay-Timestamp": timestamp,
        "Wechatpay-Nonce": nonce,
        "Wechatpay-Serial": "PUB_KEY_ID_TEST",
        "Wechatpay-Signature-Type": "WECHATPAY2-SHA256-RSA2048",
        "Wechatpay-Signature": base64.b64encode(signature).decode(),
    }, body


def client(key):
    return AsyncWeChatPay(
        wechatpay_type=WeChatPayType.NATIVE,
        mchid="1900000001",
        appid="wx123",
        private_key=key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ).decode(),
        cert_serial_no="1234",
        apiv3_key="a" * 32,
        public_key_id="PUB_KEY_ID_TEST",
        public_key=key.public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        .decode(),
    )


def config(**overrides):
    return api().WechatPayNotifyConfig(
        **{"mchid": "1900000001", "appid": "wx123", "scope": "shop", **overrides}
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event", ["TRANSACTION.SUCCESS", "REFUND.SUCCESS", "REFUND.ABNORMAL", "REFUND.CLOSED"]
)
async def test_real_sdk_verifies_payment_and_refund_without_appid(key, event):
    async with client(key) as sdk:
        verified = (
            await api()
            .WechatPayNotificationVerifier(config(), callback=sdk.callback)
            .verify(*envelope(key, event=event))
        )
    notice = api().wechatpay_notification_event(verified, scope="shop")
    assert notice.source == "wechatpay"
    assert notice.data["amount_fen"] == 12345
    assert notice.data["provider_event_id"] == "provider-event-123"
    assert "PRIVATE_OPENID" not in repr(notice.data)
    assert "123.45" in notice.content
    assert ("已入账" not in notice.content) and len(notice.content.encode()) <= 1800
    if event.startswith("REFUND"):
        assert verified.refund_fen == 300
        assert notice.event_id == f"wechat:refund:refund_123456:{event.split('.')[1]}"
    else:
        assert notice.event_id == "wechat:payment:order_123456:success"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mutation",
    [
        "signature",
        "signtest",
        "key",
        "mchid",
        "appid",
        "amount",
        "bool_amount",
        "missing",
        "long",
        "state",
        "currency",
        "refund_state",
        "refund_currency",
    ],
)
async def test_untrusted_callback_rejected_without_sensitive_error(key, mutation):
    event = "REFUND.SUCCESS" if mutation in {"refund_state", "refund_currency"} else "TRANSACTION.SUCCESS"
    payload = resource(event)
    if mutation in {"mchid", "appid"}:
        payload[mutation] = "other"
    if mutation == "amount":
        payload["amount"]["total"] = -1
    if mutation == "bool_amount":
        payload["amount"]["total"] = True
    if mutation == "missing":
        del payload["transaction_id"]
    if mutation == "long":
        payload["out_trade_no"] = "x" * 33
    if mutation == "state":
        payload["trade_state"] = "CLOSED"
    if mutation in {"currency", "refund_currency"}:
        payload["amount"]["currency"] = "USD"
    if mutation == "refund_state":
        payload["refund_status"] = "CLOSED"
    headers, body = envelope(
        key, event=event, payload=payload, aes_key=b"b" * 32 if mutation == "key" else b"a" * 32
    )
    if mutation == "signature":
        headers["Wechatpay-Signature"] = base64.b64encode(b"invalid").decode()
    if mutation == "signtest":
        headers["Wechatpay-Signature"] = "WECHATPAY/SIGNTEST/secret"
    async with client(key) as sdk:
        with pytest.raises(api().WechatPayVerificationError) as error:
            await api().WechatPayNotificationVerifier(config(), callback=sdk.callback).verify(headers, body)
    assert "secret" not in str(error.value) and "PRIVATE" not in str(error.value)


@pytest.mark.asyncio
async def test_sdk_none_and_exception_are_safe():
    for callback in (lambda h, b: None, lambda h, b: (_ for _ in ()).throw(ValueError("PRIVATE"))):
        with pytest.raises(api().WechatPayVerificationError, match="verification failed"):
            await api().WechatPayNotificationVerifier(config(), callback=callback).verify({}, b"{}")


@pytest.mark.asyncio
async def test_confirmed_and_callback_share_business_key_without_fabricated_official_id(key):
    async with client(key) as sdk:
        verified = (
            await api().WechatPayNotificationVerifier(config(), callback=sdk.callback).verify(*envelope(key))
        )
    confirmed = api().ConfirmedWechatPayResult(
        event_type="TRANSACTION.SUCCESS",
        order_no=verified.order_no,
        transaction_id=verified.transaction_id,
        amount_fen=12345,
        trade_type="NATIVE",
        trade_state="SUCCESS",
    )
    a = api().wechatpay_notification_event(verified, scope="shop")
    b = api().wechatpay_notification_event(confirmed, scope="shop")
    assert a.event_id == b.event_id
    assert "provider_event_id" not in b.data
    refund = api().ConfirmedWechatPayResult(
        event_type="REFUND.CLOSED",
        order_no=verified.order_no,
        transaction_id=verified.transaction_id,
        amount_fen=12345,
        refund_no="refund_123456",
        refund_id="wxrefund123",
        refund_fen=300,
        refund_status="CLOSED",
    )
    assert api().wechatpay_notification_event(refund, scope="shop").event_id.endswith(":CLOSED")


def test_strict_models_and_utf8_content_budget():
    for overrides in ({"scope": "x" * 129}, {"mchid": ""}, {"appid": " "}, {"max_body_bytes": 0}):
        with pytest.raises(ValidationError):
            config(**overrides)
    with pytest.raises(ValidationError):
        api().PaymentNotificationContext(description="x" * 1025)
    with pytest.raises(ValidationError):
        api().ConfirmedWechatPayResult(
            event_type="REFUND.SUCCESS", order_no="order123", transaction_id="wx1", amount_fen=100
        )
    result = api().ConfirmedWechatPayResult(
        event_type="TRANSACTION.SUCCESS",
        order_no="x" * 32,
        transaction_id="y" * 64,
        amount_fen=999999999999,
        trade_type="NATIVE",
        trade_state="SUCCESS",
    )
    context = api().PaymentNotificationContext(description="汉" * 1024, outcome="字" * 1024)
    event = api().wechatpay_notification_event(result, scope="shop", context=context)
    assert len(event.content.encode("utf8")) <= 1800
    assert "x" * 32 in event.content and "y" * 64 in event.content
    assert "9999999999.99" in event.content
    with pytest.raises(TypeError):
        api().wechatpay_notification_event(result, scope="shop", context={"token": "private"})


@pytest.mark.asyncio
async def test_installer_acknowledges_duplicates_but_retries_sink_failure_and_limits_stream(key):
    app, accepted, calls = FastAPI(), [], []

    async def sink(event):
        accepted.append(event)
        if len(accepted) == 1:
            raise RuntimeError("PRIVATE_SINK")
        return False

    async with client(key) as sdk:

        def callback(headers, body):
            calls.append(body)
            return sdk.callback(headers, body)

        api().install_wechatpay_notifications(
            app,
            config(),
            verifier=api().WechatPayNotificationVerifier(config(), callback=callback),
            sink=sink,
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="https://test.invalid"
        ) as http:
            headers, body = envelope(key)
            response = await http.post("/webhooks/wechatpay", headers=headers, content=body)
            assert response.status_code == 503 and "PRIVATE" not in response.text
            response = await http.post("/webhooks/wechatpay", headers=headers, content=body)
            assert response.status_code in {200, 204} and len(calls) == 2 and calls[0] == body

            async def stream():
                yield b"x" * 40000
                yield b"x" * 40000

            response = await http.post("/webhooks/wechatpay", content=stream())
            assert response.status_code == 413 and len(calls) == 2
            headers["Wechatpay-Signature"] = "WECHATPAY/SIGNTEST/test"
            response = await http.post("/webhooks/wechatpay", headers=headers, content=body)
            assert response.status_code == 400 and len(accepted) == 2


def test_core_import_does_not_import_fastapi_or_host_payment():
    code = (
        "import sys; import dwy_wechatpay_notify; "
        "assert 'fastapi' not in sys.modules; assert 'dwy_payment' not in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_host_result_subclass_keeps_sensitive_extensions_out_of_event_data():
    class HostResult(api().ConfirmedWechatPayResult):
        openid: str
        secret: str

    result = HostResult(
        event_type="TRANSACTION.SUCCESS",
        order_no="order123",
        transaction_id="wx123",
        amount_fen=100,
        trade_type="NATIVE",
        trade_state="SUCCESS",
        openid="SYNTHETIC_PRIVATE_OPENID",
        secret="SYNTHETIC_PRIVATE_SECRET",
    )
    event = api().wechatpay_notification_event(result, scope="shop")
    assert event.data == {
        "event_type": "TRANSACTION.SUCCESS",
        "order_no": "order123",
        "transaction_id": "wx123",
        "amount_fen": 100,
        "trade_type": "NATIVE",
        "trade_state": "SUCCESS",
    }
    assert "SYNTHETIC_PRIVATE" not in event.content


@pytest.mark.parametrize(
    "field,value", [("amount_fen", 0), ("amount_fen", "100"), ("refund_fen", 0), ("refund_fen", 101)]
)
def test_confirmed_rejects_invalid_financial_amounts(field, value):
    fields = {
        "event_type": "REFUND.SUCCESS",
        "order_no": "order123",
        "transaction_id": "wx1",
        "amount_fen": 100,
        "refund_no": "refund123",
        "refund_id": "wxrefund1",
        "refund_fen": 20,
        "refund_status": "SUCCESS",
        field: value,
    }
    with pytest.raises(ValidationError):
        api().ConfirmedWechatPayResult(**fields)


@pytest.mark.asyncio
async def test_verifier_rejects_oversize_before_callback():
    def callback(headers, body):
        pytest.fail("oversize request must never reach SDK")

    with pytest.raises(api().WechatPayVerificationError):
        await (
            api()
            .WechatPayNotificationVerifier(config(max_body_bytes=4), callback=callback)
            .verify({}, b"12345")
        )


@pytest.mark.asyncio
async def test_verifier_bounds_signature_header_before_sdk():
    def callback(headers, body):
        pytest.fail("oversize signature must not reach SDK")

    with pytest.raises(api().WechatPayVerificationError):
        await (
            api()
            .WechatPayNotificationVerifier(config(), callback=callback)
            .verify({"Wechatpay-Signature": "x" * 4097}, b"{}")
        )


def test_installer_preserves_lifecycle_and_refuses_conflicting_routes():
    app = FastAPI()
    lifespan = app.router.lifespan_context
    verifier = api().WechatPayNotificationVerifier(config(), callback=lambda h, b: None)

    async def sink(event):
        return True

    api().install_wechatpay_notifications(app, config(), verifier=verifier, sink=sink)
    assert app.router.lifespan_context is lifespan
    with pytest.raises(ValueError):
        api().install_wechatpay_notifications(app, config(), verifier=verifier, sink=sink)
    fresh = FastAPI()
    fresh.add_api_route(config().path, lambda: None, methods=["POST"])
    with pytest.raises(ValueError):
        api().install_wechatpay_notifications(fresh, config(), verifier=verifier, sink=sink)
