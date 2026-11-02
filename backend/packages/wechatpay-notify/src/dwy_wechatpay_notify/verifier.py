"""将公开 SDK callback 结果收窄为白名单模型，不实现密码学。"""

from collections.abc import Callable, Mapping

from .models import VerifiedPaymentNotification, VerifiedRefundNotification, WechatPayNotifyConfig


class WechatPayVerificationError(ValueError):
    """安全的回调失败类型；消息不携带报文、签名或密钥。"""


class WechatPayNotificationVerifier:
    """在宿主 SDK 客户端有效上下文内使用其同步 callback，不拥有或关闭 SDK。"""

    def __init__(
        self, config: WechatPayNotifyConfig, *, callback: Callable[[Mapping[str, str], bytes], object]
    ):
        self.config = config
        self._callback = callback

    async def verify(
        self, headers: Mapping[str, str], body: bytes
    ) -> VerifiedPaymentNotification | VerifiedRefundNotification:
        """原始 bytes 只交给 SDK 一次；身份、金额及事件状态在解密后校验。"""
        try:
            if not isinstance(body, bytes) or not 1 <= len(body) <= self.config.max_body_bytes:
                raise ValueError("invalid body size")
            normalized = {key.lower(): value for key, value in headers.items()}
            for name, maximum in (
                ("signature", 4096),
                ("timestamp", 32),
                ("nonce", 256),
                ("serial", 128),
                ("signature-type", 64),
            ):
                value = normalized.get(f"wechatpay-{name}", "")
                if not isinstance(value, str) or len(value) > maximum:
                    raise ValueError("invalid callback header")
            signature = normalized.get("wechatpay-signature", "")
            if signature.startswith("WECHATPAY/SIGNTEST/"):
                raise ValueError("signature test")
            # SDK 接受大小写两种头名；不重新编码/解析签名覆盖的请求正文。
            data = self._callback(normalized, body)
            if not isinstance(data, dict) or not isinstance(data.get("resource"), dict):
                raise ValueError("missing verified resource")
            resource = data["resource"]
            if resource.get("mchid") != self.config.mchid:
                raise ValueError("merchant mismatch")
            amount = resource["amount"]
            # 直连退款通知不保证提供 currency；付款必须显式为 CNY。
            currency = amount.get("currency", "CNY" if data["event_type"].startswith("REFUND.") else None)
            if currency != "CNY":
                raise ValueError("unsupported currency")
            fields = {
                "event_type": data["event_type"],
                "provider_event_id": data["id"],
                "order_no": resource["out_trade_no"],
                "transaction_id": resource["transaction_id"],
                "amount_fen": amount["total"],
                "occurred_at": data.get("create_time"),
            }
            if data["event_type"] == "TRANSACTION.SUCCESS":
                if resource.get("appid") != self.config.appid:
                    raise ValueError("application mismatch")
                return VerifiedPaymentNotification(
                    **fields, trade_type=resource["trade_type"], trade_state=resource["trade_state"]
                )
            # 退款协议不保证 appid；存在时仍核对，缺失时以商户身份为准。
            if "appid" in resource and resource["appid"] != self.config.appid:
                raise ValueError("application mismatch")
            return VerifiedRefundNotification(
                **fields,
                refund_no=resource["out_refund_no"],
                refund_id=resource["refund_id"],
                refund_fen=amount["refund"],
                refund_status=resource["refund_status"],
            )
        except Exception:
            # 第三方 SDK 可抛密码学/JSON/协议异常，统一脱敏后不误确认微信重试。
            raise WechatPayVerificationError("Wechat Pay notification verification failed") from None
