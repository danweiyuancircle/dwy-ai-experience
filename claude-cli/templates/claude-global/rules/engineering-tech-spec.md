# 工程开发技术规范

本规范约束所有项目的技术选型、架构模式和基础设施配置。AI 在任何项目中写代码时必须遵守。

> 语言/框架级编码规范见独立文件：`vue-code-style.md`、`python-code-style.md`、`flutter-code-style.md`。本文件只定义跨端、跨项目的架构约束。

---

## 一、技术选型强制约束

每个领域只有一个方案，AI 不得选择替代方案，不得"建议改用 XX"。

### 后端

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| Web 框架 | FastAPI | Django, Flask, Tornado, Sanic |
| ORM | SQLAlchemy 2.0 (异步) | Tortoise ORM, Peewee, Django ORM |
| 关系数据库 | PostgreSQL | MySQL, MariaDB, SQLite(生产) |
| 缓存 / 消息队列 | Redis | Memcached, RabbitMQ, Kafka |
| 异步任务 | ARQ (eapi[tasks]) | Celery, Dramatiq, Huey |
| 数据库迁移 | Alembic | 手动 DDL, Django migrations |
| 包管理 | UV | pip, Poetry, Pipenv |
| 密码哈希 | bcrypt (eapi security) | argon2, scrypt, 自实现 |
| JWT | python-jose (eapi security) | PyJWT, 自实现 |
| 数据校验 | Pydantic v2 | marshmallow, attrs, 手动校验 |
| 基础设施层 | danweiyuan-eapi | 自造框架、手写基础设施 |
| Linter/Formatter | Ruff | Black, isort, flake8, pylint |

### 前端（Web）

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| 框架 | Vue 3 (Composition API) | React, Svelte, Angular, Vue 2 |
| 构建工具 | Vite | Webpack, Rollup, esbuild 直接用 |
| 组件库 | @danweiyuan/eui | Element Plus, Ant Design Vue, Naive UI |
| 工具库 | @danweiyuan/ekit | 手写 request/storage/validators |
| 状态管理 | Pinia (Setup Store) | Vuex, 手动 reactive/provide |
| 样式 | Tailwind CSS 4 | Sass/Less 手写、CSS Modules、UnoCSS |
| 包管理 | pnpm | npm, yarn |
| 项目结构 | pnpm monorepo (workspace) | Lerna, Nx, Turborepo |
| 表单校验 | vee-validate + zod | 手动 v-model 校验 |
| 路由 | Vue Router 4 | — |
| 测试 | Vitest | Jest |

### 移动端 / 桌面端

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| 框架 | Flutter | React Native, Kotlin Multiplatform, MAUI |
| 状态管理 | Riverpod | GetX, Bloc, Provider, MobX |
| HTTP 客户端 | Dio | http, Chopper, Retrofit |
| 路由 | GoRouter | auto_route, Routemaster |
| 本地存储 | shared_preferences + flutter_secure_storage | Hive, Isar, sqflite(非必要时) |
| 代码生成 | riverpod_generator + freezed + json_serializable | 手写 fromJson/toJson |

### 基础设施

| 领域 | 唯一方案 | 禁止替代 |
|------|---------|---------|
| 容器化 | Docker + Docker Compose | Podman, 裸机部署 |
| 对象存储(开发) | MinIO (S3 协议) | 本地文件系统 |
| 对象存储(生产) | 任何 S3 兼容云服务 | 非 S3 协议的私有 API |
| 时序数据库(量化金融) | DolphinDB | ClickHouse, TimescaleDB, InfluxDB |

---

## 二、项目目录结构模板

AI 创建文件时**必须**遵循以下目录结构，不得自造目录名或层级。

### 2.1 后端项目（FastAPI）

