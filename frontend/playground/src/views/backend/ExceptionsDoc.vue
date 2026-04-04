<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## exceptions — 异常体系

\`\`\`python
from danweiyuan_eapi.exceptions import (
    AppError, NotFoundError, BusinessError, PermissionDeniedError, AuthenticationError,
    register_exception_handlers,
)
\`\`\`

### 异常层级

| 异常类 | HTTP 状态码 | code | message |
|--------|-----------|------|---------|
| AppError(message, code) | — | 自定义 | 自定义 |
| NotFoundError(resource) | 404 | \`NOT_FOUND\` | \`{resource}不存在\` |
| BusinessError(message, code) | 422 | 自定义 | 自定义 |
| PermissionDeniedError() | 403 | \`PERMISSION_DENIED\` | \`权限不足\` |
| AuthenticationError() | 401 | \`AUTHENTICATION_FAILED\` | \`认证失败\` |

### 注册到 FastAPI

\`\`\`python
app = FastAPI()
register_exception_handlers(app)
# 之后在 service 层直接 raise NotFoundError("用户") 即可返回 404
\`\`\`

响应格式统一为 \`{"code": "ERROR_CODE", "message": "描述"}\`。

### 使用原则

- **service 层**抛业务异常（NotFoundError, BusinessError 等）
- **router 层**不写 try/except，由 register_exception_handlers 统一处理
- **禁止**在 service 层抛 HTTPException

### 示例

\`\`\`python
# service 层
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError("用户")
        return user

# router 层 — 无需 try/except
@router.get("/users/{user_id}")
async def get_user(user_id: int, service=Depends(get_user_service)):
    user = await service.get_by_id(user_id)
    return success(data=UserResponse.model_validate(user))
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
