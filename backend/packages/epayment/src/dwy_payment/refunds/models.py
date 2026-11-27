"""退款意图及渠道最终结果；不对父支付行建立外键，独立事务不等待父行锁。"""

from datetime import datetime

from dwyeapi import dt
from dwyeapi.database import Base, TimestampMixin
from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class RefundRecord(Base, TimestampMixin):
    """一行一退款号；原额/申请额是不可变快照，business_processed仅表示本地权益操作。"""

    __tablename__ = "payment_refunds"
    __table_args__ = (
        CheckConstraint("refund_fen > 0 AND refund_fen <= amount_fen", name="ck_payment_refunds_amount"),
        CheckConstraint("source IN ('app', 'external')", name="ck_payment_refunds_source"),
        Index("ix_payment_refunds_due", "next_query_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(32), index=True, comment="父支付单号，不设外键")
    refund_no: Mapped[str] = mapped_column(String(64), unique=True, comment="稳定商户退款号")
    transaction_id: Mapped[str] = mapped_column(String(64), comment="原渠道交易号快照")
    provider_refund_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount_fen: Mapped[int] = mapped_column(Integer, comment="原支付分")
    refund_fen: Mapped[int] = mapped_column(Integer, comment="本次申请退款分")
    source: Mapped[str] = mapped_column(String(16), comment="app或商户后台external")
    provider_status: Mapped[str] = mapped_column(String(16), default="REQUESTED")
    verified_status: Mapped[str | None] = mapped_column(String(16), nullable=True, comment="已核验并登记通知的终态")
    business_processed: Mapped[bool] = mapped_column(Boolean, default=False, comment="本地权益操作已提交")
    next_query_at: Mapped[datetime | None] = mapped_column(DateTime, default=dt.now, nullable=True)
    last_query_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    manual_required: Mapped[bool] = mapped_column(Boolean, default=False, comment="超过24小时，人工告警已登记")
    version: Mapped[int] = mapped_column(Integer, default=0, comment="并发结果更新CAS版本")