```
backend/
├── src/app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口 + lifespan
│   ├── config.py             # 继承 eapi BaseSettings
│   ├── database.py           # create_async_engine_factory + create_session_factory
│   ├── dependencies.py       # FastAPI Depends（get_db, get_current_user）
│   ├── exceptions.py         # 项目级异常（继承 eapi AppError）
│   ├── validators.py         # 输入校验工具（防注入等）
│   ├── models/               # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py           # 每个实体一个文件
│   │   └── ...
│   ├── schemas/              # Pydantic v2 请求/响应模型
│   │   ├── __init__.py
│   │   ├── user.py           # UserCreate, UserUpdate, UserResponse
│   │   └── ...
│   ├── routers/              # FastAPI 路由（按业务域拆分）
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证端点
│   │   ├── user.py           # 每个业务域一个文件
│   │   └── ...
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py           # 与 router 同名，一一对应
│   │   └── ...
│   ├── tasks.py              # ARQ 任务注册（@register 装饰器）
│   └── worker.py             # ARQ Worker 入口
├── alembic/                  # 数据库迁移
│   ├── versions/             # 迁移文件
│   ├── env.py
│   └── alembic.ini
├── scripts/                  # 初始化/运维脚本
│   ├── init_db.py            # 初始化数据库表结构
│   └── seed_admin.py         # 创建初始管理员
├── tests/
│   ├── conftest.py           # pytest fixtures（SQLite 内存库、mock）
│   ├── test_auth.py          # 与 routers/ 同名
│   └── ...
├── pyproject.toml            # UV 依赖配置
├── Dockerfile.dev            # 开发容器（--reload）
├── Dockerfile.prod           # 生产容器（只读、non-root）
├── .env.example              # 环境变量模板
└── TEST_CASES.md             # 测试用例清单
```

**强制规则：**
- 分层：`routers → schemas → services → models → database`，不可跨层调用
- services 层抛 eapi 异常（AppError 子类），**不抛 HTTPException**
- routers 层只做参数接收和 response 包装，**不写业务逻辑**
- models/ schemas/ routers/ services/ 四个目录内文件按业务域一一对应

### 2.2 前端项目（Vue 3）

```
frontend/
├── src/
│   ├── main.ts               # createApp + 插件注册
│   ├── App.vue               # 根组件
│   ├── router/
│   │   └── index.ts          # Vue Router 配置 + 守卫
│   ├── stores/               # Pinia Setup Store
│   │   ├── auth.ts           # 认证状态
│   │   └── ...
│   ├── api/                  # HTTP 客户端（按业务域拆分）
│   │   ├── client.ts         # ekit createRequest() 实例
│   │   ├── auth.ts           # 登录/注册接口
│   │   ├── user.ts           # 用户接口
│   │   └── ...
│   ├── views/                # 页面级组件（路由对应）
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   └── ...
│   ├── components/           # 共享 UI 组件（非页面级）
│   ├── composables/          # Vue 3 组合式函数（use* 前缀）
│   ├── utils/                # 纯工具函数
│   └── index.css             # Tailwind CSS 入口
├── tests/
│   ├── api/
│   ├── stores/
│   ├── router/
│   └── utils/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile                # 生产构建（多阶段）
└── TEST_CASES.md
```

**强制规则：**
- views/ 放页面组件（路由直接引用），components/ 放复用组件
- api/ 每个文件对应后端一个 router 模块，保持命名一致
- stores/ 统一 Setup Store 写法（`export const useXxxStore = defineStore('xxx', () => {...})`）

### 2.3 Flutter 项目

```
lib/
├── main.dart                  # runApp + ProviderScope
├── app.dart                   # MaterialApp.router + GoRouter
├── core/
│   ├── config/
│   │   └── env.dart           # 环境配置
│   ├── network/
│   │   ├── dio_client.dart    # Dio 实例 + 拦截器
│   │   └── api_response.dart  # 统一响应模型（对齐 eapi 格式）
│   ├── storage/
│   │   └── secure_storage.dart
│   ├── theme/
│   │   └── app_theme.dart     # ThemeData + 设计 tokens
│   └── utils/
├── features/                  # 按功能模块拆分（feature-first）
│   └── {feature_name}/
│       ├── data/
│       │   ├── {feature}_repository.dart   # Repository 实现
│       │   └── {feature}_dto.dart          # 数据传输对象
│       ├── domain/
│       │   └── {feature}_entity.dart       # 领域实体
│       └── presentation/
│           ├── {feature}_page.dart         # 页面
│           ├── {feature}_provider.dart     # Riverpod Provider
│           └── widgets/                    # 功能内专属 Widget
├── shared/
│   ├── providers/             # 全局 Provider（auth, theme）
│   ├── widgets/               # 跨功能共享 Widget
│   └── models/                # 共享数据模型
test/
├── features/
│   └── {feature_name}/
└── core/
```

