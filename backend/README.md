# dwyeapi

Lightweight FastAPI infrastructure package for shared use across projects.

## Install

```bash
pip install dwyeapi
```

## Modules

- `config` — BaseSettings with required fields (database_url, redis_url, secret_key) + runtime environment API (`is_dev()` / `is_prod()` / `get_environment()`)
- `exceptions` — AppError hierarchy + FastAPI exception handlers
- `database` — Async SQLAlchemy engine/session factory + Base + TimestampMixin
- `dependencies` — `get_db()` FastAPI dependency
- `security` — JWT create/verify + bcrypt hash/verify (stateless)
- `cache` — Async Redis connection manager
- `response` — Unified API response helpers
- `pagination` — PaginationParams + paginate helper
- `logger` — Facade logger (loguru-backed) with daily + size rotation and stdlib interception; downstream code depends on `dwyeapi.logger.Logger`, not loguru directly
- `providers.email` / `providers.sms` — pluggable 验证码 Provider 工厂 (mock / resend / aliyun)

## Environment (dev / prod)

`BaseSettings` 暴露顶层 `environment` 字段,可选值 `"dev" | "prod"`,**默认 `"prod"`**(保守派,误配置时也按 prod 行为)。

```bash
# .env
ENVIRONMENT=dev          # 开发环境;留空或 prod 即生产
```

业务代码通过 `dwyeapi.is_dev()` / `dwyeapi.is_prod()` / `dwyeapi.get_environment()` 读当前环境,典型用法:

```python
from dwyeapi import is_dev
from fastapi import FastAPI
from app.config import Settings

settings = Settings()  # 实例化会把 environment 同步到 dwyeapi 全局

app = FastAPI(
    title="My API",
    docs_url="/docs" if is_dev() else None,
    redoc_url="/redoc" if is_dev() else None,
    openapi_url="/openapi.json" if is_dev() else None,
)
```

### Mock provider 仅 dev 可用

`providers.email` / `providers.sms` 的 `provider="mock"` 只在 `ENVIRONMENT=dev` 下可用。prod 环境下调用 `make_email_provider()` / `make_sms_provider()` 会抛 `ValueError`,保证正式环境一旦误配置 `EMAIL__PROVIDER=mock` 会启动失败(fail fast),而不会静默吞掉真实验证码。
