<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## dependencies — FastAPI 依赖注入

\`\`\`python
from danweiyuan_base.dependencies import create_get_db
\`\`\`

### create_get_db(session_factory)

生成 \`get_db\` FastAPI Depends 函数，自动管理会话生命周期。

\`\`\`python
get_db = create_get_db(session_factory)

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    ...
\`\`\`

### 工作原理

\`create_get_db\` 返回一个异步生成器函数，用于 FastAPI 的 \`Depends\` 注入：

1. 请求开始时，从 \`session_factory\` 创建一个 \`AsyncSession\`
2. 通过 \`yield\` 将会话提供给路由函数
3. 请求结束时（无论成功或异常），自动关闭会话

### 完整接入示例

\`\`\`python
# database.py
from danweiyuan_base.database import create_async_engine_factory, create_session_factory
from danweiyuan_base.dependencies import create_get_db

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)
\`\`\`

\`\`\`python
# routers/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("用户")
    return success(data=UserResponse.model_validate(user))
\`\`\`

### 设计要点

- **工厂模式：** \`create_get_db\` 是工厂函数，接收 \`session_factory\` 返回 Depends 函数
- **自动生命周期：** 会话在请求结束时自动关闭，无需手动管理
- **与 service 层配合：** 可将 \`get_db\` 注入到 service 工厂函数中

\`\`\`python
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
