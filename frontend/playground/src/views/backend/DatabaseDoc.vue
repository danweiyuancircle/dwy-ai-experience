<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## database — 异步 SQLAlchemy

\`\`\`python
from danweiyuan_base.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory
\`\`\`

### 模型定义

\`\`\`python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    # TimestampMixin 自动添加 created_at, updated_at
\`\`\`

### 引擎和会话

\`\`\`python
engine = create_async_engine_factory(settings.database_url, echo=settings.debug)
# 参数: database_url, pool_size=5, max_overflow=10, echo=False
# SQLite 自动跳过连接池参数

session_factory = create_session_factory(engine)
# 返回 async_sessionmaker[AsyncSession]，expire_on_commit=False
\`\`\`

### API 参考

#### Base

SQLAlchemy 声明式基类（\`DeclarativeBase\`），所有 ORM 模型必须继承。

#### TimestampMixin

自动添加 \`created_at\` 和 \`updated_at\` 字段，使用数据库 \`server_default=func.now()\`。

#### create_async_engine_factory(database_url, pool_size=5, max_overflow=10, echo=False)

创建异步 SQLAlchemy 引擎。SQLite URL 时自动跳过连接池参数。

#### create_session_factory(engine)

基于引擎创建异步会话工厂，返回 \`async_sessionmaker[AsyncSession]\`，\`expire_on_commit=False\`。

### 完整接入示例

\`\`\`python
# database.py
from danweiyuan_base.database import Base, create_async_engine_factory, create_session_factory
from danweiyuan_base.dependencies import create_get_db

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
