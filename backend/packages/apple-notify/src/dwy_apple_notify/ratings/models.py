"""显式配置与 Lookup 全版本聚合评分，不包含 Apple 私钥或宿主环境。"""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..config import ASCAppID, NotificationSettings


class RatingCollectionError(Exception):
    """仅公开固定错误码，不携带响应正文或底层请求异常。"""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class AppleRating(BaseModel):
    """某应用某地区的全版本累计指标；保留 Apple 返回均分精度。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    count: int = Field(ge=0, le=9223372036854775807, strict=True)
    average: float = Field(ge=0, le=5, allow_inf_nan=False)

    @field_validator("average", mode="before")
    @classmethod
    def numeric_average(cls, value):
        """JSON 布尔值和字符串不是数值评分。"""
        if type(value) not in (int, float):
            raise ValueError("Invalid rating average")
        return value

    @model_validator(mode="after")
    def consistent_zero(self):
        """零评分仅接受零均分，有评分时均分须位于有效星级范围。"""
        if (self.count == 0 and self.average != 0) or (self.count > 0 and self.average < 1):
            raise ValueError("Inconsistent rating aggregates")
        return self


class RatingApp(BaseModel):
    """宿主提供的应用显示名称，Apple App ID 由配置字典键指定。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1, max_length=128)


class AppleRatingsConfig(NotificationSettings):
    """独立的每日评分计划；不读取环境、不依赖文字评价的启停或周期。"""

    apps: dict[ASCAppID, RatingApp] = Field(min_length=1, max_length=100)
    territories: tuple[str, ...] = Field(default=("cn", "us"), min_length=1, max_length=50)
    timezone: str = Field(default="Asia/Shanghai", min_length=1, max_length=64)
    send_hour: int = Field(default=8, ge=0, le=23, strict=True)
    send_minute: int = Field(default=30, ge=0, le=59, strict=True)
    retention_days: int = Field(default=90, ge=32, le=3650, strict=True)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        """使用 IANA 时区标识隔离历史，不接受隐式 UTC 回退。"""
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid rating timezone") from None
        return value

    @field_validator("territories")
    @classmethod
    def valid_territories(cls, value):
        """Lookup country 使用小写双字母商店代码，同轮不重复请求。"""
        if len(set(value)) != len(value) or any(
            len(item) != 2 or not item.isascii() or not item.isalpha() or not item.islower() for item in value
        ):
            raise ValueError("Invalid rating territories")
        return value
