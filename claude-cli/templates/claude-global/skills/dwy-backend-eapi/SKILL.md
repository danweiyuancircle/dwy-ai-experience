---
name: dwy-backend-eapi
description: "dwyeapi FastAPI 后端基础设施速查。触发条件：使用 FastAPI 构建后端、配置数据库/Redis/JWT/异常处理、耗时任务处理时。"
---

# dwyeapi 后端基础设施速查

FastAPI 项目基础设施包，Python 3.11+，全异步。11 个模块。

> **Tasks 集成指南：** 详见同目录 [tasks-integration-guide.md](tasks-integration-guide.md)

## 安装

```bash
pip install dwyeapi
# 需要任务处理时
pip install dwyeapi[tasks]
```

```python
from dwyeapi.config import BaseSettings
from dwyeapi.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory
from dwyeapi.security import hash_password, verify_password, create_token, decode_token
from dwyeapi.exceptions import NotFoundError, BusinessError, register_exception_handlers
from dwyeapi.response import success, fail, paginated
from dwyeapi.pagination import PaginationParams, paginate
from dwyeapi.cache import configure as configure_redis, get_redis, close_redis
from dwyeapi.dependencies import create_get_db
from dwyeapi import dt
from dwyeapi.masking import mask_phone, mask_email, mask_id_card, mask_name

# 任务模块 (需安装 [tasks] extra)
from dwyeapi.tasks import setup_tasks, task_router, register, TaskContext, TaskStatus, create_worker_settings
```

## 查阅源码

每个模块在 `backend/src/dwyeapi/{module}.py`，单文件设计可直接阅读。

---

## config — Pydantic Settings

```python
from dwyeapi.config import BaseSettings
```

子类化后使用，从 `.env` 或环境变量读取配置。

```python
class Settings(BaseSettings):
    app_name: str = "My API"
    # 继承的必填字段：database_url, redis_url, secret_key
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| database_url | str | **必填** | 异步数据库 URL |
| redis_url | str | **必填** | Redis URL |
| secret_key | str | **必填** | JWT 签名密钥 |
| jwt_algorithm | str | `"HS256"` | JWT 算法 |
| access_token_expire_minutes | int | `30` | Token 过期分钟 |
| environment | `"dev" \| "prod"` | `"prod"` | 运行环境(见下) |
| allowed_origins | list[str] | `[]` | CORS 允许域名 |
| task_max_jobs | int | `5` | Worker 最大并发任务数 |
| task_job_timeout | int | `3600` | 单个任务超时秒数 |
| task_failure_ttl | int | `86400` | 失败任务 Redis 保留秒数 |

### 运行环境识别 (dev / prod)

`environment` 默认 `"prod"`(误配置时保守)。**没有 `debug` 字段** —— 所有调试开关统一判断 `is_dev()`,避免两个维度冲突。业务代码通过三个顶层 API 读当前环境:

```python
from dwyeapi import is_dev, is_prod, get_environment

# FastAPI docs/redoc/openapi 三个端点仅 dev 开启,prod 必须关闭(防路由元信息泄露)
app = FastAPI(
    docs_url="/docs" if is_dev() else None,
    redoc_url="/redoc" if is_dev() else None,
    openapi_url="/openapi.json" if is_dev() else None,
)

# SQL echo、慢路由 profiling 等性能相关调试也走 is_dev()
engine = create_async_engine_factory(settings.database_url, echo=is_dev())
```

**Email Provider 注入**: `providers.email` 内置仅 `resend`;业务自定义发送通道(腾讯云 SES、AWS SES、自建 SMTP 等)需继承 `EmailProviderBase` 实现 `_send`,再调 `register_email_provider("name", factory)` 注册,`.env` 设 `EMAIL__PROVIDER=name` 启用。验证码 + Redis + 品牌化模板由基类全部复用。

---

## database — 异步 SQLAlchemy

```python
from dwyeapi.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory
```

### 模型定义

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    # TimestampMixin 自动添加 created_at, updated_at
```

### 引擎和会话

```python
engine = create_async_engine_factory(settings.database_url, echo=is_dev())
# 参数: database_url, pool_size=5, max_overflow=10, echo=False
# SQLite 自动跳过连接池参数

session_factory = create_session_factory(engine)
# 返回 async_sessionmaker[AsyncSession]，expire_on_commit=False
```

---

## dependencies — FastAPI 依赖注入

```python
from dwyeapi.dependencies import create_get_db
```

### create_get_db(session_factory)

生成 `get_db` FastAPI Depends 函数，自动管理会话生命周期。

