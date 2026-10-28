"""可复用 Apple 文案只消费安全事实；不依赖业务工程或自动处理权益。"""

import json
from dataclasses import replace
from datetime import UTC, datetime

import httpx
import pytest


def notification(kind="ONE_TIME_CHARGE", **changes):
    """构造其他项目的安全通知对象，复用原八字段构造方式。"""
    from dwy_webhooks.apple import VerifiedAppleNotification

    return VerifiedAppleNotification(
        notification_id="portable-notice", bundle_id="com.example.portable", environment="Sandbox",
        notification_type=kind, signed_at=datetime(2026, 10, 27, tzinfo=UTC), **changes,
    )


@pytest.mark.parametrize("price,currency,expected", [
    (4990, "USD", "4.99 USD"), (0, "CNY", "0 CNY"), (1, "USD", "0.001 USD"),
    (3300000, "KRW", "3300 KRW"), (4990, None, "Apple 未提供"),
])
def test_portable_price_is_exact_and_has_no_product_brand(price, currency, expected):
    """整毫单位只换算一次，不猜币种，不将家庭共享或交易价格写成收入。"""
    from dwy_webhooks.apple import AppleTransactionDetails, apple_notification_content

    notice = notification(transaction_details=AppleTransactionDetails(
        transaction_id="tx", product_id="portable.lifetime", price_milliunits=price, currency=currency,
        storefront="AUS", purchase_date="2026-10-27T00:00:00Z", ownership_type="FAMILY_SHARED",
    ))
    content = apple_notification_content(notice, app_name="Other Project")
    assert "Other Project · 家庭共享内购授权" in content and "ADBox" not in content
    assert f"交易金额：{expected}" in content and "购买地区：AUS" in content
    assert "购买时间：2026-10-27T00:00:00+00:00" in content
    assert "收入" not in content and "到账" not in content


@pytest.mark.parametrize("reason,expected", [
    ("UNINTENDED_PURCHASE", "误购"), ("FULFILLMENT_ISSUE", "收取或使用内购内容遇到问题"),
    ("UNSATISFIED_WITH_PURCHASE", "对购买内容不满意"), ("LEGAL", "法律原因"),
    ("OTHER", "其他原因"), (None, "Apple 未提供"), ("NEW_REASON", "未知分类（NEW_REASON）"),
])
def test_refund_application_reason_is_not_a_refund_result(reason, expected):
    """未知分类、缺失值和 OTHER 不混淆；文案不冒充用户自由文本或已完成退款。"""
    from dwy_webhooks.apple import apple_notification_content

    content = apple_notification_content(notification("CONSUMPTION_REQUEST",
                                        consumption_request_reason=reason))
    assert "用户申请退款（待 Apple 审核）" in content
    assert f"申请原因（用户选择分类）：{expected}" in content
    assert "退款成功" not in content


@pytest.mark.parametrize("reason,expected", [
    (0, "其他原因（例如误购）"), (1, "应用内实际或用户感知的问题"),
    (None, "Apple 未提供"), (99, "未知分类（99）"),
])
def test_refund_result_uses_apple_classification_and_original_price(reason, expected):
    """0 是有效分类，原交易价格不能展示成实际退款金额。"""
    from dwy_webhooks.apple import AppleTransactionDetails, apple_notification_content

    content = apple_notification_content(notification("REFUND", transaction_details=AppleTransactionDetails(
        revocation_reason=reason, price_milliunits=14990, currency="AUD",
    )))
    assert f"退款原因（Apple 分类）：{expected}" in content
    assert "原交易金额：14.99 AUD" in content and "退款金额：" not in content


