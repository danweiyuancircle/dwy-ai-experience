"""Email Provider 工厂 -- 内置与自定义走同一注册表。

`make_email_provider` 只按名查表,不再对 resend 写死 if。
内置通道用懒加载器写入注册表,缺 extra 时由对应 builder 抛 ImportError。
"""

from collections.abc import Callable

from dwyeapi.logger import get_logger
from dwyeapi.providers.email.config import EmailSettings
from dwyeapi.providers.email.protocol import EmailProvider

logger = get_logger(__name__)

EmailProviderFactory = Callable[[EmailSettings], EmailProvider]

_REGISTRY: dict[str, EmailProviderFactory] = {}
# 测试仍 import 此名;与 _REGISTRY 是同一 dict
_PROVIDER_REGISTRY = _REGISTRY


def _load_resend() -> EmailProviderFactory:
    """延迟 import,避免未装 email-resend extra 时加载 SDK。"""
    from dwyeapi.providers.email.resend import build_resend_provider

    return build_resend_provider


# 新增内置通道只在此加一行,工厂查找逻辑不动
_BUILTIN_LOADERS: dict[str, Callable[[], EmailProviderFactory]] = {
    "resend": _load_resend,
}


def _ensure_builtin(name: str) -> None:
    """首次用到某内置名时写入注册表。注册表被测试 clear 后也能补回。"""
    if name in _REGISTRY or name not in _BUILTIN_LOADERS:
        return
    _REGISTRY[name] = _BUILTIN_LOADERS[name]()


def register_email_provider(name: str, factory: EmailProviderFactory) -> None:
    """注册自定义 Email Provider。

    业务项目继承 `EmailProviderBase` 实现 `_send` 后,通过此函数注册到工厂,
    `.env` 设 `EMAIL__PROVIDER=<name>` 即可启用,无需改 eapi。

    Args:
        name: provider 名称,与 EMAIL__PROVIDER 环境变量值对应。
        factory: 工厂函数,接收 EmailSettings 返回 EmailProvider 实例。

    Raises:
        ValueError: 名称为空或与内置名称冲突。
    """
    if not name:
        raise ValueError("provider 名称不能为空")
    if name in _BUILTIN_LOADERS:
        raise ValueError(f"'{name}' 为内置 provider 名称,不可覆盖")
    if name in _REGISTRY:
        logger.warning("Email provider %s 被覆盖注册", name)
    _REGISTRY[name] = factory


def make_email_provider(settings: EmailSettings) -> EmailProvider:
    """根据 `settings.provider` 从注册表构造实例。

    Args:
        settings: Email 模块配置(项目 Settings 的嵌套字段)。

    Returns:
        实现了 `EmailProvider` Protocol 的实例。

    Raises:
        ValueError: 未知 provider 或必填配置缺失。
        ImportError: 对应内置 extra 未安装。
    """
    name = settings.provider
    _ensure_builtin(name)
    factory = _REGISTRY.get(name)
    if factory is None:
        builtins = ", ".join(sorted(_BUILTIN_LOADERS))
        raise ValueError(
            f"未知 email provider: {name};"
            f"内置: {builtins};自定义需先调用 register_email_provider 注册"
        )
    return factory(settings)
