"""微信 Native 适配器。签名、下单、查单、关单、回调解密都走 wechatpayv3,不手写签名。"""

import json
from datetime import datetime

from dwy_wechatpay_notify import (
    VerifiedPaymentNotification,
    VerifiedRefundNotification,
    WechatPayNotificationVerifier,
    WechatPayNotifyConfig,
    WechatPayVerificationError,
)
from dwyeapi.logger import get_logger
from wechatpayv3.async_ import AsyncWeChatPay

# 同步、异步 SDK 的同名枚举不相等，必须与客户端使用同一套类型。
from wechatpayv3.async_.type import WeChatPayType

from dwy_payment.config import WechatPayConfig
from dwy_payment.constants import EVENT_QUERY, ORDER_NO_MAX_LEN, ORDER_NO_MIN_LEN
from dwy_payment.errors import PaymentChannelError, PaymentVerifyError
from dwy_payment.protocols import ChannelNotify
from dwy_payment.refunds.protocols import RefundChannelResult

logger = get_logger(__name__)

_NOTIFY_RAW_MAX = 8000
# 退款同步应答里这两种状态都表示渠道已接受,可以收回权益。CLOSED / ABNORMAL 不能当退成。
_REFUND_ACCEPTED = frozenset({"SUCCESS", "PROCESSING"})
_USE_CONFIG_NOTIFY = object()


def _normalize_pem(value: str) -> str:
    """把环境变量里的 ``\\n`` 还原成 PEM 换行。

    Args:
        value (str): PEM 文本。长度 ``[0, 8192]``。示例:``"<单行 PEM，换行写成 \\\\n>"``。
    Returns:
        str: 带真实换行的 PEM。
    """
    return value.replace("\\n", "\n")


def _query_notify(resource: dict) -> ChannelNotify:
    """保留SDK查询字段映射，直接解析资源体，不构造虚假的回调信封。"""
    amount = resource.get("amount") if isinstance(resource, dict) else None
    total = amount.get("total") if isinstance(amount, dict) else None
    order_no = resource.get("out_trade_no") if isinstance(resource, dict) else None
    trade_state = resource.get("trade_state") if isinstance(resource, dict) else None
    trade_type = resource.get("trade_type") if isinstance(resource, dict) else None
    transaction_id = resource.get("transaction_id") if isinstance(resource, dict) else None
    if not isinstance(order_no, str) or not ORDER_NO_MIN_LEN <= len(order_no) <= ORDER_NO_MAX_LEN:
        raise PaymentVerifyError
    if not isinstance(total, int):
        raise PaymentVerifyError
    if not isinstance(trade_state, str) or not isinstance(trade_type, str):
        raise PaymentVerifyError
    if not isinstance(transaction_id, str) or not 1 <= len(transaction_id) <= 64:
        raise PaymentVerifyError
    return ChannelNotify(
        order_no=order_no,
        amount_fen=total,
        trade_state=trade_state,
        trade_type=trade_type,
        event_type=EVENT_QUERY,
        transaction_id=transaction_id,
        raw=_clip(resource),
    )