```python
get_db = create_get_db(session_factory)

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    ...
```

---

## security — JWT + bcrypt

```python
from dwyeapi.security import hash_password, verify_password, create_token, decode_token
```

所有函数无状态，密钥通过参数传入。

| 函数 | 签名 | 说明 |
|------|------|------|
| hash_password | `(password: str) -> str` | bcrypt 哈希 |
| verify_password | `(plain: str, hashed: str) -> bool` | 验证密码 |
| create_token | `(data: dict, secret: str, expires_minutes: int, algorithm="HS256") -> str` | 创建 JWT，自动添加 exp |
| decode_token | `(token: str, secret: str, algorithm="HS256") -> dict \| None` | 解码 JWT，失败返回 None |

```python
hashed = hash_password("my-password")
is_valid = verify_password("my-password", hashed)

token = create_token({"sub": str(user.id)}, settings.secret_key, settings.access_token_expire_minutes)
payload = decode_token(token, settings.secret_key)  # {"sub": "1", "exp": ...} 或 None
```

---

## exceptions — 异常体系

```python
from dwyeapi.exceptions import (
    AppError, NotFoundError, BusinessError, PermissionDeniedError, AuthenticationError,
    register_exception_handlers,
)
```

### 异常层级

| 异常类 | HTTP 状态码 | code | message |
|--------|-----------|------|---------|
| AppError(message, code) | — | 自定义 | 自定义 |
| NotFoundError(resource) | 404 | `NOT_FOUND` | `{resource}不存在` |
| BusinessError(message, code) | 422 | 自定义 | 自定义 |
| PermissionDeniedError() | 403 | `PERMISSION_DENIED` | `权限不足` |
| AuthenticationError() | 401 | `AUTHENTICATION_FAILED` | `认证失败` |

### 注册到 FastAPI

```python
app = FastAPI()
register_exception_handlers(app)
# 之后在 service 层直接 raise NotFoundError("用户") 即可返回 404
```

响应格式统一为 `{"code": "ERROR_CODE", "message": "描述"}`。

### 使用原则

- **service 层**抛业务异常（NotFoundError, BusinessError 等）
- **router 层**不写 try/except，由 register_exception_handlers 统一处理
- **禁止**在 service 层抛 HTTPException

---

## response — 统一响应

```python
from dwyeapi.response import success, fail, paginated
```

| 函数 | 签名 | 返回结构 |
|------|------|---------|
| success | `(data=None, message="success") -> dict` | `{"code": 200, "message": ..., "data": ..., "timestamp": ...}` |
| fail | `(code=400, message="fail") -> dict` | `{"code": ..., "message": ..., "data": None, "timestamp": ...}` |
| paginated | `(items, total, page, page_size) -> dict` | success 包装 `{"items": [...], "total": N, "page": N, "page_size": N}` |

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, service=Depends(get_user_service)):
    user = await service.get_by_id(user_id)
    return success(data=UserResponse.model_validate(user))

@router.get("/users")
async def list_users(params: PaginationParams = Depends(), service=Depends(get_user_service)):
    items, total = await service.list(params)
    return paginated(items, total, params.page, params.page_size)
```

---

## pagination — 分页工具

```python
from dwyeapi.pagination import PaginationParams, paginate, OffsetLimit
```

### PaginationParams

FastAPI Depends 注入的查询参数模型。

| 字段 | 类型 | 默认 | 约束 |
|------|------|------|------|
| page | int | 1 | >= 1 |
| page_size | int | 20 | 1 ~ 100 |

### paginate(page, page_size) -> OffsetLimit

```python
offset_limit = paginate(params.page, params.page_size)
# OffsetLimit(offset=0, limit=20) — 可直接用于 SQLAlchemy .offset().limit()
stmt = select(User).offset(offset_limit.offset).limit(offset_limit.limit)
```

---

## cache — 异步 Redis

```python
from dwyeapi import cache
```

| 函数 | 签名 | 说明 |
|------|------|------|
| cache.configure | `(redis_url: str) -> None` | 设置 Redis URL（启动时调用一次） |
| cache.get_redis | `async () -> Redis` | 获取/创建共享连接（未 configure 时抛 RuntimeError） |
| cache.close_redis | `async () -> None` | 关闭连接（安全幂等） |

```python
# lifespan 中初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.configure(settings.redis_url)
    yield
    await cache.close_redis()