def test_renewal_and_old_notice_construction_remain_portable():
    """旧八字段及安全数据白名单保持兼容；续订设置不冒充权益变化。"""
    from dwy_webhooks.apple import AppleRenewalDetails, apple_notification_content

    notice = notification("DID_CHANGE_RENEWAL_STATUS", subtype="AUTO_RENEW_DISABLED",
                          product_id="monthly", transaction_id="tx", renewal_details=AppleRenewalDetails(
                              original_transaction_id="original", auto_renew_status=0,
                              renewal_price_milliunits=1990, currency="USD", expiration_intent=2,
                              is_in_billing_retry_period=True,
                          ))
    content = apple_notification_content(notice)
    for value in ("Apple · 已关闭自动续订", "当前有效期不受影响", "自动续订：已关闭", "下期价格：1.99 USD",
                  "到期原因：扣款失败", "扣款重试：是", "商品：monthly", "交易编号：tx"):
        assert value in content
    assert set(notice.public_data()) == {
        "notification_id", "bundle_id", "environment", "notification_type", "subtype", "signed_at",
        "product_id", "transaction_id",
    }


@pytest.mark.parametrize("name", ["", "x" * 101, "line\nbreak"])
def test_direct_formatter_rejects_invalid_brand_name(name):
    """独立调用同样约束注入名称，错误不回显输入。"""
    from dwy_webhooks.apple import apple_notification_content

    with pytest.raises(ValueError, match="^Invalid Apple application name$"):
        apple_notification_content(notification(), app_name=name)


@pytest.mark.parametrize("name", ["   ", "line\nbreak", "control\x7f"])
def test_application_config_rejects_names_that_cannot_be_formatted(name):
    """错误名称应在配置时失败，不等收到有效 Apple 回调才变成 500。"""
    from dwy_webhooks.config import AppleNotificationApp

    with pytest.raises(ValueError, match="Invalid Apple application name"):
        AppleNotificationApp(name=name, bundle_id="com.example.other", environment="Sandbox",
                             root_certificates=(b"offline",))


async def test_shared_sender_receives_portable_content_and_username_override(monkeypatch):
    """真实 Discord HTTP JSON 可独立使用，既不导入 App Cloud，也不需要其数据库。"""
    from dwy_webhooks.apple import apple_notification_content
    from dwy_webhooks.discord import DiscordWebhookSender

    requests = []

    def receive(request):
        """离线捕获 SDK 构造的请求。"""
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "123456789"})

    original = httpx.AsyncClient
    monkeypatch.setattr("dwy_webhooks.discord.discord_client",
                        lambda: original(transport=httpx.MockTransport(receive)))
    content = apple_notification_content(notification("CONSUMPTION_REQUEST",
                                        consumption_request_reason="UNINTENDED_PURCHASE"), app_name="Example")
    sender = DiscordWebhookSender(
        "https://discord.com/api/webhooks/123456789/test-token", username="Team Apple",
    )
    await sender(content)
    assert requests[0]["username"] == "Team Apple"
    assert "Example · 用户申请退款" in requests[0]["content"]
    assert "误购" in requests[0]["content"]
    assert requests[0]["allowed_mentions"] == {"parse": []}


def test_content_respects_utf16_limit_and_keeps_reason():
    """业务无关长标识也必须符合 Discord 的消息限制。"""
    from dwy_webhooks.apple import AppleRenewalDetails, AppleTransactionDetails, apple_notification_content

    notice = notification("CONSUMPTION_REQUEST", consumption_request_reason="UNINTENDED_PURCHASE",
                          subtype="😀" * 100, product_id="😀" * 255, transaction_id="😀" * 128,
                          transaction_details=AppleTransactionDetails(product_id="😀" * 255,
                                                                      transaction_id="😀" * 128))
    notice = replace(notice, notification_id="😀" * 128, renewal_details=AppleRenewalDetails(
        original_transaction_id="original", auto_renew_product_id="😀" * 255,
    ))
    content = apple_notification_content(notice, app_name="😀" * 100)
    assert len(content.encode("utf-16-le")) // 2 <= 2000
    assert "申请原因（用户选择分类）：误购" in content
