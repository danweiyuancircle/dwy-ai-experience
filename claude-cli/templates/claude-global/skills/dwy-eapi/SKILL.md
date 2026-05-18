---
name: dwy-eapi
description: "dwyeapi FastAPI 后端基础设施使用指南。涉及以下任何主题，**必须**使用此 skill（即使用户没有明确说 'dwyeapi' / 'eapi'）：FastAPI 项目搭建 / Pydantic Settings 配置 / 异步 SQLAlchemy / Redis 缓存 / JWT 认证 / bcrypt 密码哈希 / 异常体系（AppError / NotFoundError / BusinessError）/ 统一响应信封（ApiResponse / PageData）/ 分页 / 日志（loguru）/ 健康检查 / PII 脱敏 / 时区敏感的时间处理 / 异步任务（ARQ）/ 邮件验证码发送。本 skill 是 @dwydev/eapi 的唯一权威导航来源。"
category: 基础库
eapi_baseline_version: "0.9.0"
---

# dwyeapi 后端基础设施使用指南

Python 3.11+ FastAPI 基础设施包，全异步。单文件模块设计（每个能力一个 .py），便于直接读源码。

本 skill 索引基于 dwyeapi **0.9.0**。消费方版本可能不同 — 见 [版本兼容规则](#版本兼容规则)。

## 模块清单（13 个）

| 模块 | 用途 |
|------|------|
| `config` | Pydantic BaseSettings + 运行环境识别 (is_dev / is_prod / get_environment) |
| `exceptions` | AppError 异常体系 + FastAPI 全局 handler 注册 |
| `database` | 异步 SQLAlchemy engine/session 工厂 + Base + TimestampMixin |
| `dependencies` | FastAPI 依赖注入工厂（如 get_db） |
| `security` | JWT 令牌 + bcrypt 密码哈希（无状态） |
| `cache` | 异步 Redis 连接管理（懒单例） |
| `response` | 统一 API 响应信封 `ApiResponse[T]` + `PageData[T]` |
| `pagination` | 分页参数 PaginationParams + offset/limit 计算 |
| `dt` | 中国时区敏感的全局时间工具（替代 datetime.now） |
| `logger` | loguru 全局日志（按天 + 按大小轮转、stdlib 拦截） |
| `masking` | PII 数据脱敏（手机/邮箱/身份证/银行卡/姓名/地址/IP/车牌） |
| `health` | 健康检查路由工厂（只探活、不探依赖） |
| `tasks` | 异步任务系统（基于 ARQ，需 `pip install dwyeapi[tasks]`） |
| `providers.email` | 邮件验证码发送（可插拔，默认 Resend，可继承注入腾讯 SES / SMTP 等） |

---

## 查 API 标准动作（核心：每次写 dwyeapi 代码前都做）

dwyeapi 的源码 docstring 写得非常详尽（含设计意图、边界行为、Args/Returns/Raises、典型陷阱）。**本文档不再镜像签名表格** —— 因为表格信息密度低于源码 docstring，且会随版本漂移。需要某个 API 的精确签名/语义时，按下面顺序拿：

### 第一步：定位 dwyeapi 真实版本和安装路径

```bash
# 拿版本
pip show dwyeapi | grep -i version
#  或：python -c "import dwyeapi; print(dwyeapi.__version__)"

# 拿包安装目录
python -c "import dwyeapi; print(dwyeapi.__file__)"
# 输出形如 /path/to/.venv/lib/python3.12/site-packages/dwyeapi/__init__.py
# dirname 后的目录就是 dwyeapi 包根，模块都在里面
```

### 第二步：读模块源码（按存在性回退）

```
a. 优先：<site-packages>/dwyeapi/{module}.py
   —— 下游消费方默认场景。每个模块单文件，含模块级 docstring + 所有公开函数/类的 Args/Returns/Raises

b. 次选：<dwy-shared-root>/backend/src/dwyeapi/{module}.py
   —— 仅当在 dwy-shared monorepo 内或并列 clone 时可用，内容相同

c. 都拿不到 → 退到本文档下方的 [模块清单](#模块清单13-个)（粗略，仅做导航）
```

### 第三步：tasks 模块查详细文档

tasks 模块功能丰富（注册 / 提交 / 查询 / 取消 / 进度），单独维护一份完整集成指南：

```
references/tasks-integration-guide.md
```

只在用到 tasks 时读，平时不必加载。

### 第四步：冲突时永远信源码

本 SKILL.md 是导航 + 心智模型，**不是 API 真相**。当文档描述与 site-packages 中的 `.py` 不一致：无条件以源码为准。

---

## 版本兼容规则

- 本 skill `eapi_baseline_version: 0.9.0`，模块清单、踩坑提示都基于这个版本
- 消费方装的是不同版本（更新或更旧）时，**必须**按"查 API 标准动作"流程读 .py，不要默认本文档准确
- dwyeapi < 0.9.0 可能没有 dt / tasks / providers 模块：先 `ls <site-packages>/dwyeapi/` 确认存在再用
- 主版本号变更（0.x → 1.x）时，本文档的索引可能完全失效：先 `ls <site-packages>/dwyeapi/` 重建认知

---

## 重要约束与已知陷阱

源码读得出来但容易忽略的"踩坑经验"，写后端代码时遵守：

### 业务层架构（service / router 分层）

- **service 层**抛业务异常（`NotFoundError("用户")` / `BusinessError("余额不足", code="INSUFFICIENT_BALANCE")` 等），不感知 HTTP 概念
- **router 层**不写 try/except，由 `register_exception_handlers(app)` 统一转成 `ApiResponse` 信封 JSON
- **禁止**在 service 层抛 `HTTPException` —— 会绕过统一 handler，破坏响应结构一致性

### 时间处理（避免时区 bug）

- 业务时间统一中国时区，**禁止 `datetime.now()`**，统一走 `dwyeapi.dt`
- `dt.now()` 返回 naive datetime（Asia/Shanghai，用于数据库存储）
- `dt.utc_now()` 返回 aware UTC datetime（用于 JWT exp 等协议字段）
- 这两个不能混用：数据库列存 naive 中国时间、JWT exp 存 UTC aware

### 配置

- **没有 `debug` 字段**，所有调试开关统一用 `is_dev()`：避免两个维度（debug + environment）冲突
- `environment` 默认 `"prod"`（误配置时保守）：生产环境必须显式关闭 docs/redoc/openapi 三个端点（`docs_url="/docs" if is_dev() else None`），否则路由元信息会泄露给攻击者
- `BaseSettings` 必填三个字段：`database_url` / `redis_url` / `secret_key`（继承时不能给默认值）

### Redis 连接

- `cache.configure(redis_url)` 启动时调用一次（lifespan）；`cache.get_redis()` 首次调用懒建立连接
- `close_redis()` 可重复调用（安全幂等），lifespan 关闭阶段调用
- 未 configure 直接 `get_redis()` 会抛 `RuntimeError`

### tasks 模块

- 需要 `pip install dwyeapi[tasks]` 单独装 extra（避免不用任务的项目背 ARQ 依赖）
- 任务函数签名固定 `async def task(ctx: TaskContext, params: dict)`，第一个参数 ctx 由框架注入
- 取消机制是协作式：任务函数内必须主动 `await ctx.is_cancelled()` 检查，否则取消信号无效
- 完整细节读 `references/tasks-integration-guide.md`

### 邮件 Provider

- 内置仅 `resend`。业务用其他通道（腾讯 SES / SMTP / 自建）：继承 `EmailProviderBase` 实现 `_send` → `register_email_provider("name", factory)` → `.env` 设 `EMAIL__PROVIDER=name`
- 验证码生成 + Redis 存储 + 品牌化模板 由基类全部复用，子类只管"发出去"

### 日志

- `logger.configure()` 启动时调用一次；`logger.close()` 在 lifespan 结束时调用
- `intercept_stdlib=True`（默认）会把 stdlib logging（uvicorn / SQLAlchemy 等）也接管到统一 sink
- 多进程部署时必须 `enqueue=True`（默认）——避免日志文件竞争写

### 健康检查

- `create_health_router()` **只**探活、**不**触达 PostgreSQL / Redis 等依赖
- 理由：健康端点常对公网开放，内置 dependency check 会被攻击者用来 DoS 放大数据库/缓存
- 需要 readiness 的业务自行实现并限制内网访问

---

## 典型项目接入流程

```python
# config.py
from dwyeapi.config import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    service_name: str = "my-api"

settings = Settings()  # 从 .env / 环境变量读 database_url、redis_url、secret_key

# database.py
from dwyeapi.database import create_async_engine_factory, create_session_factory
from dwyeapi.dependencies import create_get_db
from dwyeapi import is_dev

engine = create_async_engine_factory(settings.database_url, echo=is_dev())
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)

# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dwyeapi import cache, logger, is_dev
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.health import create_health_router

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

---

## 响应契约速查（前后端对齐用）

所有接口返回统一信封：

```json
{
  "code": "SUCCESS",
  "message": "success",
  "data": { ... },
  "timestamp": 1775625000
}
```

- 成功：`code = "SUCCESS"`，`data` 是业务载荷（单体或 `PageData[T]`）
- 失败：`code` 是业务错误码（如 `NOT_FOUND` / `BUSINESS_ERROR` / `VALIDATION_ERROR` 等），HTTP 状态保持语义（404 就是 404）
- 校验错误 `VALIDATION_ERROR`：`data.errors: [{field, message}]`，field 含 `body.` / `query.` / `path.` 前缀

构造响应：用 `ApiResponse.ok(data)` 或 `ApiResponse.page(items, total, page, page_size)`，不直接实例化 `ApiResponse`。

错误响应**不要业务代码构造** —— 直接 `raise NotFoundError("用户")`，handler 自动转。

---

## 防腐层硬性约束（写代码前必读）

dwyeapi 把基础设施细节封装在自有 API 后面。业务代码**禁止**直接调下面这些底层 API，违反会导致升级困难、行为不一致：

| 禁止 | 改用 |
|------|------|
| `datetime.now()` / `datetime.utcnow()` | `dt.now()` / `dt.utc_now()` |
| `import logging; logging.getLogger()` | `from dwyeapi import logger; logger.get_logger()` |
| 手写 `from redis.asyncio import Redis` 全局变量 | `cache.configure()` + `cache.get_redis()` |
| 手写 JWT encode/decode（含 `import jwt`） | `security.create_token()` / `security.decode_token()` |
| 直接 `raise HTTPException(404, ...)` | `raise NotFoundError("资源名")` |
| 自己写 `{"code": ..., "data": ...}` dict 当响应 | `ApiResponse.ok(data)` / `ApiResponse.page(...)` |
| 自己写 `?page=&page_size=` Query 参数 | `params: PaginationParams = Depends()` |
