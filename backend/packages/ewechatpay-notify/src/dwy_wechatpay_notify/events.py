"""付款/退款与主动查单共用业务去重键，向统一通知出口投递安全元数据。"""

from dwy_notify import NotificationField, render_notification_fields
from dwy_notify.events import NotificationEvent
from pydantic import TypeAdapter

from .models import (
    ConfirmedWechatPayResult,
    PaymentNotificationContext,
    Scope,
    VerifiedPaymentNotification,
    VerifiedRefundNotification,
)


def _money(fen: int) -> str:
    return f"{fen // 100}.{fen % 100:02d}"


def _context_field(label: str, value: str) -> tuple[NotificationField, ...]:
    # 旧上下文允许空白及格式字符；新增展示能力不能让这些历史输入阻断支付事务。
    value = "".join(char for char in value if char.isprintable()).strip()
    if not value:
        return ()
    value = value if len(value) <= 256 else value[:255] + "…"
    return (NotificationField(label=label, value=value),)


def wechatpay_notification_event(
    result: VerifiedPaymentNotification | VerifiedRefundNotification | ConfirmedWechatPayResult,
    *,
    scope: str,
    context: PaymentNotificationContext | None = None,
) -> NotificationEvent:
    """只接受类型化结果；scope 隔离商户，收到官方事件本身不证明本地已入账。"""
    if not isinstance(
        result, (VerifiedPaymentNotification, VerifiedRefundNotification, ConfirmedWechatPayResult)
    ):
        raise TypeError("result must be a verified or confirmed Wechat Pay result")
    if context is not None and not isinstance(context, PaymentNotificationContext):
        raise TypeError("context must be PaymentNotificationContext")
    scope = TypeAdapter(Scope).validate_python(scope)
    payment = result.event_type == "TRANSACTION.SUCCESS"
    if payment:
        event_id = f"wechat:payment:{result.order_no}:success"
        lines = [
            "微信支付成功",
            f"订单号：{result.order_no}",
            f"微信交易号：{result.transaction_id}",
            f"金额：CNY {_money(result.amount_fen)}",
        ]
    else:
        status = {"SUCCESS": "成功", "ABNORMAL": "异常", "CLOSED": "关闭"}[result.refund_status]
        event_id = f"wechat:refund:{result.refund_no}:{result.refund_status}"
        lines = [
            f"微信退款{status}",
            f"订单号：{result.order_no}",
            f"微信交易号：{result.transaction_id}",
            f"退款单号：{result.refund_no}",
            f"微信退款号：{result.refund_id}",
            f"原金额：CNY {_money(result.amount_fen)}",
            f"退款金额：CNY {_money(result.refund_fen)}",
        ]
    if result.occurred_at is not None:
        lines.append(f"事件时间：{result.occurred_at.isoformat()}")
    if context is not None and context.extra_fields:
        # 附加资料先于可选商品描述分配预算；固定金融事实始终保留。
        for fields in (
            _context_field("业务结果", context.outcome),
            context.extra_fields,
            _context_field("商品", context.description),
        ):
            rendered = render_notification_fields(
                fields,
                max_bytes=1800 - len("\n".join(lines).encode("utf8")) - 1,
            )
            if rendered:
                lines.append(rendered)
    elif context is not None:
        for label, value in (("商品", context.description), ("业务结果", context.outcome)):
            if value and len(("\n".join(lines) + f"\n{label}：{value}").encode("utf8")) <= 1800:
                lines.append(f"{label}：{value}")
    content = "\n".join(lines)
    if len(content.encode("utf8")) > 1800:
        raise ValueError("notification content exceeds UTF8 byte budget")
    # 宿主可继承结果模型；出口白名单不能随子类或后续模型字段自动扩张。
    data = result.model_dump(
        include={
            "event_type",
            "order_no",
            "transaction_id",
            "amount_fen",
            "provider_event_id",
            "trade_type",
            "trade_state",
            "refund_no",
            "refund_id",
            "refund_fen",
            "refund_status",
            "occurred_at",
        },
        exclude_none=True,
        mode="json",
    )
    return NotificationEvent(
        source="wechatpay",
        scope=scope,
        event_id=event_id,
        event_type=result.event_type,
        content=content,
        data=data,
    )
