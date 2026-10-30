"""业务无关的 Apple 通知文案；品牌由项目注入，传输复用现有 Discord 发送器。"""

from datetime import UTC, datetime
from decimal import Decimal

from ..validation import validate_apple_app_name
from .apple_models import AppleRenewalDetails, VerifiedAppleNotification

_LABELS = {
    "ONE_TIME_CHARGE": "内购购买事件", "SUBSCRIBED": "订阅已开始", "DID_RENEW": "订阅续订成功",
    "DID_CHANGE_RENEWAL_STATUS": "自动续订设置变更", "DID_CHANGE_RENEWAL_PREF": "订阅方案变更",
    "DID_FAIL_TO_RENEW": "订阅续订失败", "EXPIRED": "订阅已到期", "GRACE_PERIOD_EXPIRED": "订阅宽限期已结束",
    "CONSUMPTION_REQUEST": "用户申请退款（待 Apple 审核）", "REFUND": "退款成功",
    "REFUND_DECLINED": "退款申请未获批准", "REFUND_REVERSED": "退款已撤销",
    "REVOKE": "家庭共享授权已撤销", "TEST": "Apple 测试通知",
}
_REQUEST_REASONS = {
    "UNINTENDED_PURCHASE": "误购", "FULFILLMENT_ISSUE": "收取或使用内购内容遇到问题",
    "UNSATISFIED_WITH_PURCHASE": "对购买内容不满意", "LEGAL": "法律原因", "OTHER": "其他原因",
}
_REFUND_REASONS = {0: "其他原因（例如误购）", 1: "应用内实际或用户感知的问题"}
_EXPIRATION_REASONS = {
    1: "用户取消订阅", 2: "扣款失败", 3: "未同意涨价或优惠转换", 4: "续订时商品不可用", 5: "其他原因",
}


def _category(value, labels) -> str:
    """缺失和未知分类分别展示，有效值 0 不能当成缺失。"""
    return "Apple 未提供" if value is None else labels.get(value, f"未知分类（{value}）")


def _money(price: int | None, currency: str | None) -> str:
    """整数毫单位精确换算，Apple 价格已包含数量；缺失事实不补造。"""
    if price is None or currency is None:
        return "Apple 未提供（金额或币种缺失）"
    amount = format(Decimal(price) / Decimal(1000), ".3f").rstrip("0").rstrip(".")
    return f"{amount} {currency}"


def _date(value: datetime) -> str:
    """带时区的 UTC 时间，区分购买和签名时间。"""
    return value.astimezone(UTC).isoformat(timespec="seconds")


def _renewal_lines(info: AppleRenewalDetails) -> list[str]:
    """续订设置不代表已付款，也不撤销本期有效期。"""
    lines = ["自动续订：" + _category(info.auto_renew_status, {0: "已关闭", 1: "已开启"})]
    if info.auto_renew_product_id is not None:
        lines.append(f"下期商品：{info.auto_renew_product_id}")
    if info.renewal_price_milliunits is not None or info.currency is not None:
        lines.append("下期价格：" + _money(info.renewal_price_milliunits, info.currency))
    if info.renewal_date is not None:
        lines.append("本期结束时间（Apple 续订信息）：" + _date(info.renewal_date))
    if info.expiration_intent is not None:
        lines.append("到期原因：" + _category(info.expiration_intent, _EXPIRATION_REASONS))
    if info.is_in_billing_retry_period is not None:
        lines.append("扣款重试：" + ("是" if info.is_in_billing_retry_period else "否"))
    if info.grace_period_expires_date is not None:
        lines.append("宽限期至：" + _date(info.grace_period_expires_date))
    return lines


def apple_notification_content(notice: VerifiedAppleNotification, *, app_name: str = "Apple") -> str:
    """格式化安全事实，优先保留退款原因；名称可注入，消息最多 2000 UTF-16 单位。"""
    app_name = validate_apple_app_name(app_name)
    label = _LABELS.get(notice.notification_type, "Apple 内购状态更新")
    if notice.notification_type == "DID_CHANGE_RENEWAL_STATUS":
        label = {
            "AUTO_RENEW_DISABLED": "已关闭自动续订（当前有效期不受影响）",
            "AUTO_RENEW_ENABLED": "已恢复自动续订",
        }.get(notice.subtype, label)
    tx = notice.transaction_details
    family_shared = tx is not None and tx.ownership_type == "FAMILY_SHARED"
    if family_shared:
        label = {
            "ONE_TIME_CHARGE": "家庭共享内购授权",
            "SUBSCRIBED": "家庭成员已获得订阅共享",
            "DID_RENEW": "家庭共享订阅已续期",
        }.get(notice.notification_type, label)
    event = notice.notification_type + (f" / {notice.subtype}" if notice.subtype else "")
    lines = [f"{app_name} · {label}", f"环境：{notice.environment}", f"事件：{event}"]
    if notice.notification_type == "CONSUMPTION_REQUEST":
        reason = _category(notice.consumption_request_reason, _REQUEST_REASONS)
        lines.append("申请原因（用户选择分类）：" + reason)
    if notice.notification_type == "REFUND":
        reason = tx.revocation_reason if tx else None
        lines.append("退款原因（Apple 分类）：" + _category(reason, _REFUND_REASONS))
    if notice.notification_type == "REFUND_DECLINED":
        lines.append("驳回原因：Apple 未提供")
    if tx:
        amount_label = "原交易金额" if notice.notification_type in {
            "CONSUMPTION_REQUEST", "REFUND", "REFUND_DECLINED", "REFUND_REVERSED",
        } else "交易金额"
        if family_shared:
            amount_label = "原订阅价格" if tx.expires_date is not None else "原交易金额"
        amount = _money(tx.price_milliunits, tx.currency)
        if family_shared:
            amount += "（家庭共享，无新增付款）"
        lines.extend([
            f"{amount_label}：{amount}",
            f"购买地区：{tx.storefront or 'Apple 未提供'}（App Store 店面）",
            "购买时间：" + (_date(tx.purchase_date) if tx.purchase_date is not None else "Apple 未提供"),
            "购买归属：" + _category(tx.ownership_type, {
                "PURCHASED": "本人购买", "FAMILY_SHARED": "家庭共享",
            }),
        ])
        if tx.expires_date:
            lines.append("有效期至：" + _date(tx.expires_date))
        if tx.revocation_date:
            lines.append("退款/撤销时间：" + _date(tx.revocation_date))
    if notice.renewal_details is not None:
        lines.extend(_renewal_lines(notice.renewal_details))
    product_id = notice.product_id if notice.product_id is not None else (tx.product_id if tx else None)
    transaction_id = (notice.transaction_id if notice.transaction_id is not None
                      else (tx.transaction_id if tx else None))
    if product_id is not None:
        lines.append(f"商品：{product_id}")
    if transaction_id is not None:
        lines.append(f"交易编号：{transaction_id}")
    lines.extend([f"通知编号：{notice.notification_id}", "Apple 签名时间：" + _date(notice.signed_at)])
    content = "\n".join(lines)
    encoded = content.encode("utf-16-le")
    return content if len(encoded) <= 4000 else encoded[:3998].decode("utf-16-le", errors="ignore") + "…"
