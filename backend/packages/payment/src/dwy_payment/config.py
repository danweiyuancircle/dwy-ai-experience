"""支付配置。

凭证全部走环境变量,空配置也能启动;缺字段时下单失败,不在导入期连微信。
"""

from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class WechatPayConfig(BaseModel):
    """微信支付普通商户 APIv3 Native 凭证。公钥模式,不下载平台证书。"""

    model_config = ConfigDict(hide_input_in_errors=True)

    mchid: str = Field(default="", max_length=32, description="商户号")
    appid: str = Field(default="", max_length=32, description="Native 下单 appid,须已绑定该商户号")
    private_key: str = Field(default="", max_length=8192, repr=False, exclude=True,
                             description="商户 API 私钥 PEM,可用 \\n 表示换行")
    cert_serial: str = Field(default="", max_length=64, description="商户 API 证书序列号")
    public_key: str = Field(default="", max_length=8192, description="微信支付公钥 PEM")
    public_key_id: str = Field(default="", max_length=128, description="微信支付公钥 ID,形如 PUB_KEY_ID_")
    apiv3_key: str = Field(default="", max_length=64, repr=False, exclude=True, description="APIv3 密钥,只用于回调解密")
    notify_url: str = Field(default="", max_length=255, description="支付结果通知 URL,须公网 HTTPS")
    refund_notify_url: str = Field(default="", max_length=255, description="微信退款专用HTTPS通知地址，不得含query")
    timeout_seconds: float = Field(default=10.0, ge=1, le=30, description="调用微信的连接与读取超时(秒)")

    @field_validator("refund_notify_url")
    @classmethod
    def validate_refund_notify_url(cls, value: str, info: ValidationInfo) -> str:
        """空值保留历史不传退款notify_url的行为；明确值只允许公网HTTPS格式。"""
        if value:
            url = urlsplit(value)
            if (url.scheme != "https" or not url.hostname or "?" in value or url.fragment
                    or url.username or url.password or value == info.data.get("notify_url")):
                raise ValueError("refund_notify_url must be HTTPS without query or credentials")
        return value


class AlipayPayConfig(BaseModel):
    """支付宝订单码凭证。公钥模式,签名固定 RSA2。空字段表示这条渠道未启用。"""

    model_config = ConfigDict(hide_input_in_errors=True)

    app_id: str = Field(default="", max_length=32, description="开放平台应用 APPID")
    private_key: str = Field(default="", max_length=8192, repr=False, exclude=True,
                             description="应用私钥 PKCS#1,可用 \\n 表示换行")
    alipay_public_key: str = Field(default="", max_length=8192, description="支付宝公钥,用于应答和通知验签")
    notify_url: str = Field(default="", max_length=255, description="支付结果通知 URL,须公网 HTTPS")
    gateway: str = Field(
        default="https://openapi.alipay.com/gateway.do",
        max_length=128,
        description="开放平台网关。正式环境用默认值",
    )
    timeout_seconds: float = Field(default=10.0, ge=1, le=30, description="调用支付宝的超时秒数")


class PaymentConfig(BaseModel):
    """支付插件配置。两条渠道各自凭证齐才启用,可以同时开。"""

    model_config = ConfigDict(hide_input_in_errors=True)

    provider: str = Field(default="", max_length=16, description="历史字段。渠道是否启用看各自凭证,不看这里")
    # 与 Native code_url 两小时有效期对齐;过期后关单再换新订单号,本字段只控制下单 time_expire
    order_expire_minutes: int = Field(default=120, ge=1, le=10080, description="订单支付截止,分钟")
    max_pending_orders: int = Field(default=3, ge=1, le=20, description="同一用户未支付订单上限")
    max_notify_bytes: int = Field(default=65536, ge=1024, le=1048576, description="回调正文上限字节")
    wechat: WechatPayConfig = WechatPayConfig()
    alipay: AlipayPayConfig = AlipayPayConfig()