class WechatNativeGateway:
    """普通商户 Native。公钥模式,每次调用单独打开 HTTP 客户端。"""

    # 宿主仅对具备最终结果查询/回调能力的真实渠道登记自动退款独立意图。
    supports_refund_results = True

    def __init__(self, cfg: WechatPayConfig) -> None:
        """保存凭证。不在这里连微信,避免导入或启动时打外网。

        Args:
            cfg (WechatPayConfig): 已确认非空的微信配置。示例:``WechatPayConfig(mchid="1600000000")``。
        """
        self._cfg = cfg

    def is_configured(self) -> bool:
        """独立消费者可直接构造网关，凭据不齐时必须阻止发起资金操作。"""
        return all(value.strip() for value in (
            self._cfg.mchid, self._cfg.appid, self._cfg.private_key, self._cfg.cert_serial,
            self._cfg.public_key, self._cfg.public_key_id, self._cfg.apiv3_key, self._cfg.notify_url,
        ))

    def _client(self, *, notify_url: object = _USE_CONFIG_NOTIFY) -> AsyncWeChatPay:
        """按当前配置建客户端。PEM 在这里还原换行。

        退款客户端传 ``notify_url=None``，专用地址由退款方法显式提供，避免SDK回退付款地址。

        Args:
            notify_url (object): 回调地址。默认沿用配置。示例:``None``。
        Returns:
            AsyncWeChatPay: 尚未进入上下文的客户端。
        """
        timeout = self._cfg.timeout_seconds
        url = self._cfg.notify_url if notify_url is _USE_CONFIG_NOTIFY else notify_url
        return AsyncWeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=self._cfg.mchid,
            private_key=_normalize_pem(self._cfg.private_key),
            cert_serial_no=self._cfg.cert_serial,
            appid=self._cfg.appid,
            apiv3_key=self._cfg.apiv3_key,
            notify_url=url if isinstance(url, str) else None,
            public_key=_normalize_pem(self._cfg.public_key),
            public_key_id=self._cfg.public_key_id,
            timeout=(timeout, timeout),
        )

    async def create_native(
        self,
        *,
        order_no: str,
        description: str,
        amount_fen: int,
        time_expire: datetime,
    ) -> str:
        """调用 Native 下单,只要 code_url。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            description (str): 商品描述。长度 ``[1, 127]``。示例:``"基础版月付"``。
            amount_fen (int): 金额分。取值范围 ``[1, 100000000]``。示例:``9900``。
            time_expire (datetime): 上海墙钟的支付截止,无时区。示例:``dt.after(minutes=120)``。
        Returns:
            str: 二维码链接。
        Raises:
            PaymentChannelError: HTTP 非 2xx,或应答里没有 code_url。
        """
        # dt.now/after 是上海墙钟的 naive 值,微信要带 +08:00 的 RFC3339。
        expire = time_expire.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        try:
            async with self._client() as client:
                code, text = await client.pay(
                    description=description,
                    out_trade_no=order_no,
                    amount={"total": amount_fen, "currency": "CNY"},
                    time_expire=expire,
                    notify_url=self._cfg.notify_url,
                    pay_type=WeChatPayType.NATIVE,
                )
        except Exception as exc:
            # SDK 验签会抛通用异常；归一化后服务才能保留未知下单，且不暴露原始报文。
            logger.warning("wechat payment create failed type=%s", type(exc).__name__)
            raise PaymentChannelError("payment create request failed") from None
        return _code_url(code, text)

    async def query(self, order_no: str) -> ChannelNotify:
        """按商户订单号查单。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Returns:
            ChannelNotify: 查单结果。event_type 为 QUERY。是否入账看 trade_state,不看事件名。
        Raises:
            PaymentChannelError: 查单失败。
        """
        try:
            async with self._client() as client:
                code, text = await client.query(out_trade_no=order_no)
        except Exception as exc:
            # 单笔 SDK 网络或验签失败不能打断其他待支付订单的补查。
            logger.warning("wechat payment query failed type=%s", type(exc).__name__)
            raise PaymentChannelError("payment query request failed") from None
        payload = _json_body(code, text)
        try:
            note = _query_notify(payload)
        except PaymentVerifyError as exc:
            raise PaymentChannelError("query body invalid") from exc
        return note

    async def close(self, order_no: str) -> None:
        """关闭未支付订单。微信成功是 204。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Raises:
            PaymentChannelError: 非 204。
        """
        try:
            async with self._client() as client:
                code, text = await client.close(out_trade_no=order_no)
        except Exception as exc:
            # 关闭结果未知时不能泄露 SDK 异常正文，也不能把本地订单标成已关闭。
            logger.warning("wechat payment close failed type=%s", type(exc).__name__)
            raise PaymentChannelError("payment close request failed") from None
        if code != 204:
            logger.warning("wechat close failed status=%s order_no=%s", code, order_no)
            raise PaymentChannelError(f"status={code} body={_clip_text(text)}")

    async def refund(self, order_no: str, refund_no: str, refund_fen: int, total_fen: int) -> str:
        """申请退款。返回渠道受理状态；到账仅由退款回调/查询核验，不从PROCESSING推导。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            refund_no (str): 商户退款单号。长度 ``[1, 64]``。示例:``"Ra1b2c3d4e5f64789a0b1c2d3e4f5678"``。
            refund_fen (int): 本次退款分。取值范围 ``[1, 100000000]``。示例:``9580``。
            total_fen (int): 原订单实付分。取值范围 ``[1, 100000000]``。示例:``9900``。
        Raises:
            PaymentChannelError: 非 2xx,或状态不是 SUCCESS / PROCESSING。
        Returns:
            str: SUCCESS或PROCESSING，既有权益政策由业务编排保留。
        """
        try:
            async with self._client(notify_url=None) as client:
                code, text = await client.refund(
                    out_refund_no=refund_no,
                    out_trade_no=order_no,
                    amount={"refund": refund_fen, "total": total_fen, "currency": "CNY"},
                    reason="用户申请退款",
                    notify_url=self._cfg.refund_notify_url or None,
                )
        except Exception as exc:
            # SDK验签失败使用通用Exception；仅在外部SDK边界收窄为不含报文的渠道错误。
            logger.warning("wechat refund request failed type=%s", type(exc).__name__)
            raise PaymentChannelError("refund request failed") from None
        payload = _json_body(code, text)
        state = payload.get("status")
        if state not in _REFUND_ACCEPTED:
            logger.warning("wechat refund rejected status=%s order_no=%s", state, order_no)
            raise PaymentChannelError(f"refund status={state}")
        return state

    async def parse_notify(self, headers: object, body: bytes) -> ChannelNotify:
        """验签并解密。探测流量和验签失败都抛 PaymentVerifyError。

        Args:
            headers (object): 回调头。示例:``{"wechatpay-signature": "WECHATPAY/SIGNTEST/"}``。
            body (bytes): 原始正文。示例:``b"{}"``。
        Returns:
            ChannelNotify: 解密后的通知。
        Raises:
            PaymentVerifyError: 探测、验签失败、字段不齐、或商户号/appid 与配置不一致。
        """
        parsed = await self._verify_notification(headers, body)
        if not isinstance(parsed, VerifiedPaymentNotification):
            raise PaymentVerifyError
        return ChannelNotify(order_no=parsed.order_no, amount_fen=parsed.amount_fen,
                             trade_state=parsed.trade_state, trade_type=parsed.trade_type,
                             event_type=parsed.event_type, transaction_id=parsed.transaction_id,
                             raw=parsed.model_dump_json())

    async def _verify_notification(self, headers: object, body: bytes):
        try:
            # 公钥模式callback仅使用构造期密钥，不进入会发HTTP/下载证书的异步上下文。
            client = self._client()
            verifier = WechatPayNotificationVerifier(
                # 路由执行当前max_notify_bytes；此处仅保留PaymentConfig允许的最高硬上限。
                WechatPayNotifyConfig(mchid=self._cfg.mchid, appid=self._cfg.appid, scope="dwy-payment",
                                      max_body_bytes=1048576),
                callback=client.callback,
            )
            return await verifier.verify(headers, body)
        except (WechatPayVerificationError, ValueError) as exc:
            raise PaymentVerifyError from exc

    async def parse_refund_notify(self, headers: object, body: bytes) -> RefundChannelResult:
        """来源包只验签一次，仅接收退款回调；退款资源不要求缺失的appid。"""
        parsed = await self._verify_notification(headers, body)
        if not isinstance(parsed, VerifiedRefundNotification):
            raise PaymentVerifyError
        return RefundChannelResult(order_no=parsed.order_no, transaction_id=parsed.transaction_id,
                                   amount_fen=parsed.amount_fen, refund_no=parsed.refund_no,
                                   refund_id=parsed.refund_id, refund_fen=parsed.refund_fen,
                                   refund_status=parsed.refund_status, provider_event_id=parsed.provider_event_id,
                                   occurred_at=parsed.occurred_at)

    async def refund_query(self, refund_no: str) -> RefundChannelResult:
        """按原退款号查询；SDK真实方法为query_refund，结果不冒充原始回调。"""
        try:
            async with self._client(notify_url=None) as client:
                code, text = await client.query_refund(out_refund_no=refund_no)
        except Exception as exc:
            # SDK验签失败使用通用Exception；统一渠道错误才能逐笔补查且不泄露原始报文。
            logger.warning("wechat refund query failed type=%s", type(exc).__name__)
            raise PaymentChannelError("refund query request failed") from None
        if code == 404:
            from dwy_payment.errors import RefundNotFoundError

            try:
                failure = json.loads(text)
            except (ValueError, TypeError):
                failure = None
            if isinstance(failure, dict) and failure.get("code") == "RESOURCE_NOT_EXISTS":
                raise RefundNotFoundError("refund not found")
        payload = _json_body(code, text)
        try:
            amount = payload["amount"]
            parsed = RefundChannelResult(
                order_no=payload["out_trade_no"], transaction_id=payload["transaction_id"],
                amount_fen=amount["total"], refund_no=payload["out_refund_no"], refund_id=payload["refund_id"],
                refund_fen=amount["refund"], refund_status=payload["status"], currency=amount["currency"],
                occurred_at=payload.get("success_time"),
            )
            if parsed.refund_no != refund_no or parsed.currency != "CNY":
                raise ValueError("refund query mismatch")
            return parsed
        except (KeyError, TypeError, ValueError) as exc:
            raise PaymentChannelError("refund query body invalid") from exc


