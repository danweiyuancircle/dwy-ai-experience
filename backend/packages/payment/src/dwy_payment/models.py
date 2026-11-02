"""支付流水。一行是一笔渠道收款,user_id 只是调用方标识,不外键到用户表。"""

import uuid as uuid_lib
from datetime import datetime

from dwyeapi.database import Base, TimestampMixin
from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from dwy_payment.constants import (
    AMOUNT_FEN_MAX,
    DESCRIPTION_MAX_LEN,
    ORDER_NO_MAX_LEN,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_REFUND,
    STATUS_SUCCESS,
    USER_ID_MAX_LEN,
)


class PaymentOrder(Base, TimestampMixin):
    """渠道支付流水。

    成功、失败、退款都记在这张表。退款列保留既有权益政策，渠道最终到账证据在RefundRecord。
    """

    __tablename__ = "payment_orders"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{STATUS_PENDING}', '{STATUS_SUCCESS}', '{STATUS_FAILED}', '{STATUS_REFUND}')",
            name="ck_payment_orders_status",
        ),
        CheckConstraint(
            f"amount_fen >= 1 AND amount_fen <= {AMOUNT_FEN_MAX}",
            name="ck_payment_orders_amount",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="内部主键,不对外")
    uuid: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid_lib.uuid4()),
        unique=True,
        index=True,
        comment="对外 uuid。业务回对用 order_no,不用本字段",
    )
    # 调用方传入。各项目用户主键类型不同,所以用字符串,不做外键。
    user_id: Mapped[str] = mapped_column(String(USER_ID_MAX_LEN), index=True, comment="调用方用户标识")
    idempotency_key: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, comment="宿主提供的稳定支付意图键，商户实例内唯一"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="原下单截止快照，重试不得按当前配置延长；旧记录未知"
    )
    order_no: Mapped[str] = mapped_column(
        String(ORDER_NO_MAX_LEN),
        unique=True,
        index=True,
        comment="商户订单号,下单与回调的回对键",
    )
    amount_fen: Mapped[int] = mapped_column(Integer, comment="应收金额,单位分,回调必须与此相等")
    channel: Mapped[str] = mapped_column(String(16), comment="渠道:wechat 或 alipay")
    channel_trade_no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="渠道交易号")
    status: Mapped[str] = mapped_column(String(16), default=STATUS_PENDING, comment="pending/success/failed/refund")
    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LEN), comment="商品描述,送给渠道")
    code_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Native 二维码链接")
    # 部分退也停在 refund。amount_fen 保持原实付,已退金额单独记,避免对账时分不清实收和实退。
    refunded_fen: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        comment="本地退款处理分，渠道最终到账以独立退款记录为准",
    )
    refund_no: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        comment="商户退款单号。同一支付单固定,渠道重试幂等",
    )
    notify_payload: Mapped[str | None] = mapped_column(Text, nullable=True, comment="最近一次解密回调,不回给前端")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="软删除标记")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="软删除时间")