# 业务中使用
redis = await cache.get_redis()
await redis.set("key", "value", ex=3600)
val = await redis.get("key")
```

---

## dt — 全局时间工具

```python
from dwyeapi import dt
```

业务时间统一 Asia/Shanghai，**禁止在业务代码中直接使用 `datetime.now()`**，统一通过 `dt` 模块访问。

| 函数 | 签名 | 说明 |
|------|------|------|
| dt.now | `() -> datetime` | 当前中国时间（naive，用于数据库存储） |
| dt.now_str | `(fmt="%Y-%m-%d %H:%M:%S") -> str` | 格式化的当前中国时间字符串 |
| dt.today | `() -> date` | 当前中国日期 |
| dt.timestamp | `() -> float` | 当前 Unix 时间戳（秒） |
| dt.utc_now | `() -> datetime` | 当前 UTC 时间（aware，用于 JWT exp 等协议字段） |

```python
dt.now()          # datetime(2026, 4, 8, 14, 30, 0) — naive, Asia/Shanghai
dt.now_str()      # "2026-04-08 14:30:00"
dt.today()        # date(2026, 4, 8)
dt.timestamp()    # 1775625000.0
dt.utc_now()      # datetime(2026, 4, 8, 6, 30, 0, tzinfo=UTC) — aware
```

常量：`dt.TZ`（Asia/Shanghai）、`dt.UTC`。

---

## masking — PII 数据脱敏

```python
from dwyeapi.masking import (
    mask_phone,          # 138****5678
    mask_email,          # z***@gmail.com
    mask_id_card,        # 420***********1234
    mask_bank_card,      # 6222********1234
    mask_name,           # 张*明
    mask_address,        # 浙江省杭州市西湖区****
    mask_ip,             # 192.168.1.*
    mask_license_plate,  # 浙A***8
    mask_text,           # 通用脱敏（自定义首尾保留位数）
)
```

纯函数模块，无外部依赖。所有函数对空字符串、格式不匹配的输入原样返回，不抛异常。

### 在 Response Schema 中使用

```python
class UserResponse(BaseModel):
    phone: str
    email: str

    @field_validator("phone", mode="before")
    @classmethod
    def _mask_phone(cls, v: str) -> str:
        return mask_phone(v) if v else v

    @field_validator("email", mode="before")
    @classmethod
    def _mask_email(cls, v: str) -> str:
        return mask_email(v) if v else v
```

### mask_text — 通用脱敏

```python
mask_text("hello", start=1, end=1, mask_char="*")  # h***o
mask_text("1234567890", start=2, end=3)              # 12*****890
```

---

## 典型项目接入流程

```python
# config.py
from dwyeapi.config import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"

settings = Settings()

# database.py
from dwyeapi.database import Base, create_async_engine_factory, create_session_factory
from dwyeapi.dependencies import create_get_db

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)

# main.py
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi import cache

app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
```

---

## tasks — 异步任务处理 (需 `[tasks]` extra)

```python
from dwyeapi.tasks import setup_tasks, task_router, register, TaskContext
```

基于 ARQ 的全异步耗时任务系统。3 步接入：注册任务 → setup + 挂载路由 → 启动 Worker。

### 快速示例

```python
# 1. 注册任务
@register("process_data")
async def process_data(ctx: TaskContext, params: dict):
    await ctx.log("开始处理")
    await ctx.update_progress(50, "处理中...")
    if await ctx.is_cancelled():
        return
    return {"result": "ok"}  # 框架自动设为 SUCCESS

# 2. FastAPI 接入
await setup_tasks(app, settings, session_factory)
app.include_router(task_router)

# 3. Worker: arq app.worker.WorkerSettings
```

### 公共 API

| 导出项 | 用途 |
|--------|------|
| `setup_tasks(app, settings, session_factory)` | lifespan 中调用, 初始化 |
| `task_router` | 开箱即用 APIRouter (提交/查询/列表/取消) |
| `register(task_type)` | 装饰器, 注册异步任务 |
| `TaskContext` | 任务函数上下文 (db/log/progress/cancel) |
| `TaskStatus` | 枚举: PENDING/RUNNING/SUCCESS/FAILED/CANCELED |
| `create_worker_settings(settings, session_factory)` | 生成 ARQ Worker 配置 |

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tasks` | 提交任务 |
| GET | `/tasks/{task_id}` | 查询状态 |
| GET | `/tasks` | 列表 (分页 + 筛选) |
| POST | `/tasks/{task_id}/cancel` | 取消任务 |

> **完整文档：** [tasks-integration-guide.md](tasks-integration-guide.md) — 包含 TaskContext API、数据模型、Worker 配置、取消机制等详细说明。
