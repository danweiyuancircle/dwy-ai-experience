"""管理员认证配置由宿主显式注入，不读取环境变量或业务配置。"""

from urllib.parse import urlsplit

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, SecretStr, field_validator


class AdminAuthConfig(BaseModel):
    """一个独立管理员 Cookie 边界；生产宿主负责启用策略与密码强度。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    username: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.@-]+$")
    password: SecretStr = Field(min_length=12, max_length=256, repr=False)
    session_seconds: int = Field(default=28800, ge=300, le=86400)
    secure_cookie: bool = False
    origin: str | None = Field(default=None, max_length=2048)

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value: str | None) -> str | None:
        """只接受单个完整 HTTP origin，保持与可信部署值精确比较。"""
        if value is None:
            return None
        if any(ord(char) <= 32 or ord(char) == 127 for char in value):
            raise ValueError("origin must be a single HTTP origin")
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.path
            or "?" in value
            or "#" in value
            or "\\" in value
            or parsed.username is not None
            or parsed.password is not None
            or parsed.netloc.endswith(":")
        ):
            raise ValueError("origin must contain only scheme, host and optional port")
        AnyHttpUrl(value)
        return value