**强制规则：**
- features/ 按功能模块拆分，每个模块自包含 data/domain/presentation
- core/ 放全局基础设施（网络、存储、主题），不放业务代码
- shared/ 放跨功能共享的 provider/widget/model

### 2.4 Monorepo 项目结构（pnpm workspace）

当项目包含前端 + 后端时，使用 monorepo：

```
project-root/
├── backend/                   # FastAPI 后端（上述 2.1 结构）
├── frontend/                  # Vue 前端（上述 2.2 结构）
├── mobile/                    # Flutter 移动端（上述 2.3 结构，独立管理）
├── docker-compose.dev.yml     # 开发环境
├── docker-compose.prod.yml    # 生产环境
├── dev.sh                     # 一键启动脚本
├── pnpm-workspace.yaml        # pnpm monorepo 配置
├── package.json               # 根 package.json（scripts）
├── CLAUDE.md                  # 项目规范
└── .env.example               # 全局环境变量模板
```

**注意：** Flutter 项目（mobile/）不纳入 pnpm workspace，独立用 `flutter pub get` 管理依赖。

---

## 三、API 设计规范

### 3.1 URL 命名

```
基础格式: /api/{resource}

GET    /api/users              # 列表（支持分页）
POST   /api/users              # 创建
GET    /api/users/{id}         # 详情
PATCH  /api/users/{id}         # 部分更新
DELETE /api/users/{id}         # 删除

# 子资源
GET    /api/users/{id}/orders  # 用户的订单列表

# 动作（非 CRUD，用 POST + 动词）
POST   /api/users/{id}/activate
POST   /api/tasks/{id}/cancel
POST   /api/tasks/{id}/retry
```

**规则：**
- 资源名用复数、kebab-case：`/api/upload-tasks`（不是 `uploadTasks` 或 `upload_task`）
- 路径参数用 `{id}` 不用 `{user_id}`（除非有歧义）
- 查询参数用 snake_case：`?page_size=20&task_type=export`
- 所有路由加 `/api` 前缀
- 禁止在 URL 中包含动词（用 HTTP 方法区分），但非 CRUD 操作例外

### 3.2 统一响应格式

所有 API 使用 eapi response 模块的标准格式：

**成功响应（`response.success()`）：**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1712467200
}
```

**分页响应（`response.paginated()`）：**
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

**错误响应（eapi 异常处理器自动生成）：**
```json
{
  "code": "NOT_FOUND",
  "message": "用户不存在"
}
```

**禁止：** 自造响应格式、在 router 中手动构造 `{"success": true, ...}` 等非标准格式。

### 3.3 HTTP 状态码

| 场景 | 状态码 | 说明 |
|------|--------|------|
| 查询/更新成功 | 200 | GET / PATCH 默认 |
| 创建成功 | 201 | POST 创建资源 |
| 删除成功 | 204 | DELETE，无响应体 |
| 参数错误 | 400 | 请求格式错误 |
| 未认证 | 401 | Token 缺失或过期 |
| 无权限 | 403 | 认证通过但权限不足 |
| 资源不存在 | 404 | — |
| 业务错误 | 422 | 参数合法但业务规则不允许 |

### 3.4 Pydantic Schema 命名约定

```python
# 创建请求
class UserCreate(BaseModel): ...

# 更新请求（所有字段可选）
class UserUpdate(BaseModel): ...

