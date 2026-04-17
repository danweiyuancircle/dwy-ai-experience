---
description: API URL/响应格式/状态码/Schema 命名 + JWT/RBAC 认证方案
paths:
  - "**/routers/**/*.py"
  - "**/schemas/**/*.py"
  - "**/services/**/*.py"
  - "**/dependencies.py"
  - "**/main.py"
---

# API 设计与认证规范

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

---

## 五、认证方案(JWT + RBAC)

### 5.1 Token 体系

使用 eapi security 模块,禁止自实现 JWT。

```python
from danweiyuan_eapi.security import create_token, decode_token, hash_password, verify_password

# 登录时
access_token = create_token(
    data={"sub": str(user.id), "role": user.role},
    secret=settings.secret_key,
    expires_minutes=settings.access_token_expire_minutes,
)
refresh_token = create_token(
    data={"sub": str(user.id), "type": "refresh"},
    secret=settings.secret_key,
    expires_minutes=60 * 24 * 7,  # 7 天
)
```

**双 Token 流程:**
1. 登录 → 返回 access_token (短期, 30min) + refresh_token (长期, 7天)
2. 请求携带 `Authorization: Bearer {access_token}`
3. access_token 过期 → 前端用 refresh_token 换新 token
4. refresh_token 过期 → 重新登录

### 5.2 后端认证依赖

```python
# dependencies.py
from fastapi import Depends, Header
from danweiyuan_eapi.security import decode_token
from danweiyuan_eapi.exceptions import AuthenticationError, PermissionDeniedError

async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token, settings.secret_key)
    if payload is None:
        raise AuthenticationError()
    user = await db.get(User, int(payload["sub"]))
    if user is None:
        raise AuthenticationError()
    return user

def require_role(*roles: str):
    """权限校验依赖工厂"""
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDeniedError()
        return user
    return checker
```

### 5.3 前端 Token 管理

```typescript
// stores/auth.ts — 使用 ekit storage 存储
import { storage } from '@danweiyuan/ekit'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(storage.get('access_token') || '')
  const refreshToken = ref(storage.get('refresh_token') || '')

  function setTokens(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    storage.set('access_token', access)
    storage.set('refresh_token', refresh)
  }

  function clearTokens() {
    token.value = ''
    refreshToken.value = ''
    storage.remove('access_token')
    storage.remove('refresh_token')
  }

  return { token, refreshToken, setTokens, clearTokens }
})
```

```typescript
// api/client.ts — 使用 ekit request + refreshToken 插件
import { createRequest } from '@danweiyuan/ekit'

export const request = createRequest({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  plugins: [
    tokenPlugin(),         // 自动注入 Authorization header
    refreshTokenPlugin(),  // 401 时自动刷新 token
    unwrapPlugin(),        // 解包 {code, data, message} → data
  ],
})
```

### 5.4 前端路由守卫

```typescript
// router/index.ts
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```

### 5.5 Flutter 认证

```dart
// core/storage/token_storage.dart
class TokenStorage {
  static const _storage = FlutterSecureStorage();
  static Future<void> saveTokens(String access, String refresh) async { ... }
  static Future<String?> getAccessToken() async { ... }
  static Future<void> clear() async { ... }
}

// GoRouter redirect
redirect: (context, state) {
  final isLoggedIn = ref.read(authProvider).isAuthenticated;
  final isLoginRoute = state.matchedLocation == '/login';
  if (!isLoggedIn && !isLoginRoute) return '/login';
  if (isLoggedIn && isLoginRoute) return '/';
  return null;
}
```

### 5.6 RBAC 权限模型

数据库表结构(最小可用,按需扩展):

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")  # "admin" | "user" | 自定义
    is_active: Mapped[bool] = mapped_column(default=True)
```

简单项目用单字段 `role`;如需细粒度权限,扩展为角色表 + 权限表 + 关联表。
