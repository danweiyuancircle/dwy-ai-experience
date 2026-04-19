# dwyeapi

## 0.5.0

### Minor Changes

- **新增 providers 体系** — 业务相关但复用性强的外部服务抽象(邮件/短信),通过 Protocol + 配置驱动切换实现。第三方 SDK 依赖一律走 optional-dependencies,业务项目按需安装。
- **新增 providers/email 子包**
  - `EmailProvider` Protocol + `EmailProviderBase` 抽象基类(封装 Redis 验证码存取 + 一次性校验逻辑)
  - `MockEmailProvider`(开发环境,零额外依赖,日志打印验证码)
  - `ResendEmailProvider`(基于 resend-python SDK 的 async API) — `pip install dwyeapi[email-resend]`
  - `AliyunEmailProvider`(占位,`_send` 待首个接入项目补全) — `pip install dwyeapi[email-aliyun]`
  - `EmailSettings` 嵌套配置类,业务项目一行 `email: EmailSettings = EmailSettings()` 即可,`.env` 用 `EMAIL__PROVIDER` / `EMAIL__RESEND__API_KEY` 双下划线嵌套
  - `make_email_provider(settings.email)` 工厂函数,按 `settings.provider` 分发
- **新增 providers/sms 子包**
  - `SmsProvider` Protocol + `SmsProviderBase` 抽象基类(对称 Email)
  - `MockSmsProvider`(开发环境)
  - `AliyunSmsProvider`(占位) — `pip install dwyeapi[sms-aliyun]`
  - `SmsSettings` 嵌套配置 + `make_sms_provider` 工厂
- **新增 optional-dependencies**
  - 细粒度:`email-resend` / `email-aliyun` / `sms-aliyun`
  - 聚合:`email`(拉 email 所有实现) / `sms`(拉 sms 所有实现)
  - dev extras 不预置任何 provider SDK,跑 provider 测试需显式 `--extra email --extra sms`

### 约定

- Provider Redis key 前缀统一:`dwyeapi:email:code:{target}` / `dwyeapi:sms:code:{target}`,TTL 默认 300s
- Provider 依赖 `dwyeapi.cache.configure(redis_url)` 先就位,业务 `main.py` lifespan 必须先调 cache.configure 再 make_*_provider
- 未装对应 extra 时,provider `__init__` 抛友好 `ImportError` 并提示 `pip install dwyeapi[xxx]`

## 0.4.0

### Breaking Changes

- **包名重命名** — PyPI 包名 `danweiyuan-eapi` → `dwyeapi`,Python import 路径 `danweiyuan_eapi` → `dwyeapi`。老包 `danweiyuan-eapi` 停止维护,旧版本(≤0.3.0)继续保留在 PyPI 作为历史版本。
  - 迁移方式:业务项目 `pip uninstall danweiyuan-eapi && pip install dwyeapi`,把所有 `from danweiyuan_eapi ...` 替换为 `from dwyeapi ...`。
  - 不提供兼容别名。

## 0.3.0

### Minor Changes

- **新增 logger 模块** — 基于 Loguru 的全局日志,`configure / get_logger / close` 生命周期
  - 彩色控制台输出 + 按日期分文件(`app_YYYY-MM-DD.log`)
  - 单文件大小超限自动切分(默认 100MB,可配置)、旧日志自动清理(默认 30 天)
  - 可选 JSON 序列化、异步非阻塞写入(`enqueue=True`)
  - 可选拦截标准 `logging`,统一 uvicorn/SQLAlchemy 等第三方库日志格式
- `BaseSettings` 新增 `log_level` / `log_dir` / `log_filename` / `log_max_bytes` / `log_retention` / `log_console` / `log_serialize` / `log_intercept_stdlib` 配置字段
- `tasks/worker.py` 迁移到新 logger(原用原生 logging)

## 0.2.0

### Minor Changes

- **新增 tasks 模块** — 基于 ARQ 的全异步耗时任务处理系统，通过 `pip install dwyeapi[tasks]` 按需安装
  - `Task` ORM 模型 — 任务持久化（状态、进度、日志、结果）
  - `@register` 装饰器 — 声明式任务注册
  - `TaskContext` — 丰富的执行上下文（db/log/progress/cancel），框架自动管理生命周期
  - `task_router` — 开箱即用的 API 路由（提交/查询/列表/取消）
  - `setup_tasks()` — 一站式初始化
  - `create_worker_settings()` — 从 BaseSettings 生成 ARQ Worker 配置
  - 协作式任务取消机制（Redis 标记 + `ctx.is_cancelled()`）
- `BaseSettings` 新增 `task_max_jobs` / `task_job_timeout` / `task_failure_ttl` 配置字段

## 0.1.0

首次发布。从 `danweiyuan-base` 重命名而来，统一 "e = easy" 命名体系。

FastAPI 异步基础设施包，Python 3.11+，8 个模块：

- **config** — `BaseSettings`（database_url、redis_url、secret_key）
- **database** — AsyncEngine 工厂、`DeclarativeBase`、`TimestampMixin`（created_at/updated_at）
- **security** — JWT `create_token`/`decode_token`、bcrypt `hash_password`/`verify_password`
- **exceptions** — `AppError` 层级（NotFoundError、BusinessError、PermissionDeniedError、AuthenticationError）+ FastAPI handler 注册
- **response** — `success()`、`fail()`、`paginated()` → `{ code, message, data, timestamp }`
- **pagination** — `PaginationParams`、`paginate()`、`OffsetLimit`
- **cache** — 异步 Redis 管理：`configure()`、`get_redis()`、`close_redis()`
- **dependencies** — FastAPI 依赖注入工厂
