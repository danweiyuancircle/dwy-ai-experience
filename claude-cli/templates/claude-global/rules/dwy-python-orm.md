---
description: SQLAlchemy 2.0 异步 ORM 规范
paths:
  - "**/models/**/*.py"
  - "**/database.py"
  - "**/db.py"
---

# SQLAlchemy 2.0 异步 ORM 规范

## 九、数据库与 ORM

### 强制规则
- 使用 **SQLAlchemy 2.0** 风格（声明式映射 + async）
- 数据库迁移使用 **Alembic**，**禁止**手动执行 DDL
- **禁止**在路由层直接写 SQL 查询

```python
# models/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

# models/user.py
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
```

### 异步数据库会话

```python
# config.py / database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

### 查询规范

```python
# ❌ 旧式查询
session.query(User).filter(User.id == user_id).first()

# ✅ SQLAlchemy 2.0 风格
result = await session.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```
