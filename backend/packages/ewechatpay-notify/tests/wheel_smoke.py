"""在独立已安装 wheel 环境执行，不需要 FastAPI 或宿主支付模块。"""

import sys

from dwy_wechatpay_notify import ConfirmedWechatPayResult, __version__, wechatpay_notification_event

assert "fastapi" not in sys.modules
assert "dwy_payment" not in sys.modules
assert __version__ == "0.1.1"
result = ConfirmedWechatPayResult(
    event_type="TRANSACTION.SUCCESS",
    order_no="order123",
    transaction_id="wx123",
    amount_fen=1,
    trade_type="NATIVE",
    trade_state="SUCCESS",
)
event = wechatpay_notification_event(result, scope="wheel-smoke")
assert event.source == "wechatpay"
assert event.event_id == "wechat:payment:order123:success"
assert "provider_event_id" not in event.data
assert "0.01" in event.content
assert len(event.content.encode()) <= 1800
print("dwy-wechatpay-notify installed wheel smoke passed")
