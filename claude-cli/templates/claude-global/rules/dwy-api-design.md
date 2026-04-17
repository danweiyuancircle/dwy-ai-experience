---
description: 后端 API URL/响应格式/状态码/Schema 命名规范
paths:
  - "**/routers/**/*.py"
  - "**/schemas/**/*.py"
  - "**/services/**/*.py"
  - "**/dependencies.py"
  - "**/main.py"
---

# API 设计规范

---

## 一、URL 命名

```
基础格式: /api/{resource}

GET    /api/users              # 列表(支持分页)
POST   /api/users              # 创建
GET    /api/users/{id}         # 详情
PATCH  /api/users/{id}         # 部分更新
DELETE /api/users/{id}         # 删除

# 子资源
GET    /api/users/{id}/orders  # 用户的订单列表

# 动作(非 CRUD,用 POST + 动词)
POST   /api/users/{id}/activate
POST   /api/tasks/{id}/cancel
POST   /api/tasks/{id}/retry
```

**规则:**
- 资源名用复数、kebab-case:`/api/upload-tasks`(不是 `uploadTasks` 或 `upload_task`)
- 路径参数用 `{id}` 不用 `{user_id}`(除非有歧义)
- 查询参数用 snake_case:`?page_size=20&task_type=export`
- 所有路由加 `/api` 前缀
- 禁止在 URL 中包含动词(用 HTTP 方法区分),但非 CRUD 操作例外

## 二、统一响应格式

所有 API 使用 eapi response 模块的标准格式:

**成功响应(`response.success()`):**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1712467200
}
```

**分页响应(`response.paginated()`):**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20
  },
  "timestamp": 1712467200
}
```

**错误响应(eapi 异常处理器自动生成):**
```json
{
  "code": "NOT_FOUND",
  "message": "用户不存在"
}
```

**禁止:** 自造响应格式、在 router 中手动构造 `{"success": true, ...}` 等非标准格式。

## 三、HTTP 状态码

| 场景 | 状态码 | 说明 |
|------|--------|------|
| 查询/更新成功 | 200 | GET / PATCH 默认 |
| 创建成功 | 201 | POST 创建资源 |
| 删除成功 | 204 | DELETE,无响应体 |
| 参数错误 | 400 | 请求格式错误 |
| 未认证 | 401 | Token 缺失或过期 |
| 无权限 | 403 | 认证通过但权限不足 |
| 资源不存在 | 404 | — |
| 业务错误 | 422 | 参数合法但业务规则不允许 |

## 四、Pydantic Schema 命名约定

```python
# 创建请求
class UserCreate(BaseModel): ...

# 更新请求(所有字段可选)
class UserUpdate(BaseModel): ...

# 响应
class UserResponse(BaseModel): ...

# 列表项(精简字段)
class UserBrief(BaseModel): ...
```

请求和响应**必须分离**,禁止同一个 Schema 同时用于请求和响应。
