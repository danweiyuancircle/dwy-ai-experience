"""显式配置及已验证/已确认结果；不包含凭据或宿主账本模型。"""

from datetime import datetime
from typing import Annotated, Literal

from dwy_notify import NotificationField
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_*|@-]+$")]
OrderNo = Annotated[str, Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_*|@-]+$")]
EventType = Literal["TRANSACTION.SUCCESS", "REFUND.SUCCESS", "REFUND.ABNORMAL", "REFUND.CLOSED"]
Money = Annotated[int, Field(strict=True, gt=0, le=999999999999)]
Scope = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[^\x00-\x20\x7f]+$")]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class WechatPayNotifyConfig(_Model):
    """固定直连商户/应用身份；SDK 和私钥由宿主提供，不读取环境变量。"""

    mchid: Annotated[str, Field(min_length=1, max_length=32, pattern=r"^[0-9]+$")]
    appid: Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
    scope: Scope
    max_body_bytes: int = Field(default=65536, strict=True, ge=1, le=1048576)
    path: str = Field(default="/webhooks/wechatpay", max_length=256, pattern=r"^/(?:[A-Za-z0-9_-]+/?)+$")


class PaymentNotificationContext(_Model):
    """宿主投影业务快照；资料须显式选择 extra_fields，禁止自动转发账号或原始报文。"""

    description: str = Field(default="", max_length=1024)
    outcome: str = Field(default="", max_length=1024)
    extra_fields: tuple[NotificationField, ...] = Field(default=(), max_length=8)

    @field_validator("extra_fields")
    @classmethod
    def distinct_display_fields(cls, values: tuple[NotificationField, ...]) -> tuple[NotificationField, ...]:
        """展示标签不能冒充支付固定字段，也不能用重复标签制造歧义。"""
        reserved = {
            "订单号", "微信交易号", "金额", "退款单号", "微信退款号", "原金额", "退款金额",
            "事件时间", "商品", "业务结果",
        }
        labels = [value.label.strip() for value in values]
        if len(labels) != len(set(labels)) or reserved.intersection(labels):
            raise ValueError("custom notification labels must be distinct and non-reserved")
        return values

    @field_validator("description", "outcome")
    @classmethod
    def printable_text(cls, value: str) -> str:
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("context must be printable single-line text")
        return value


class _Result(_Model):
    event_type: EventType
    order_no: OrderNo
    transaction_id: Identifier
    amount_fen: Money
    provider_event_id: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$"
    )
    trade_type: Literal["JSAPI", "NATIVE", "APP", "MWEB", "MICROPAY"] | None = None
    trade_state: Literal["SUCCESS"] | None = None
    refund_no: Identifier | None = None
    refund_id: Identifier | None = None
    refund_fen: Money | None = None
    refund_status: Literal["SUCCESS", "ABNORMAL", "CLOSED"] | None = None
    occurred_at: datetime | None = None

    @model_validator(mode="after")
    def consistent_result(self):
        if self.occurred_at is not None and self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")
        if self.event_type == "TRANSACTION.SUCCESS":
            if self.trade_type is None or self.trade_state != "SUCCESS":
                raise ValueError("successful payment requires trade type and state")
            if any(
                value is not None
                for value in (self.refund_no, self.refund_id, self.refund_fen, self.refund_status)
            ):
                raise ValueError("payment must not contain refund fields")
        else:
            if any(
                value is None
                for value in (self.refund_no, self.refund_id, self.refund_fen, self.refund_status)
            ):
                raise ValueError("refund requires identifiers, amount and status")
            if self.refund_status != self.event_type.removeprefix("REFUND."):
                raise ValueError("refund event and status mismatch")
            if self.refund_fen > self.amount_fen:
                raise ValueError("refund exceeds original amount")
            if self.trade_state is not None or self.trade_type is not None:
                raise ValueError("refund must not contain payment state")
        return self


class VerifiedPaymentNotification(_Result):
    """仅由通过 SDK 验签与应用身份核对的付款回调构造；不是入账证明。"""

    event_type: Literal["TRANSACTION.SUCCESS"] = "TRANSACTION.SUCCESS"
    provider_event_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    trade_type: Literal["JSAPI", "NATIVE", "APP", "MWEB", "MICROPAY"]
    trade_state: Literal["SUCCESS"]


class VerifiedRefundNotification(_Result):
    """官方退款状态；ABNORMAL/CLOSED 不表示退款成功，不推导宿主权益状态。"""

    event_type: Literal["REFUND.SUCCESS", "REFUND.ABNORMAL", "REFUND.CLOSED"]
    provider_event_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    refund_no: Identifier
    refund_id: Identifier
    refund_fen: Money
    refund_status: Literal["SUCCESS", "ABNORMAL", "CLOSED"]


class ConfirmedWechatPayResult(_Result):
    """宿主已确认的渠道/账本结果；查单缺少官方事件 ID 时保持 None，不得伪造。"""
