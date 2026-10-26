"""宿主显式注入的评论采集配置与经过边界校验的 Apple 评论。"""

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, SecretStr

from ..config import ASCAppID, Destination


class ReviewCollectionError(Exception):
    """只携带稳定错误码；不得包含 Apple 响应、签名密钥或底层异常。"""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class AppleReview(BaseModel):
    """与外部 JSON 命名隔离的不可变评论，时间必须包含时区。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(min_length=1, max_length=128)
    rating: int = Field(ge=1, le=5, strict=True)
    title: str = Field(max_length=1000)
    body: str = Field(max_length=20000)
    reviewer_nickname: str = Field(max_length=256)
    created_at: AwareDatetime
    territory: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class ReviewApp(BaseModel):
    """由项目提供的应用显示名称，不包含运行环境或全局设置。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1, max_length=128)


class AppleReviewsConfig(BaseModel):
    """仅消费显式参数；账号 API 密钥用于已列出的 App 评论读取。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    apps: dict[ASCAppID, ReviewApp] = Field(min_length=1, max_length=100)
    issuer_id: str = Field(min_length=36, max_length=36,
                           pattern=r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
    key_id: str = Field(min_length=10, max_length=10, pattern=r"^[A-Z0-9]{10}$")
    private_key: SecretStr = Field(min_length=1, max_length=16384, repr=False)
    poll_interval_seconds: int = Field(default=3600, ge=60, le=604800)
    retention_days: int = Field(default=30, ge=1, le=3650)
    discord_webhook_url: Destination = Field(default=None, max_length=2048, repr=False)