def _code_url(code: int, text: object) -> str:
    """从下单应答取出 code_url。

    Args:
        code (int): HTTP 状态。示例:``200``。
        text (object): 应答正文。示例:``'{"code_url":"weixin://wxpay/bizpayurl"}'``。
    Returns:
        str: 二维码链接。
    Raises:
        PaymentChannelError: 状态或正文不合格。
    """
    payload = _json_body(code, text)
    url = payload.get("code_url")
    if not isinstance(url, str) or not url:
        raise PaymentChannelError("missing code_url")
    return url


def _json_body(code: int, text: object) -> dict:
    """把 2xx JSON 正文解析成对象。

    Args:
        code (int): HTTP 状态。取值范围 ``[100, 599]``。示例:``200``。
        text (object): 正文,可能是 str 或 bytes。示例:``b'{}'``。
    Returns:
        dict: JSON 对象。
    Raises:
        PaymentChannelError: 非 2xx 或不是 JSON 对象。
    """
    if code < 200 or code >= 300:
        logger.warning("wechat http failed status=%s", code)
        raise PaymentChannelError(f"status={code}")
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    if not isinstance(text, str):
        raise PaymentChannelError("empty body")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PaymentChannelError("invalid json") from exc
    if not isinstance(payload, dict):
        raise PaymentChannelError("json not object")
    return payload


def _clip(payload: dict) -> str:
    """截断落库的回调 JSON,避免超大报文写进文本列。

    Args:
        payload (dict): 解密资源。示例:``{"out_trade_no": "abc"}``。
    Returns:
        str: 最长 8000 字符的 JSON。
    """
    return json.dumps(payload, ensure_ascii=False)[:_NOTIFY_RAW_MAX]


def _clip_text(text: object) -> str:
    """日志里的应答摘要,最多 200 字符。

    Args:
        text (object): 渠道正文。示例:``"{"code":"PARAM_ERROR"}"``。
    Returns:
        str: 截断后的文本。
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    if not isinstance(text, str):
        return ""
    return text[:200]
