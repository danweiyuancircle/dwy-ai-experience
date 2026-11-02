"""微信支付独立来源包；核心导入不加载 FastAPI 或宿主支付模块。"""

from .events import wechatpay_notification_event
from .models import (
    ConfirmedWechatPayResult,
    PaymentNotificationContext,
    VerifiedPaymentNotification,
    VerifiedRefundNotification,
    WechatPayNotifyConfig,
)
from .verifier import WechatPayNotificationVerifier, WechatPayVerificationError

__version__ = "0.1.0"
__all__ = [
    "ConfirmedWechatPayResult",
    "PaymentNotificationContext",
    "VerifiedPaymentNotification",
    "VerifiedRefundNotification",
    "WechatPayNotificationVerifier",
    "WechatPayNotifyConfig",
    "WechatPayVerificationError",
    "install_wechatpay_notifications",
    "wechatpay_notification_event",
]


def install_wechatpay_notifications(app, config: WechatPayNotifyConfig, *, verifier, sink) -> None:
    """安装可选 FastAPI 路由；调用前安装 [fastapi] extra 并显式提供持久 sink。"""
    from .fastapi import install_wechatpay_notifications as install

    install(app, config, verifier=verifier, sink=sink)