# 响应
class UserResponse(BaseModel): ...

# 列表项（精简字段）
class UserBrief(BaseModel): ...
```

请求和响应**必须分离**，禁止同一个 Schema 同时用于请求和响应。

---

## 四、认证方案（JWT + RBAC）

### 4.1 Token 体系

使用 eapi security 模块，禁止自实现 JWT。

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

**双 Token 流程：**
1. 登录 → 返回 access_token (短期, 30min) + refresh_token (长期, 7天)
2. 请求携带 `Authorization: Bearer {access_token}`
3. access_token 过期 → 前端用 refresh_token 换新 token
4. refresh_token 过期 → 重新登录

### 4.2 后端认证依赖

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

### 4.3 前端 Token 管理

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

### 4.4 前端路由守卫

```typescript
// router/index.ts
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```

### 4.5 Flutter 认证

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

### 4.6 RBAC 权限模型

数据库表结构（最小可用，按需扩展）：

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")  # "admin" | "user" | 自定义
    is_active: Mapped[bool] = mapped_column(default=True)
```

简单项目用单字段 `role`；如需细粒度权限，扩展为角色表 + 权限表 + 关联表。

---

## 五、数据库迁移规范（Alembic）

### 5.1 初始化

```bash
cd backend
alembic init alembic
```

### 5.2 配置

```python
# alembic/env.py — 必须配置项
from app.database import Base        # 导入 ORM Base
from app.models import *             # 导入所有模型（确保被扫描到）
target_metadata = Base.metadata
```

### 5.3 工作流

```bash
# 模型变更后生成迁移
alembic revision --autogenerate -m "add user table"

# 执行迁移（dev 和 prod 相同）
alembic upgrade head

# 回滚一步
alembic downgrade -1
```

### 5.4 强制规则

- 每次 model 变更**必须**生成 migration 文件，禁止手动 `CREATE TABLE`
- 迁移文件**必须**提交到 git，dev 和 prod 共用同一套迁移
- 生产数据库只通过 `alembic upgrade head` 变更 schema
- 迁移文件命名：Alembic 自动生成 revision ID + 人类可读描述
- 禁止在迁移文件中写业务数据操作（seed data 放 scripts/ 目录）

---

## 六、错误处理规范

### 6.1 后端

**唯一方式：** 使用 eapi exceptions 体系。

```python
from danweiyuan_eapi.exceptions import (
    NotFoundError,          # 404 — 资源不存在
    BusinessError,          # 422 — 业务规则不允许
    PermissionDeniedError,  # 403 — 无权限
    AuthenticationError,    # 401 — 认证失败
)

# services 层
async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("用户")     # → {"code": "NOT_FOUND", "message": "用户不存在"}
    return user

async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
    if data.amount <= 0:
        raise BusinessError("订单金额必须大于 0", code="INVALID_AMOUNT")
    ...
```

**禁止清单：**
| 禁止写法 | 正确写法 |
|---------|---------|
| `raise HTTPException(status_code=404)` | `raise NotFoundError("资源名")` |
| `try: ... except Exception: pass` | 只捕获预期的具体异常 |
| 自定义异常类不继承 AppError | 项目异常必须继承 `AppError` |
| 在 router 中 try/except 包 service 调用 | 让异常自然冒泡到 handler |

### 6.2 前端（Vue）

通过 ekit request 插件统一处理：

```typescript
// 在 api/client.ts 配置拦截器后，业务代码不需要 try/catch
// 401 → refreshToken 插件自动刷新，失败则跳登录
// 422 → unwrap 插件抛出错误，页面级 catch 显示 message
// 其他错误 → 全局错误提示
```

**禁止：** 每个 API 调用都包 try/catch，应在页面级或 store 级统一处理。

### 6.3 Flutter

Dio interceptor 统一处理，模式与前端对齐：

```dart
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.response?.statusCode) {
      case 401: // → 跳转登录
      case 403: // → 提示无权限
      case 422: // → 提取 message 显示
    }
    handler.next(err);
  }
}
```

