"""由发布流程在仓库外干净环境运行，只验真实已安装wheel。"""

import importlib.util
from importlib.metadata import version

import dwy_payment
from dwy_payment import NoOpPaymentHook, PaymentConfig
from dwy_payment.events import PaymentEvent
from dwy_payment.gateways.wechat_native import WechatNativeGateway
from dwy_payment.models import PaymentOrder
from dwy_payment.refunds.models import RefundRecord

assert version("dwy-payment") == "0.3.0"
assert importlib.util.find_spec("dwy_shared") is None
assert importlib.util.find_spec("dwy_auth") is None
assert importlib.util.find_spec("app") is None
assert importlib.util.find_spec("quant_billing") is None
assert importlib.util.find_spec("alipay") is None
assert not hasattr(dwy_payment, "register")
assert PaymentOrder.metadata is RefundRecord.metadata is PaymentEvent.metadata
assert NoOpPaymentHook() is not None
assert not WechatNativeGateway(PaymentConfig().wechat).is_configured()
print("dwy-payment installed core wheel: OK")
