<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## response — 统一响应

\`\`\`python
from dwyeapi.response import success, fail, paginated
\`\`\`

| 函数 | 签名 | 返回结构 |
|------|------|---------|
| success | \`(data=None, message="success") -> dict\` | \`{"code": 200, "message": ..., "data": ..., "timestamp": ...}\` |
| fail | \`(code=400, message="fail") -> dict\` | \`{"code": ..., "message": ..., "data": None, "timestamp": ...}\` |
| paginated | \`(items, total, page, page_size) -> dict\` | success 包装 \`{"items": [...], "total": N, "page": N, "page_size": N}\` |

### 使用示例

\`\`\`python
@router.get("/users/{user_id}")
async def get_user(user_id: int, service=Depends(get_user_service)):
    user = await service.get_by_id(user_id)
    return success(data=UserResponse.model_validate(user))

@router.get("/users")
async def list_users(params: PaginationParams = Depends(), service=Depends(get_user_service)):
    items, total = await service.list(params)
    return paginated(items, total, params.page, params.page_size)
\`\`\`

### 响应格式示例

**success 响应：**

\`\`\`json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "name": "Alice" },
  "timestamp": 1711872000
}
\`\`\`

**fail 响应：**

\`\`\`json
{
  "code": 400,
  "message": "参数错误",
  "data": null,
  "timestamp": 1711872000
}
\`\`\`

**paginated 响应：**

\`\`\`json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [{ "id": 1, "name": "Alice" }],
    "total": 50,
    "page": 1,
    "page_size": 20
  },
  "timestamp": 1711872000
}
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