---

## 七、环境变量管理

### 7.1 后端（eapi BaseSettings + 嵌套分组）

**必须使用嵌套模型分组配置**，禁止所有字段平铺。同一服务/SDK 的多个字段拆成独立 `BaseModel`。

```python
# app/config.py
from pydantic import BaseModel
from danweiyuan_eapi.config import BaseSettings

class OssConfig(BaseModel):
    endpoint: str = ""
    access_key: str = ""
    secret_key: str = ""
    bucket: str = ""

class Settings(BaseSettings):
    # eapi 内置字段保持顶层：database_url, redis_url, secret_key, ...

    # 项目专属 — 嵌套分组
    app_name: str = "My App"
    oss: OssConfig = OssConfig()
```

**`.env` 中用 `__` 双下划线分隔层级：**

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
OSS__ENDPOINT=http://localhost:9000
OSS__ACCESS_KEY=minioadmin
OSS__SECRET_KEY=minioadmin
OSS__BUCKET=my-app
```

**代码中通过属性链访问：** `settings.oss.endpoint`，禁止 `settings.oss_endpoint`。

详细规则见 `python-code-style.md` 第十二节。

### 7.2 前端（Vite）

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=/api
```

代码中通过 `import.meta.env.VITE_API_BASE_URL` 访问。**只有 `VITE_` 前缀的变量会暴露给客户端。**

### 7.3 Flutter

使用编译时注入或 `.env` + `flutter_dotenv`：

```bash
# .env
API_BASE_URL=http://localhost:8000/api

# 或编译时注入
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api
```

### 7.4 强制规则

| 规则 | 说明 |
|------|------|
| 每个项目必须有 `.env.example` | 列出所有变量名 + 注释说明，值用占位符 |
| `.env` 文件禁止提交 git | 已在 git-security.md 约束 |
| 禁止硬编码 | 数据库连接、密钥、API 地址等必须走环境变量 |
| 禁止运行时读取 `.env` 文件 | 后端用 BaseSettings（启动时加载），前端用 Vite 编译注入 |

---

## 八、日志规范

### 8.1 后端

使用 Python 标准 `logging` 模块：

```python
import logging

logger = logging.getLogger(__name__)

# 正确用法
logger.info("用户 %s 登录成功", user_id)
logger.error("导出任务失败: task_id=%s, error=%s", task_id, str(e))

# 禁止
print("debug info")                    # 禁止 print
logger.info(f"用户 {user_id} 登录")    # 禁止 f-string（无法被日志聚合）
```

### 8.2 日志级别规则

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 开发调试信息，生产环境不输出 | 变量值、SQL 语句 |
| INFO | 关键业务流程节点 | 用户登录、任务提交、导出完成 |
| WARNING | 异常但可恢复的情况 | 重试成功、降级处理 |
| ERROR | 错误但服务仍可用（单次请求失败） | 外部 API 超时、单个任务失败 |
| CRITICAL | 服务不可用 | 数据库连接断开、必要服务宕机 |

### 8.3 禁止事项

- 禁止 `print()`，全部用 `logger`
- 禁止在循环体内打 INFO/WARNING 日志（大量重复）
- 禁止日志中包含密码、token、密钥等敏感信息
- 禁止用 f-string 格式化日志消息（用 `%s` 占位符，支持日志聚合延迟求值）

---

## 九、状态管理规范

| 平台 | 方案 | 详细规范 |
|------|------|---------|
| Vue | Pinia Setup Store | 见 `vue-code-style.md` 状态管理章节 |
| Flutter | Riverpod | 见 `flutter-code-style.md` 状态管理章节 |

**跨端共识：**
- 认证状态全局管理（Vue: `useAuthStore`，Flutter: `authProvider`）
- 页面级状态就近管理，不上提到全局
- 缓存策略：列表数据按需刷新，不做客户端持久化缓存（除离线场景）

---

## 十、网络层规范

### 10.1 Vue 前端

**唯一方式：** ekit `createRequest()` + 插件。

