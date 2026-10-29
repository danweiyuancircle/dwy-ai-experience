"""宿主显式配置与不可变的官方报表快照；缺失数据不冒充零。"""

from datetime import date
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from ..config import ASCAppID, NotificationSettings


class AnalyticsCollectionError(Exception):
    """只传播固定错误码，隐藏签名下载地址和 Apple 响应。"""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class AnalyticsApp(BaseModel):
    """宿主提供的应用名称，最多 128 字符。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1, max_length=128)


class AppleAnalyticsConfig(NotificationSettings):
    """仅消费显式配置；定时使用指定时区，固定取昨天的 Apple UTC 统计日报表。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    apps: dict[ASCAppID, AnalyticsApp] = Field(min_length=1, max_length=100)
    issuer_id: str = Field(
        min_length=36, max_length=36, pattern=r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$"
    )
    key_id: str = Field(min_length=10, max_length=10, pattern=r"^[A-Z0-9]{10}$")
    private_key: SecretStr = Field(min_length=1, max_length=16384, repr=False)
    timezone: str = Field(default="Asia/Shanghai", min_length=1, max_length=128)
    send_hour: int = Field(default=8, ge=0, le=23, strict=True)
    send_minute: int = Field(default=30, ge=0, le=59, strict=True)
    retention_days: int = Field(default=400, ge=7, le=3650, strict=True)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid analytics timezone") from None
        return value


class AnalyticsValue(BaseModel):
    """数值连同来源和可用性保存；缺失值不得由调用方补零。"""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    value: Decimal | None = None
    status: Literal["available", "pending", "unavailable", "not_applicable"] = "unavailable"
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    source: str = Field(default="", max_length=256)


class AppleBusinessSnapshot(BaseModel):
    """单应用单 UTC 日期的替换版本；金额统一使用 Decimal。"""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    app_id: ASCAppID
    report_date: date
    metrics: dict[str, AnalyticsValue]
    breakdowns: dict[str, dict[str, Decimal]] = Field(default_factory=dict)
    notes: tuple[str, ...] = ()
