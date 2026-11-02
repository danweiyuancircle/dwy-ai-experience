"""支付宝订单码适配器。下单、查单、关单、退款、通知验签都走官方 SDK,不手写签名。"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qsl

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeCloseModel import AlipayTradeCloseModel
from alipay.aop.api.domain.AlipayTradePrecreateModel import AlipayTradePrecreateModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
from alipay.aop.api.request.AlipayTradeCloseRequest import AlipayTradeCloseRequest
from alipay.aop.api.request.AlipayTradePrecreateRequest import AlipayTradePrecreateRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
from alipay.aop.api.util.SignatureUtils import get_sign_content, verify_with_rsa
from dwyeapi import dt
from dwyeapi.logger import get_logger

from dwy_payment.config import AlipayPayConfig
from dwy_payment.constants import (
    EVENT_QUERY,
    EVENT_TRANSACTION_SUCCESS,
    ORDER_NO_MAX_LEN,
    ORDER_NO_MIN_LEN,
    TRADE_STATE_SUCCESS,
    TRADE_TYPE_NATIVE,
)
from dwy_payment.errors import PaymentChannelError, PaymentVerifyError
from dwy_payment.protocols import ChannelNotify

logger = get_logger(__name__)

_SUCCESS_CODE = "10000"
_PAID_STATUS = frozenset({"TRADE_SUCCESS", "TRADE_FINISHED"})
_NOTIFY_RAW_MAX = 8000
# 订单码官方示例用这个产品码。页面跳转类接口才用 page_execute,这里必须 execute。
_PRODUCT_CODE = "FACE_TO_FACE_PAYMENT"


def _normalize_pem(value: str) -> str:
    """把环境变量里的 ``\\n`` 还原成 PEM 换行。不改密钥格式。

    Args:
        value (str): 密钥文本。长度 ``[0, 8192]``。示例:``"<单行 PKCS#1，换行写成 \\\\n>"``。
    Returns:
        str: 带真实换行的文本。
    """
    return value.replace("\\n", "\n")


def _yuan(amount_fen: int) -> str:
    """分换成支付宝要的元字符串。两位小数,不用二进制浮点。

    Args:
        amount_fen (int): 金额分。取值范围 ``[1, 100000000]``。示例:``9900``。
    Returns:
        str: 元。示例:``"99.00"``。
    """
    return f"{Decimal(amount_fen) / Decimal(100):.2f}"


def _fen(yuan: str) -> int:
    """元字符串换回分。不是两位小数就拒绝,避免把 1.001 收成 100 分。

    Args:
        yuan (str): 支付宝金额。示例:``"88.88"``。
    Returns:
        int: 分。示例:``8888``。
    Raises:
        PaymentVerifyError: 不是合法的两位小数金额。
    """
    try:
        amount = Decimal(yuan)
    except InvalidOperation as exc:
        raise PaymentVerifyError from exc
    fen = amount * 100
    if fen != fen.to_integral_value():
        raise PaymentVerifyError
    return int(fen)


def _timeout_express(time_expire: datetime) -> str:
    """把截止时间收成支付宝的相对超时。至少 1 分钟。

    Args:
        time_expire (datetime): 支付截止。示例:上海墙钟。
    Returns:
        str: 形如 ``"120m"``。
    """
    seconds = (time_expire - dt.now()).total_seconds()
    minutes = max(1, int(seconds // 60))
    return f"{minutes}m"


def _execute(client_config: AlipayClientConfig, request: object) -> str:
    """同步调用官方 SDK。异步路由用 to_thread 包住,避免堵住事件循环。

    Args:
        client_config (AlipayClientConfig): 本次请求的客户端配置。
        request (object): 官方请求对象。示例:``AlipayTradePrecreateRequest``。
    Returns:
        str: SDK 返回的 JSON 文本。
    """
    # 不把业务 logger 交给 SDK。它会打印完整请求,私钥不能进日志。
    client = DefaultAlipayClient(alipay_client_config=client_config)
    return client.execute(request)


def _node(raw: str, key: str) -> dict:
    """取出某个接口的响应节点。结构不对当渠道失败。

    Args:
        raw (str): SDK 原文。
        key (str): 响应键。示例:``"alipay_trade_precreate_response"``。
    Returns:
        dict: 该节点。
    Raises:
        PaymentChannelError: 不是 JSON 或没有这个节点。
    """
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PaymentChannelError("alipay body invalid") from exc
    node = payload.get(key) if isinstance(payload, dict) else None
    if not isinstance(node, dict):
        raise PaymentChannelError("alipay body invalid")
    return node


class AlipayPrecreateGateway:
    """支付宝订单码。凭证在构造时只保存,真正请求发生在方法里。"""

    def __init__(self, cfg: AlipayPayConfig) -> None:
        """保存订单码配置。

        Args:
            cfg (AlipayPayConfig): 应用凭证。示例:空配置表示未启用。
        """
        self._cfg = cfg

    def is_configured(self) -> bool:
        """四项凭证都非空才算启用。网关地址有默认值,不算缺项。"""
        fields = (self._cfg.app_id, self._cfg.private_key, self._cfg.alipay_public_key, self._cfg.notify_url)
        return all(item.strip() for item in fields)

    def _client_config(self) -> AlipayClientConfig:
        """按官方示例组装客户端。签名类型和字符集固定,不从环境改。

        Returns:
            AlipayClientConfig: 一次请求用的配置。
        """
        config = AlipayClientConfig()
        config.server_url = self._cfg.gateway
        config.app_id = self._cfg.app_id
        config.app_private_key = _normalize_pem(self._cfg.private_key)
        config.alipay_public_key = _normalize_pem(self._cfg.alipay_public_key)
        config.charset = "utf-8"
        config.sign_type = "RSA2"
        config.timeout = int(self._cfg.timeout_seconds)
        return config

    async def _call(self, request: object, key: str) -> dict:
        """执行请求并取出响应节点。失败只记状态码,不记密钥。

        Args:
            request (object): 官方请求。
            key (str): 响应键。示例:``"alipay_trade_query_response"``。
        Returns:
            dict: 业务节点。
        Raises:
            PaymentChannelError: 网络、解析或业务码不是 10000。
        """
        try:
            raw = await asyncio.to_thread(_execute, self._client_config(), request)
        except Exception as exc:
            logger.warning("alipay call failed type=%s", type(exc).__name__)
            raise PaymentChannelError("alipay call failed") from exc
        node = _node(raw, key)
        if node.get("code") != _SUCCESS_CODE:
            logger.warning("alipay rejected code=%s sub=%s", node.get("code"), node.get("sub_code"))
            raise PaymentChannelError(f"code={node.get('code')}")
        return node

    async def create_native(
        self,
        *,
        order_no: str,
        description: str,
        amount_fen: int,
        time_expire: datetime,
    ) -> str:
        """预创建订单码,返回 qr_code。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            description (str): 商品标题。长度 ``[1, 127]``。示例:``"10G 流量包"``。
            amount_fen (int): 金额分。取值范围 ``[1, 100000000]``。示例:``9900``。
            time_expire (datetime): 支付截止。示例:上海墙钟。
        Returns:
            str: 支付宝二维码内容。
        Raises:
            PaymentChannelError: 支付宝拒绝或没有 qr_code。
        """
        model = AlipayTradePrecreateModel()
        model.out_trade_no = order_no
        model.total_amount = _yuan(amount_fen)
        model.subject = description
        model.product_code = _PRODUCT_CODE
        model.timeout_express = _timeout_express(time_expire)
        request = AlipayTradePrecreateRequest()
        request.biz_model = model
        request.notify_url = self._cfg.notify_url
        node = await self._call(request, "alipay_trade_precreate_response")
        qr_code = node.get("qr_code")
        if not isinstance(qr_code, str) or not qr_code:
            raise PaymentChannelError("alipay qr missing")
        return qr_code

    async def query(self, order_no: str) -> ChannelNotify:
        """按商户订单号查单。未支付时 trade_state 不是 SUCCESS。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Returns:
            ChannelNotify: 查单结果。事件名是 QUERY。
        Raises:
            PaymentChannelError: 支付宝拒绝。
        """
        model = AlipayTradeQueryModel()
        model.out_trade_no = order_no
        request = AlipayTradeQueryRequest()
        request.biz_model = model
        node = await self._call(request, "alipay_trade_query_response")
        return _as_notify(node, event_type=EVENT_QUERY)

    async def close(self, order_no: str) -> None:
        """关闭未支付订单。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
        Raises:
            PaymentChannelError: 支付宝拒绝关单。
        """
        model = AlipayTradeCloseModel()
        model.out_trade_no = order_no
        request = AlipayTradeCloseRequest()
        request.biz_model = model
        await self._call(request, "alipay_trade_close_response")

    async def refund(self, order_no: str, refund_no: str, refund_fen: int, total_fen: int) -> None:
        """按商户订单号退一笔。out_request_no 固定,重试由支付宝幂等。

        Args:
            order_no (str): 商户订单号。长度 ``[6, 32]``。示例:``"a1b2c3d4e5f64789a0b1c2d3e4f56789"``。
            refund_no (str): 商户退款单号。长度 ``[1, 64]``。示例:``"Ra1b2c3d4e5f64789a0b1c2d3e4f5678"``。
            refund_fen (int): 本次退款分。取值范围 ``[1, 100000000]``。示例:``9900``。
            total_fen (int): 原订单实付分。只用来拒绝超额退款。取值范围 ``[1, 100000000]``。示例:``9900``。
        Raises:
            PaymentChannelError: 退款额超过实付,或支付宝拒绝。
        """
        if refund_fen > total_fen:
            raise PaymentChannelError("refund exceeds total")
        model = AlipayTradeRefundModel()
        model.out_trade_no = order_no
        model.refund_amount = _yuan(refund_fen)
        model.out_request_no = refund_no
        model.refund_reason = "用户申请退款"
        request = AlipayTradeRefundRequest()
        request.biz_model = model
        await self._call(request, "alipay_trade_refund_response")

    async def parse_notify(self, headers: object, body: bytes) -> ChannelNotify:
        """先验签,再读交易状态。验签失败不能当支付成功。

        Args:
            headers (object): 支付宝通知不靠自定义头验签。保留参数是为了和渠道接口一致。
            body (bytes): ``application/x-www-form-urlencoded`` 原文。
        Returns:
            ChannelNotify: 验签后的通知。
        Raises:
            PaymentVerifyError: 验签失败、app_id 不对、或字段不齐。
        """
        del headers
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PaymentVerifyError from exc
        params = {key: value for key, value in parse_qsl(text, keep_blank_values=True)}
        sign = params.pop("sign", "")
        params.pop("sign_type", None)
        if not sign or params.get("app_id") != self._cfg.app_id:
            raise PaymentVerifyError
        message = get_sign_content(params).encode("utf-8")
        try:
            ok = verify_with_rsa(_normalize_pem(self._cfg.alipay_public_key), message, sign)
        except Exception as exc:
            logger.info("alipay notify verify failed type=%s", type(exc).__name__)
            raise PaymentVerifyError from exc
        if not ok:
            raise PaymentVerifyError
        kept = {key: params[key] for key in ("out_trade_no", "trade_status", "total_amount") if key in params}
        raw = json.dumps(kept, ensure_ascii=False)
        return _as_notify(params, event_type=EVENT_TRANSACTION_SUCCESS, raw=raw[:_NOTIFY_RAW_MAX])


def _as_notify(data: dict, *, event_type: str, raw: str = "{}") -> ChannelNotify:
    """把支付宝字段收成渠道通知。已支付才标 SUCCESS,其它状态留给查单轮询。

    Args:
        data (dict): 查询节点或通知表单。
        event_type (str): ``QUERY`` 或 ``TRANSACTION.SUCCESS``。
        raw (str): 落库审计摘要。默认 ``"{}"``。
    Returns:
        ChannelNotify: 结构化结果。trade_type 固定 NATIVE,和微信主扫同一入账条件。
    Raises:
        PaymentVerifyError: 订单号或金额无法核对。
    """
    order_no = data.get("out_trade_no")
    if not isinstance(order_no, str) or not ORDER_NO_MIN_LEN <= len(order_no) <= ORDER_NO_MAX_LEN:
        raise PaymentVerifyError
    total = data.get("total_amount")
    if not isinstance(total, str):
        raise PaymentVerifyError
    trade_no = data.get("trade_no")
    if not isinstance(trade_no, str) or not trade_no:
        trade_no = "-"
    paid = data.get("trade_status") in _PAID_STATUS
    return ChannelNotify(
        order_no=order_no,
        amount_fen=_fen(total),
        trade_state=TRADE_STATE_SUCCESS if paid else "NOTPAY",
        trade_type=TRADE_TYPE_NATIVE,
        event_type=event_type,
        transaction_id=trade_no[:64],
        raw=raw,
    )
