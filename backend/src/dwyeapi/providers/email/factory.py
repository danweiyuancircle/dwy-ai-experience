"""Email Provider 工厂 -- 内置 resend,支持外部注册自定义 provider。"""

from collections.abc import Callable

from dwyeapi.logger import get_logger
from dwyeapi.providers.email.config import EmailSettings
from dwyeapi.providers.email.protocol import EmailProvider

logger = get_logger(__name__)

EmailProviderFactory = Callable[[EmailSettings], EmailProvider]

_BUILTIN_RESEND = "resend"
_PROVIDER_REGISTRY: dict[str, EmailProviderFactory] = {}


def register_email_provider(name: str, factory: EmailProviderFactory) -> None:
    """注册自定义 Email Provider。

    业务项目继承 `EmailProviderBase` 实现 `_send` 后,通过此函数注册到工厂,
    `.env` 设 `EMAIL__PROVIDER=<name>` 即可启用。

    Args:
        name: provider 名称,与 EMAIL__PROVIDER 环境变量值对应。
        factory: 工厂函数,接收 EmailSettings 返回 EmailProvider 实例。

    Raises:
        ValueError: 名称为空或与内置名称冲突。
    """
    if not name:
        raise ValueError("provider 名称不能为空")
    if name == _BUILTIN_RESEND:
        raise ValueError(f"'{name}' 为内置 provider 名称,不可覆盖")
    if name in _PROVIDER_REGISTRY:
        logger.warning("Email provider %s 被覆盖注册", name)
    _PROVIDER_REGISTRY[name] = factory


def make_email_provider(settings: EmailSettings) -> EmailProvider:
    """根据 `settings.provider` 构造对应的 Email Provider 实例。

    Args:
        settings: Email 模块配置(项目 Settings 的嵌套字段)。

    Returns:
        实现了 `EmailProvider` Protocol 的实例。

    Raises:
        ValueError: 未知 provider 或必填配置缺失。
        ImportError: resend extra 未安装。
    """
    common = {
        "code_ttl": settings.code_ttl,
        "code_length": settings.code_length,
        "brand_name": settings.brand_name,
        "brand_tagline": settings.brand_tagline,
        "brand_url": settings.brand_url,
        "brand_slogan": settings.brand_slogan,
        "support_email": settings.support_email,
    }

    if settings.provider == _BUILTIN_RESEND:
        from dwyeapi.providers.email.resend import ResendEmailProvider

        if not settings.resend.api_key:
            raise ValueError("EMAIL__RESEND__API_KEY 未配置")
        return ResendEmailProvider(
            api_key=settings.resend.api_key,
            from_email=settings.resend.from_email,
            subject=settings.resend.subject,
            **common,
        )

    if settings.provider in _PROVIDER_REGISTRY:
        return _PROVIDER_REGISTRY[settings.provider](settings)

    raise ValueError(
        f"未知 email provider: {settings.provider};"
        f"内置仅支持 'resend',自定义 provider 需先调用 register_email_provider 注册"
    )
