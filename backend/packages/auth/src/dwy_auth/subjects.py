"""应用主体适配：认证库不声明或假设任何业务 User 表。"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from .providers import ExternalIdentity


@dataclass(frozen=True)
class SubjectRegistration:
    """已通过身份验证的初始化资料；邮箱仅为资料，不用于合并账号。"""

    method: str
    email: str | None = None
    external_identity: "ExternalIdentity | None" = None


class SubjectAdapter(Protocol):
    """宿主接收当前事务，不得 commit、close 或另开事务初始化主体。"""

    async def create_subject(self, db: AsyncSession, registration: SubjectRegistration) -> str:
        """返回稳定、不透明且最多 255 字符的 subject。"""
        ...

    async def is_active(self, db: AsyncSession, subject: str) -> bool:
        """检查主体存在且允许认证；敏感写入时应锁定对应业务行。"""
        ...
