"""真实 Apple 事实决定展示，价格不能把状态变更变成新增付款。"""

from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI

from dwy_apple_notify.apple import AppleTransactionDetails, VerifiedAppleNotification


def notice(event="SUBSCRIBED", subtype="INITIAL_BUY", *, environment="Production", **changes):
    tx = dict(transaction_id="tx-1", product_id="pro", purchase_date=datetime(2026, 11, 9, tzinfo=UTC),
              ownership_type="PURCHASED", price_milliunits=22000, currency="CNY")
    product_type = changes.pop("product_type", "Auto-Renewable Subscription")
    tx.update(changes)
    # 此处先验证公开模型确实支持官方商品类型，不能以模型 copy 绕过字段校验。
    details = AppleTransactionDetails(**tx, product_type=product_type)
    return VerifiedAppleNotification("notice-1", "com.example.app", environment, event,
                                     datetime(2026, 11, 9, tzinfo=UTC), subtype,
                                     transaction_details=details)


@pytest.mark.parametrize("event,subtype,product_type,name,icon", [
    ("SUBSCRIBED", "INITIAL_BUY", "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("SUBSCRIBED", "RESUBSCRIBE", "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("DID_RENEW", None, "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("DID_RENEW", "BILLING_RECOVERY", "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("DID_CHANGE_RENEWAL_PREF", "UPGRADE", "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("OFFER_REDEEMED", "UPGRADE", "Auto-Renewable Subscription", "订阅购买", "subscription.png"),
    ("ONE_TIME_CHARGE", None, "Non-Consumable", "买断购买", "purchase.png"),
    ("REFUND", None, "Non-Consumable", "退款通知", "refund.png"),
    ("REFUND", None, "Auto-Renewable Subscription", "退款通知", "refund.png"),
    ("DID_CHANGE_RENEWAL_STATUS", "AUTO_RENEW_DISABLED", "Auto-Renewable Subscription",
     "内购动态", "general.png"),
    ("DID_CHANGE_RENEWAL_PREF", "DOWNGRADE", "Auto-Renewable Subscription", "内购动态", "general.png"),
    ("CONSUMPTION_REQUEST", None, "Non-Consumable", "内购动态", "general.png"),
    ("REFUND_DECLINED", None, "Non-Consumable", "内购动态", "general.png"),
    ("REFUND_REVERSED", None, "Non-Consumable", "内购动态", "general.png"),
    ("REVOKE", None, "Non-Consumable", "内购动态", "general.png"),
    ("EXPIRED", None, "Auto-Renewable Subscription", "内购动态", "general.png"),
    ("OFFER_REDEEMED", None, "Auto-Renewable Subscription", "内购动态", "general.png"),
    ("ONE_TIME_CHARGE", None, "Consumable", "内购动态", "general.png"),
    ("FUTURE_EVENT", None, "Non-Consumable", "内购动态", "general.png"),
])
def test_four_appearances_follow_event_and_product_type(event, subtype, product_type, name, icon):
    from dwy_apple_notify.apple import apple_notification_appearance

    result = apple_notification_appearance(notice(event, subtype, product_type=product_type))
    assert result.username == name
    assert result.avatar_url.endswith("/" + icon)


@pytest.mark.parametrize("changes", [
    {"ownership_type": "FAMILY_SHARED"}, {"ownership_type": None},
    {"price_milliunits": 0}, {"price_milliunits": None}, {"currency": None},
    {"product_type": None}, {"product_type": "Future Type"},
    {"transaction_id": None}, {"purchase_date": None},
    {"revocation_date": datetime(2026, 11, 9, tzinfo=UTC)},
])
def test_shared_free_missing_or_revoked_facts_are_not_payment(changes):
    from dwy_apple_notify.apple import apple_notification_appearance

    assert apple_notification_appearance(notice(**changes)).username == "内购动态"


@pytest.mark.parametrize("event", ["SUBSCRIBED", "REFUND", "TEST"])
def test_sandbox_never_uses_payment_or_refund_appearance(event):
    from dwy_apple_notify.apple import apple_notification_appearance

    assert apple_notification_appearance(notice(event, environment="Sandbox")).username == "内购动态"


def test_refund_does_not_require_price_and_missing_transaction_is_neutral():
    from dwy_apple_notify.apple import apple_notification_appearance

    assert apple_notification_appearance(notice("REFUND", price_milliunits=None)).username == "退款通知"
    unknown = VerifiedAppleNotification("id", "bundle", "Production", "SUBSCRIBED", datetime.now(UTC))
    assert apple_notification_appearance(unknown).username == "内购动态"


async def test_router_attaches_event_appearance_without_expanding_public_data():
    from dwy_apple_notify.config import AppleNotificationApp, AppleNotificationsConfig
    from dwy_apple_notify.providers.apple import create_apple_router

    events = []
    async def verified(signed):
        return notice()
    async def sink(event):
        events.append(event)
        return True

    app = FastAPI()
    app.include_router(create_apple_router(
        AppleNotificationsConfig(apps={"app": AppleNotificationApp(
            name="Example", bundle_id="com.example.app", environment="Production", app_apple_id=123,
            root_certificates=(b"injected-test-root",),
        )}), sink, {"app": SimpleNamespace(verify=verified)},
    ))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://test") as client:
        response = await client.post("/webhooks/apple/app", json={"signedPayload": "verified-boundary"})
    assert response.status_code == 200
    assert events[0].appearance.username == "订阅购买"
    assert len(events[0].data) == 8
    assert "product_type" not in events[0].data


def test_sdk_type_is_preserved_as_public_fact():
    from appstoreserverlibrary.models.JWSTransactionDecodedPayload import JWSTransactionDecodedPayload
    from appstoreserverlibrary.models.Type import Type

    from dwy_apple_notify.apple import apple_transaction_details

    facts = apple_transaction_details(JWSTransactionDecodedPayload(type=Type.NON_CONSUMABLE))
    assert facts.product_type == "Non-Consumable"


@pytest.mark.parametrize("name", ["subscription", "refund"])
def test_new_icons_ship_as_svg_and_256_pixel_png(name):
    import struct
    from importlib.resources import files

    assets = files("dwy_apple_notify").joinpath("assets")
    png = assets.joinpath(name + ".png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == (256, 256)
    assert 'stroke-width="1.8"' in assets.joinpath(name + ".svg").read_text()
    assert "Lucide Contributors" in assets.joinpath("LICENSE.lucide.txt").read_text()
