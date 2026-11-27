"""Apple 通知的安全展示事实；不含原始 JWS、账户 token 或产品权益策略。"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, TypeAdapter

PriceMilliunits = Annotated[int, Field(strict=True, ge=0, le=2**63 - 1)]
CurrencyCode = Annotated[str, Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")]
RefundRequestReason = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Z0-9_]+$")]
_REFUND_REASON = TypeAdapter(RefundRequestReason | None)


class AppleTransactionDetails(BaseModel):
    """与业务交易账本无关的展示白名单；缺失事实保持 None，不虚构免费或购买归属。"""

    model_config = ConfigDict(frozen=True, extra="forbid")
    transaction_id: str | None = Field(default=None, min_length=1, max_length=128)
    original_transaction_id: str | None = Field(default=None, min_length=1, max_length=128)
    product_id: str | None = Field(default=None, min_length=1, max_length=255)
    purchase_date: AwareDatetime | None = None
    expires_date: AwareDatetime | None = None
    revocation_date: AwareDatetime | None = None
    ownership_type: str | None = Field(default=None, max_length=32)
    price_milliunits: PriceMilliunits | None = None
    currency: CurrencyCode | None = None
    storefront: str | None = Field(default=None, min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    revocation_reason: int | None = Field(default=None, ge=0, le=2**31 - 1, strict=True)


class AppleRenewalDetails(BaseModel):
    """独立验签的续订设置，只用于展示，不覆盖当前已付有效期。"""

    model_config = ConfigDict(frozen=True, extra="forbid")
    original_transaction_id: str = Field(min_length=1, max_length=128)
    auto_renew_product_id: str | None = Field(default=None, max_length=255)
    auto_renew_status: int | None = Field(default=None, ge=0, le=2**31 - 1, strict=True)
    renewal_price_milliunits: PriceMilliunits | None = None
    currency: CurrencyCode | None = None
    renewal_date: AwareDatetime | None = None
    expiration_intent: int | None = Field(default=None, ge=1, le=2**31 - 1, strict=True)
    is_in_billing_retry_period: bool | None = Field(default=None, strict=True)
    grace_period_expires_date: AwareDatetime | None = None


@dataclass(frozen=True, slots=True)
class VerifiedAppleNotification:
    """保留原八字段构造合同，追加安全详情；不表达用户账户或购买权益。"""

    notification_id: str
    bundle_id: str
    environment: str
    notification_type: str
    signed_at: datetime
    subtype: str | None = None
    product_id: str | None = None
    transaction_id: str | None = None
    transaction_details: AppleTransactionDetails | None = None
    renewal_details: AppleRenewalDetails | None = None
    consumption_request_reason: str | None = None

    def public_data(self) -> dict[str, str | None]:
        """保持原回调八字段白名单；详情显式从对象读取，不扩大旧事件数据合同。"""
        return {
            "notification_id": self.notification_id, "bundle_id": self.bundle_id,
            "environment": self.environment, "notification_type": self.notification_type,
            "subtype": self.subtype, "signed_at": self.signed_at.isoformat(),
            "product_id": self.product_id, "transaction_id": self.transaction_id,
        }


def _date(milliseconds) -> datetime:
    """Apple 时间是 UTC 毫秒，拒绝布尔值、缺失和不可表示的时间。"""
    if isinstance(milliseconds, bool) or not isinstance(milliseconds, (int, float)):
        raise ValueError("invalid notification date")
    return datetime.fromtimestamp(milliseconds / 1000, UTC)


def _optional_date(milliseconds) -> datetime | None:
    """可选时间缺失时不补造时间；有值时与通知日期使用相同边界。"""
    return None if milliseconds is None else _date(milliseconds)


def _enum_value(decoded, name):
    """SDK 将未来未知枚举保存在 raw 字段，不能把它误报为 OTHER 或缺失。"""
    value = getattr(decoded, name, None)
    if value is None:
        value = getattr(decoded, "raw" + name[0].upper() + name[1:], None)
    return getattr(value, "value", value)


def apple_transaction_details(decoded) -> AppleTransactionDetails:
    """仅映射已经过官方验签的交易对象；本函数本身不验签、不读取账户 token。"""
    return AppleTransactionDetails(
        transaction_id=decoded.transactionId, original_transaction_id=decoded.originalTransactionId,
        product_id=decoded.productId, purchase_date=_optional_date(decoded.purchaseDate),
        expires_date=_optional_date(decoded.expiresDate),
        revocation_date=_optional_date(decoded.revocationDate),
        ownership_type=_enum_value(decoded, "inAppOwnershipType"), price_milliunits=decoded.price,
        currency=decoded.currency, storefront=decoded.storefront,
        revocation_reason=_enum_value(decoded, "revocationReason"),
    )


def apple_renewal_details(decoded) -> AppleRenewalDetails:
    """消费独立验签及交易关联核对之后的续订信息，不处理权益或自动退款。"""
    return AppleRenewalDetails(
        original_transaction_id=decoded.originalTransactionId,
        auto_renew_product_id=decoded.autoRenewProductId,
        auto_renew_status=_enum_value(decoded, "autoRenewStatus"),
        renewal_price_milliunits=decoded.renewalPrice,
        currency=decoded.currency, renewal_date=_optional_date(decoded.renewalDate),
        expiration_intent=_enum_value(decoded, "expirationIntent"),
        is_in_billing_retry_period=decoded.isInBillingRetryPeriod,
        grace_period_expires_date=_optional_date(decoded.gracePeriodExpiresDate),
    )


def apple_refund_request_reason(data) -> str | None:
    """读取已验签 data 中的用户选择分类，不存在用户自由文本或默认 OTHER。"""
    return _REFUND_REASON.validate_python(_enum_value(data, "consumptionRequestReason"))
