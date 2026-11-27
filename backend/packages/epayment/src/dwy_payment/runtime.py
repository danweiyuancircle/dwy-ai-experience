"""装配层注入的渠道、钩子和配置。业务请求从这里取,不在路由里 new 微信客户端。"""

from dwy_payment.config import PaymentConfig
from dwy_payment.protocols import NoOpPaymentHook, PaymentGateway, PaymentPaidHook
from dwy_payment.refunds.protocols import (
    RefundManualReviewHook,
    RefundResultHook,
    noop_refund_manual_review,
    noop_refund_result,
)

_config: PaymentConfig | None = None
_gateway: PaymentGateway | None = None
_hook: PaymentPaidHook = NoOpPaymentHook()
_refund_session_factory = None
_refund_result_hook: RefundResultHook = noop_refund_result
_refund_manual_review_hook: RefundManualReviewHook = noop_refund_manual_review


def configure_refunds(*, session_factory=None, result_hook: RefundResultHook | None = None,
                      manual_review_hook: RefundManualReviewHook | None = None) -> None:
    """启动时注入退款独立会话及同事务sink；测试必须注入真正独立的factory。"""
    global _refund_session_factory, _refund_result_hook, _refund_manual_review_hook
    _refund_session_factory = session_factory
    _refund_result_hook = noop_refund_result if result_hook is None else result_hook
    _refund_manual_review_hook = noop_refund_manual_review if manual_review_hook is None else manual_review_hook


def get_refund_session_factory():
    """宿主显式注入独立会话工厂；永不读取项目配置或复用请求session。"""
    if _refund_session_factory is None:
        raise RuntimeError("refund session_factory must be configured by the host")
    return _refund_session_factory


def get_refund_result_hook() -> RefundResultHook:
    """返回当前宿主退款结果sink。"""
    return _refund_result_hook


def get_refund_manual_review_hook() -> RefundManualReviewHook:
    """返回超时退款人工核对的同事务通知sink。"""
    return _refund_manual_review_hook


def configure(*, config: PaymentConfig, gateway: PaymentGateway, hook: PaymentPaidHook) -> None:
    """注入支付运行时。进程启动时调用一次。

    Args:
        config (PaymentConfig): 支付配置。示例:``PaymentConfig()``。
        gateway (PaymentGateway): 渠道实现。未配置时传空实现。
        hook (PaymentPaidHook): 支付成功钩子。示例:项目侧的套餐发放。
    """
    global _config, _gateway, _hook
    _config = config
    _gateway = gateway
    _hook = hook


def get_config() -> PaymentConfig:
    """返回已注入的配置。

    Returns:
        PaymentConfig: 当前配置。

    Raises:
        RuntimeError: 尚未 configure。
    """
    if _config is None:
        raise RuntimeError("dwy_payment 未注册")
    return _config


def get_gateway() -> PaymentGateway:
    """返回已注入的渠道。

    Returns:
        PaymentGateway: 当前渠道。

    Raises:
        RuntimeError: 尚未 configure。
    """
    if _gateway is None:
        raise RuntimeError("dwy_payment 未注册")
    return _gateway


def get_hook() -> PaymentPaidHook:
    """返回支付成功钩子。

    Returns:
        PaymentPaidHook: 当前钩子。
    """
    return _hook


def set_gateway(gateway: PaymentGateway) -> None:
    """测试替换渠道。生产路径只用 configure。

    Args:
        gateway (PaymentGateway): 替换后的渠道。
    """
    global _gateway
    _gateway = gateway
