<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## response — 统一响应信封

\`\`\`python
from dwyeapi.response import ApiResponse, PageData
# 或
from dwyeapi import ApiResponse, PageData
\`\`\`

> **注意（0.6.0+）：** 已删除 \`success\` / \`fail\` / \`paginated\` 函数。成功用 \`ApiResponse.ok\` / \`ApiResponse.page\`，错误由异常 handler 构造。成功 \`code\` 固定为字符串 \`"SUCCESS"\`，不是数字 \`200\`。

| API | 签名 | 说明 |
|------|------|------|
| ApiResponse.ok | \`(data, message="success") -> ApiResponse[T]\` | 单体成功响应 |
| ApiResponse.page | \`(items, total, page, page_size, message="success") -> ApiResponse[PageData[T]]\` | 分页成功响应 |
| PageData | \`items / total / page / page_size\` | 分页载荷 |

### 使用示例

\`\`\`python
from dwyeapi import ApiResponse
from dwyeapi.pagination import PaginationParams, paginate

@router.get("/users/{user_id}")
async def get_user(user_id: int, service=Depends(get_user_service)):
    user = await service.get_by_id(user_id)
    return ApiResponse.ok(UserResponse.model_validate(user))

@router.get("/users")
async def list_users(params: PaginationParams = Depends(), service=Depends(get_user_service)):
    items, total = await service.list(params)
    return ApiResponse.page(items, total, params.page, params.page_size)
\`\`\`

### 响应格式示例

**成功响应：**

\`\`\`json
{
  "code": "SUCCESS",
  "message": "success",
  "data": { "id": 1, "name": "Alice" },
  "timestamp": 1711872000
}
\`\`\`

**分页响应：**

\`\`\`json
{
  "code": "SUCCESS",
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

**错误响应（由 exception handler 生成）：**

\`\`\`json
{
  "code": "NOT_FOUND",
  "message": "用户不存在",
  "data": null,
  "timestamp": 1711872000
}
\`\`\`

### 设计要点

- 信封统一 \`{code, message, data, timestamp}\`
- HTTP 状态码保留语义（404 仍是 404），前端可按 HTTP + \`code\` 双重判断
- 业务路由**不要**手写 fail 信封，直接 \`raise NotFoundError(...)\` 等
`
</script>

<template>
  <DocPage :content="content" />
</template>
