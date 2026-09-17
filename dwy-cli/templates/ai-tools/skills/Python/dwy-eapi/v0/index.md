# dwyeapi 0.x

精确签名以安装版本的源码为准（见上级 SKILL.md：先 clone tag，拿不到再读 venv）。本页是 0.x 导航与陷阱。

跨大版本不变的分层 / 时区 / 信封 / 防腐层在 `shared/`。

## 模块清单（当前 0.9 线）

| 模块 | 用途 | 下限 |
|------|------|------|
| `config` | BaseSettings + `is_dev` / `is_prod` / `get_environment` | |
| `exceptions` | AppError + FastAPI handler | |
| `database` | 异步 engine/session + Base + TimestampMixin | |
| `dependencies` | `get_db` 工厂 | |
| `security` | JWT + bcrypt | |
| `cache` | 异步 Redis | |
| `response` | `ApiResponse[T]` + `PageData[T]` | ≥0.6.0 |
| `pagination` | PaginationParams + paginate | |
| `dt` | 中国时区时间工具 | ≥0.7 左右；`timedelta`/`after` ≥0.9.4 |
| `logger` | loguru | |
| `masking` | PII 脱敏 | |
| `email` | Gmail 规范化 + 常见域名白名单 | 规范化 ≥0.9.6；白名单 / 发码校验 ≥0.10.0 |
| `health` | 只探活健康检查 | ≥0.7.0 |
| `tasks` | ARQ 异步任务，需 `[tasks]` | ≥0.7 后 |
| `providers.email` | 邮件验证码，内置 resend | 工厂注册表 ≥0.9.0 |

`<0.9.0` 可能没有 dt / tasks / providers。先 `ls` 安装目录或 clone 该 tag 再调用。

## 接入骨架

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dwyeapi import cache, logger, is_dev
from dwyeapi.config import BaseSettings
from dwyeapi.database import create_async_engine_factory, create_session_factory
from dwyeapi.dependencies import create_get_db
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.health import create_health_router

class Settings(BaseSettings):
    app_name: str = "My API"
    service_name: str = "my-api"

settings = Settings()
engine = create_async_engine_factory(settings.database_url, echo=is_dev())
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.configure(level="INFO", log_dir="./logs", filename="app")
    cache.configure(settings.redis_url)
    yield
    await cache.close_redis()
    logger.close()

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if is_dev() else None,
    redoc_url="/redoc" if is_dev() else None,
    openapi_url="/openapi.json" if is_dev() else None,
)
register_exception_handlers(app)
app.include_router(create_health_router(service_name=settings.service_name, version="1.0.0"))
```

## 0.x 陷阱

### 配置

- **没有 `debug` 字段**，调试开关用 `is_dev()`
- `environment` 默认 `"prod"`。非 dev 必须关掉 docs/redoc/openapi
- `BaseSettings` 必填：`database_url` / `redis_url` / `secret_key`（子类不能给默认值）

### Redis

- `cache.configure(redis_url)` 启动时一次；`get_redis()` 懒连接
- `close_redis()` 可重复调用
- 未 configure 直接 `get_redis()` → `RuntimeError`

### tasks

- `pip install dwyeapi[tasks]`
- 签名 `async def task(ctx: TaskContext, params: dict)`
- 取消是协作式：必须 `await ctx.is_cancelled()`
- 细节：`references/tasks-integration-guide.md`

### 日志

- `logger.configure()` 启动一次；`logger.close()` 在 lifespan 结束
- `intercept_stdlib=True`（默认）接管 uvicorn / SQLAlchemy
- 多进程必须 `enqueue=True`（默认）

### 健康检查

- `create_health_router()` **只**探活，**不**碰 PostgreSQL / Redis
- readiness 业务自建并限制内网

### 邮件 / Gmail

- Provider：`v0/providers-email.md`
- 规范化 / 常见域名白名单：`v0/email-canonical.md`（规范化 ≥0.9.6；白名单 / 发码校验 ≥0.10.0）