```typescript
// api/client.ts
import { createRequest } from '@danweiyuan/ekit'

export const request = createRequest({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  plugins: [
    tokenPlugin(),         // 注入 Authorization header
    refreshTokenPlugin(),  // 401 自动刷新
    unwrapPlugin(),        // 解包响应 → data
  ],
})

// api/user.ts — 按业务域拆分
export function getUsers(params: { page: number; page_size: number }) {
  return request.get('/users', { params })
}

export function createUser(data: UserCreate) {
  return request.post('/users', data)
}
```

**禁止：** `axios.create()`、`fetch()`、`new XMLHttpRequest()`

### 10.2 Flutter

**唯一方式：** Dio + 拦截器，封装与 ekit request 对齐。

```dart
// core/network/dio_client.dart
class DioClient {
  late final Dio _dio;

  DioClient({required String baseUrl}) {
    _dio = Dio(BaseOptions(baseUrl: baseUrl))
      ..interceptors.addAll([
        TokenInterceptor(),    // 注入 Authorization header
        RefreshInterceptor(),  // 401 自动刷新
        UnwrapInterceptor(),   // 解包 {code, data, message} → data
        ErrorInterceptor(),    // 统一错误处理
      ]);
  }
}
```

**禁止：** `http.get()`、`HttpClient`、裸 `Dio()` 不加拦截器

### 10.3 响应解包

前端和 Flutter 的解包逻辑必须与后端 eapi response 格式对齐：

```
后端返回: { code: 200, message: "success", data: {...}, timestamp: ... }
                                                  ↓ unwrap
前端/Flutter 拿到: {...}  (直接是 data 的内容)
```

分页响应解包后拿到 `{ items, total, page, page_size }`。

---

## 十一、Docker 规范

每个项目**必须**提供两个 compose 文件，不可合并。

### 11.1 docker-compose.dev.yml（开发环境）

**核心原则：** 快速启动、热更新、方便调试。

```yaml
# docker-compose.dev.yml — 只跑基础设施，应用在宿主机跑
services:
  postgres:
    image: postgres:16
    ports:
      - "${PG_PORT:-15432}:5432"     # 映射到宿主机，方便用 DBeaver 连
    environment:
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "${REDIS_PORT:-16379}:6379"

  minio:
    image: minio/minio
    ports:
      - "${MINIO_PORT:-19000}:9000"
      - "${MINIO_CONSOLE_PORT:-19001}:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

  # 可选：DolphinDB（量化金融项目）
  # dolphindb:
  #   image: dolphindb/dolphindb:v3.00.5
  #   ports:
  #     - "18848:8848"

volumes:
  pgdata:
  miniodata:
```

**关键要点：**
- 基础设施容器化，应用代码在宿主机运行（`uvicorn --reload` / `vite dev`）
- 端口映射到宿主机非标准端口（避免与其他项目冲突），端口用环境变量可配
- volume 持久化数据

### 11.2 docker-compose.prod.yml（生产环境）

**核心原则：** 安全、稳定、最小权限。

```yaml
# docker-compose.prod.yml — 所有服务容器化
services:
  postgres:
    image: postgres:16
    # 不暴露端口（仅内网通信）
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  minio:
    image: minio/minio
    # 不暴露端口
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    command: server /data
    volumes:
      - miniodata:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    read_only: true                    # 只读根文件系统
    tmpfs:
      - /tmp                           # 临时文件写 tmpfs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: arq app.worker.WorkerSettings
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "${WEB_PORT:-3000}:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
  miniodata:
```

**关键要点：**
- 基础设施不暴露端口（仅通过 Docker 网络内部通信）
- 后端容器只读根文件系统 + tmpfs
- 所有服务 `restart: unless-stopped`
- 健康检查确保启动顺序
- 环境变量从 `.env` 注入（不硬编码在 yml 中）

### 11.3 Dockerfile 规范

