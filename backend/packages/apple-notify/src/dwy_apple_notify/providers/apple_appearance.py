"""仅按已验签事件与交易事实分类；价格不是状态通知产生收入的证据。"""

from dwy_notify import NotificationAppearance

from .._assets import ASSET_BASE_URL
from .apple_models import VerifiedAppleNotification

DEFAULT_APPEARANCE = NotificationAppearance(username="购买通知", avatar_url=f"{ASSET_BASE_URL}/purchase.png")

# 新资源随下一版 Apple 包的不可变标签公开，旧资源地址保持不变。
_IAP_ASSET_BASE_URL = (
    "https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/"
    "dwy-apple-notify@0.1.7/backend/packages/apple-notify/src/dwy_apple_notify/assets"
)
SUBSCRIPTION_APPEARANCE = NotificationAppearance(
    username="订阅购买", avatar_url=f"{_IAP_ASSET_BASE_URL}/subscription.png",
)
BUYOUT_APPEARANCE = NotificationAppearance(username="买断购买", avatar_url=f"{ASSET_BASE_URL}/purchase.png")
REFUND_APPEARANCE = NotificationAppearance(
    username="退款通知", avatar_url=f"{_IAP_ASSET_BASE_URL}/refund.png",
)
ACTIVITY_APPEARANCE = NotificationAppearance(username="内购动态", avatar_url=f"{ASSET_BASE_URL}/general.png")


def apple_notification_appearance(notice: VerifiedAppleNotification) -> NotificationAppearance:
    """返回逐事件默认展示，不代表银行到账；显式应用展示仍由通知器优先覆盖。"""
    if notice.environment != "Production":
        return ACTIVITY_APPEARANCE
    if notice.notification_type == "REFUND":
        return REFUND_APPEARANCE
    tx = notice.transaction_details
    if (tx is None or tx.ownership_type != "PURCHASED" or tx.price_milliunits is None
            or tx.price_milliunits == 0 or tx.currency is None or tx.transaction_id is None
            or tx.purchase_date is None or tx.revocation_date is not None):
        return ACTIVITY_APPEARANCE
    event = (notice.notification_type, notice.subtype)
    if tx.product_type == "Auto-Renewable Subscription" and event in {
        ("SUBSCRIBED", "INITIAL_BUY"), ("SUBSCRIBED", "RESUBSCRIBE"),
        ("DID_RENEW", None), ("DID_RENEW", "BILLING_RECOVERY"),
        ("DID_CHANGE_RENEWAL_PREF", "UPGRADE"), ("OFFER_REDEEMED", "UPGRADE"),
    }:
        return SUBSCRIPTION_APPEARANCE
    if tx.product_type == "Non-Consumable" and event == ("ONE_TIME_CHARGE", None):
        return BUYOUT_APPEARANCE
    return ACTIVITY_APPEARANCE
