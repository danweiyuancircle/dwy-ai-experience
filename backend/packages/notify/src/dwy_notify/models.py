"""通知包拥有的配置与结果契约，不向调用方泄漏 Apprise 类型。"""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class NotificationConfig(BaseModel):
    """显式目标映射；URL 可含凭据，不应解密后写入日志或错误。"""

    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)

    targets: dict[str, SecretStr] = Field(min_length=1)
    timeout_seconds: float = Field(default=10, gt=0, le=30, strict=True, allow_inf_nan=False)

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, targets: dict[str, SecretStr]) -> dict[str, SecretStr]:
        if any(not name.strip() or not url.get_secret_value().strip() for name, url in targets.items()):
            raise ValueError("empty_target")
        return targets


@dataclass(frozen=True)
class NotificationDelivery:
    """单个命名目标的结果；错误码固定且不含第三方响应或请求内容。"""

    target: str
    success: bool
    message_id: str | None = None
    error_code: str | None = None
    retry_after: float | None = None
    permanent: bool = False


@dataclass(frozen=True)
class NotificationResult:
    """按请求目标顺序保留结果；failed 可直接作为下次 send 的 targets。"""

    deliveries: tuple[NotificationDelivery, ...]

    @property
    def success(self) -> bool:
        return bool(self.deliveries) and all(delivery.success for delivery in self.deliveries)

    @property
    def succeeded(self) -> tuple[str, ...]:
        return tuple(delivery.target for delivery in self.deliveries if delivery.success)

    @property
    def failed(self) -> tuple[str, ...]:
        return tuple(delivery.target for delivery in self.deliveries if not delivery.success)