**后端 Dockerfile.dev：**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e ".[dev]" --system
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**后端 Dockerfile.prod：**
```dockerfile
# 多阶段构建
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e "." --system

FROM python:3.11-slim
RUN useradd -r -s /bin/false appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端 Dockerfile（生产）：**
```dockerfile
FROM node:20-slim AS builder
RUN npm i -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml .
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**强制规则：**
- 生产镜像必须用多阶段构建（builder + runtime）
- 生产镜像必须用 non-root user 运行
- 必须有 `.dockerignore`（排除 node_modules/、.env、__pycache__/、.git/）
- 禁止在镜像中包含 dev 依赖

### 11.4 一键启动脚本

每个项目提供 `dev.sh`：

```bash
#!/bin/bash
# 启动基础设施
docker compose -f docker-compose.dev.yml up -d

# 等待 PostgreSQL 就绪
until docker compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres; do
  sleep 1
done

# 后端（热更新）
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Worker（后台任务）
cd backend && arq app.worker.WorkerSettings &

# 前端（热更新）
cd frontend && pnpm dev &

wait
```

---

## 十二、OSS 规范（MinIO / S3 兼容）

### 12.1 核心原则

**代码只用 S3 协议，不用任何云厂商专有 API。** 通过环境变量切换 dev/prod 存储。

### 12.2 后端封装

```python
# services/oss.py
import boto3
from app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.oss_endpoint,       # dev: http://localhost:19000
        aws_access_key_id=settings.oss_access_key,
        aws_secret_access_key=settings.oss_secret_key,
    )

async def upload_file(key: str, data: bytes, content_type: str = "") -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.oss_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key

async def get_presigned_url(key: str, expires: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.oss_bucket, "Key": key},
        ExpiresIn=expires,
    )
```

### 12.3 环境变量

```bash
# .env.development（MinIO）
OSS_ENDPOINT=http://localhost:19000
OSS_ACCESS_KEY=minioadmin
OSS_SECRET_KEY=minioadmin
OSS_BUCKET=my-app

# .env.production（阿里云 OSS / AWS S3）
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY=your-key
OSS_SECRET_KEY=your-secret
OSS_BUCKET=my-app-prod
```

### 12.4 禁止事项

- 禁止使用 `minio` Python 库（用 `boto3`，S3 协议通用）
- 禁止代码中出现 MinIO / 阿里云 / AWS 等厂商名称判断逻辑
- 禁止硬编码 bucket 名、endpoint 地址

---

## 十三、DolphinDB 规范（量化金融项目专用）

> 仅适用于需要时序数据库的量化金融项目，普通业务项目跳过此章节。

### 13.1 连接池管理

```python
# dolphindb_pool.py — 全局单例
import dolphindb as ddb

_pool: ddb.DBConnectionPool | None = None

def get_pool() -> ddb.DBConnectionPool:
    global _pool
    if _pool is None:
        _pool = ddb.DBConnectionPool(
            host=settings.ddb_host,
            port=settings.ddb_port,
            userid=settings.ddb_user,
            password=settings.ddb_password,
            poolSize=2,  # 社区版限制：最多 2 个连接
        )
    return _pool
```

### 13.2 查询规则

```python
# 正确：WHERE 条件直接命中分区列
script = 'select * from loadTable("dfs://factors", "factor_data") where date = 2024.01.01, code = "000001"'

# 错误：函数包裹分区列（导致全表扫描）
script = 'select * from ... where month(date) = 2024.01M'  # 禁止！
```

### 13.3 强制规则

| 规则 | 说明 |
|------|------|
| 连接池 ≤ 2 | DolphinDB 社区版限制 |
| 批量写入 ≤ 500K 行/批 | 内存安全，超过需分片 |
| WHERE 必须直接命中分区列 | 禁止函数包裹，防止全表扫描 |
| 外部输入必须校验 | 防止 DolphinDB 脚本注入（用 validators.py） |
| 大数据处理后调 `gc.collect()` | 及时释放 DataFrame 内存 |
| 禁止在业务代码中直接拼 DDB 脚本 | 封装到 services 层 |
