"""按渠道名取出已装配的网关。

微信和支付宝可以同时配置。下单、查单、退款都按流水上的渠道走,不在微信文件里写支付宝分支。
"""

from dwy_payment.constants import CHANNEL_WECHAT
from dwy_payment.gateways.unconfigured import UnconfiguredGateway
from dwy_payment.protocols import PaymentGateway


class ChannelHub:
    """已启用渠道的表。缺的名字返回未配置占位,不在这里连外网。"""

    def __init__(self, channels: dict[str, PaymentGateway]) -> None:
        """保存渠道表。调用方已经决定哪些凭证齐。

        Args:
            channels (dict[str, PaymentGateway]): 渠道名到实现。示例:``{"wechat": gateway}``。
        """
        self._channels = channels

    def is_configured(self) -> bool:
        """至少一条渠道凭证齐。自动续费用这个判断能不能下单。"""
        return bool(self.configured_channels())

    def configured_channels(self) -> list[str]:
        """凭证齐的渠道名。微信在前,方便前端默认选它。

        Returns:
            list[str]: 子集 ``{"wechat", "alipay"}``。示例:``["wechat", "alipay"]``。
        """
        names = [name for name, gateway in self._channels.items() if gateway.is_configured()]
        names.sort(key=lambda name: (name != CHANNEL_WECHAT, name))
        return names

    def default_channel(self) -> str:
        """没人在场选渠道时用哪一条。有微信就用微信。

        Returns:
            str: 渠道名。示例:``"wechat"``。
        """
        names = self.configured_channels()
        if CHANNEL_WECHAT in names:
            return CHANNEL_WECHAT
        if names:
            return names[0]
        return CHANNEL_WECHAT

    def require(self, channel: str) -> PaymentGateway:
        """按名字取网关。没装配的名字当未配置。

        Args:
            channel (str): 渠道名。枚举 ``{"wechat", "alipay"}``。示例:``"alipay"``。
        Returns:
            PaymentGateway: 对应实现,或未配置占位。
        """
        return self._channels.get(channel, UnconfiguredGateway())
