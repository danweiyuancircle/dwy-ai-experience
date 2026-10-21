"""不把 Google 凭据当作应用会话；凭据字段不进入 repr 或验证错误。"""

from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuthError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 401):
        super().__init__(message)
        self.code, self.message, self.status_code = code, message, status_code


class GoogleConfig(BaseModel):
    """一个应用使用独立的 Web OAuth client ID；无需 client secret。"""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    client_id: str = Field(
        min_length=20, max_length=255, pattern=r"^[0-9]+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com$"
    )


class GoogleIdentity(BaseModel):
    """只能由完成验签的可信适配器返回；邮箱不作为账户关联键。"""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)
    subject: str = Field(min_length=1, max_length=255, pattern=r"^[^\x00-\x20\x7f]+$")
    email: str | None = Field(default=None, max_length=320)
    display_name: str | None = Field(default=None, max_length=255)


class GoogleVerifier(Protocol):
    async def verify(self, id_token: str) -> GoogleIdentity: ...


class UserProfile(BaseModel):
    id: UUID
    email: str | None
    display_name: str | None


class TokenResponse(BaseModel):
    access_token: str = Field(repr=False)
    refresh_token: str = Field(repr=False)
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: Literal[900] = 900
    user: UserProfile


class DeviceQuery(BaseModel):
    """设备分页只允许显式游标与最多一百项。"""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    limit: int = Field(default=50, ge=1, le=100)
    cursor: UUID | None = None


class DeviceSummary(BaseModel):
    """仅返回本人活跃设备元数据，不公开会话标识或凭据摘要。"""

    model_config = ConfigDict(extra="forbid")
    device_id: UUID
    first_seen_at: int = Field(ge=0)
    last_login_at: int = Field(ge=0)
    active_sessions: int = Field(ge=1)
    current: bool


class DevicePage(BaseModel):
    """设备 UUID 升序分页，游标不包含用户身份。"""

    model_config = ConfigDict(extra="forbid")
    devices: list[DeviceSummary] = Field(max_length=100)
    next_cursor: UUID | None = None


class AccountDeletion(BaseModel):
    """同事务去标识、撤销会话与业务清理全部完成后才返回成功。"""

    model_config = ConfigDict(extra="forbid")
    status: Literal["completed"] = "completed"
