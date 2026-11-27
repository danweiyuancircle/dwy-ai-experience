"""支付流水的对外响应。不包含内部 id、回调原文和密钥。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentOrderResponse(BaseModel):
    """当前用户可见的一笔支付流水。"""

    order_no: str = Field(description="商户订单号")
    user_id: str = Field(description="下单时传入的用户标识")
    amount_fen: int = Field(description="金额,单位分")
    refunded_fen: int = Field(default=0, description="已退金额,单位分。未退为 0")
    refund_no: str | None = Field(default=None, description="商户退款单号。未退为空")
    status: str = Field(description="pending/success/failed/refund")
    channel: str = Field(description="渠道")
    channel_trade_no: str | None = Field(description="渠道交易号,未支付时为空")
    code_url: str | None = Field(description="Native 二维码链接,下单失败时为空")
    description: str = Field(description="商品描述")
    created_at: datetime = Field(description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class PaymentEcho(BaseModel):
    """下单或支付成功后吐回的回对字段。项目用这三项和自己的桥接单比较。"""

    user_id: str = Field(description="调用方用户标识")
    amount_fen: int = Field(description="金额,单位分")
    order_no: str = Field(description="商户订单号")
    code_url: str | None = Field(description="二维码链接")
    status: str = Field(description="当前流水状态")
    channel: str = Field(default="wechat", description="渠道:wechat 或 alipay")
