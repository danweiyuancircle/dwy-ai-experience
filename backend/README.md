# danweiyuan-eapi

Lightweight FastAPI infrastructure package for shared use across projects.

## Install

```bash
pip install danweiyuan-eapi
```

## Modules

- `config` — BaseSettings with required fields (database_url, redis_url, secret_key)
- `exceptions` — AppError hierarchy + FastAPI exception handlers
- `database` — Async SQLAlchemy engine/session factory + Base + TimestampMixin
- `dependencies` — `get_db()` FastAPI dependency
- `security` — JWT create/verify + bcrypt hash/verify (stateless)
- `cache` — Async Redis connection manager
- `response` — Unified API response helpers
- `pagination` — PaginationParams + paginate helper
