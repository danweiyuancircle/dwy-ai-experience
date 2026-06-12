# dwyeapi

## 0.9.2

### Patch Changes

- 增加 GitHub Actions OIDC 发布链路测试版本，支持通过 `dwyeapi@x.y.z` tag 自动发布到 PyPI，并同步创建 GitHub Release。

## 0.9.0

### Minor Changes

- **Email Provider 注入扩展点** —— 新增 `register_email_provider(name, factory)` 公开 API + 模块级注册表。业务项目继承 `EmailProviderBase` 实现 `_send`,再用 `register_email_provider("tencent_ses", build_fn)` 注册即可,`.env` 设 `EMAIL__PROVIDER=tencent_ses` 自动装配。Redis 验证码生成/存取/校验、品牌化 HTML+text 模板由基类全部复用,业务只关心发送通道。
- **`EmailSettings.provider` 字段类型放宽** —— 由 `Literal["mock", "resend", "aliyun"]` 改为 `str`,默认 `"resend"`。Pydantic 静态校验交给 `make_email_provider()` 运行时校验,允许任意自定义 provider 名称。

### Breaking Changes

- **删除 `MockEmailProvider`** —— 开发环境如需 no-op 邮件发送,业务自行注册一个测试 provider。
- **删除 `AliyunEmailProvider` 与 `AliyunEmailConfig`** —— 阿里云邮件接入改为业务自实现 + `register_email_provider` 注入。
- **删除整个 `dwyeapi.providers.sms` 模块** —— 包含 `SmsProvider` Protocol、`SmsProviderBase`、`MockSmsProvider`、`AliyunSmsProvider`、`SmsSettings` 等全部符号。短信验证码能力不再由 eapi 提供,业务项目自行实现。
- **删除 extras**:`email-aliyun` / `sms-aliyun` / `sms`;`email` 聚合 extra 现在仅含 `email-resend`。
- **移除 `EmailSettings.aliyun` 嵌套字段**,以及邮箱工厂中的 `is_prod()` 校验(随 mock 一并去除)。

### 升级指南

依赖 ~0.8 版本的项目升级到 0.9.0 时:

1. `.env` 里 `EMAIL__PROVIDER=mock` / `EMAIL__PROVIDER=aliyun` 改为 `resend`,或注册业务自己的 provider
2. 移除 `EMAIL__ALIYUN__*` / `SMS__*` 相关环境变量
3. 业务代码 `from dwyeapi.providers.sms import ...` 全部失效,需自实现短信发送
4. 自定义邮件 provider 推荐用法见 `dwyeapi.providers.email` 模块 docstring

## 0.8.2

### Patch Changes

- **`TimestampMixin` 字段补 column comment** — `created_at` / `updated_at` 各加 `comment="创建时间"` / `comment="更新时间"`。继承 `TimestampMixin` 的项目在 alembic autogenerate 后,迁移会自动 `op.alter_column(..., comment=...)` 把注释 push 到 PostgreSQL `pg_description`,DBeaver / Navicat / `psql \d+` 看表结构时就能看到字段说明。无运行时行为变化。
- **`tasks.Task` 模型 7 个字段补 column comment** — `id` / `task_type` / `status` / `params` / `result` / `progress` / `logs` 全部加 `comment="..."` + 行尾 `#` 中文注释,与 `dwy-python-orm` 规则中"字段文档化规范"对齐。继承 `dwyeapi.tasks` 的项目下次 alembic autogenerate 会生成 `op.alter_column(..., comment=...)` 把注释 push 到数据库,SQL 工具看 `tasks` 表即可读到字段说明。无运行时行为变化。

## 0.8.0

### Minor Changes

- **Email Provider 品牌化模板** —— `EmailProviderBase` 新增 `_render_code_html()` / `_render_code_text()` 共享渲染方法,`ResendEmailProvider` 替换原本简陋的硬编码 HTML 为专业品牌化模板(深色 hero 渐变页眉 + 居中验证码卡片 + 安全提示 + 客服联系 + 页脚版权)。同时附 text 版本,降低 163/QQ 等国内邮箱反垃圾误判概率,提升 Gmail/Outlook/Apple Mail 兼容性。
  - 模板使用 table 布局 + inline CSS,主流邮件客户端零兼容问题。
  - `brand_name` 等动态文案经 `html.escape()` 转义,即使配置含 `<script>` 也不会破坏 HTML 结构。
  - `Resend.from` 自动拼接为 `"brand_name <from_email>"`,收件人看到的发件人显示名即品牌名。
- **`EmailSettings` 顶层新增 5 个品牌字段** —— 与 provider 解耦的"邮件外观"参数,切换 provider(resend / aliyun)时品牌信息保留。
  - `brand_name`:品牌名,展示在页眉与页脚版权(也作发件人显示名)。
  - `brand_tagline`:品牌副标语(英文/口号),展示在页眉右上。
  - `brand_url`:品牌官网,展示在页脚链接。
  - `brand_slogan`:页脚版权下方一行说明文案。
  - `support_email`:客服邮箱,展示在邮件正文底部。
  - 全部默认空串,**完全向后兼容**。已有项目升级到 0.8.0 不改任何配置即可继续运行,只是邮件依然走通用模板。
- **`AliyunEmailProvider` 占位实现同步参数签名** —— 构造器接收同一组品牌字段并透传给基类,首次接入项目时直接 `self._render_code_html(code)` 复用模板,无需重复造轮子。

### `.env` 升级示例

```bash
EMAIL__PROVIDER=resend
EMAIL__BRAND_NAME=宽舟科技
EMAIL__BRAND_TAGLINE=QuantZone
EMAIL__BRAND_URL=https://quantzone.tech
EMAIL__BRAND_SLOGAN=专业量化数据服务平台
EMAIL__SUPPORT_EMAIL=support@quantzone.tech
EMAIL__RESEND__API_KEY=re_xxx
EMAIL__RESEND__FROM_EMAIL=noreply@quantzone.tech
EMAIL__RESEND__SUBJECT=【宽舟科技】您的验证码
```

## 0.7.1

### Patch Changes

- **`BaseSettings.log_dir` 默认值由 `None` 改为 `"."`** — 文件日志默认启用,写到进程当前目录。此前 `None` 表示关闭文件输出,业务项目若未显式配置 `LOG_DIR`,全部日志只进控制台,排障时难以回溯。显式传 `None` 仍可关闭文件输出(只保留控制台)。
- **所有 `BaseSettings` 字段改用 `Field(..., description="中文说明")` 标注含义** — 16 个配置项(database_url / redis_url / secret_key / jwt_algorithm / access_token_expire_minutes / environment / allowed_origins / task_*×3 / log_*×8)全部带中文 description,进入 Pydantic schema / OpenAPI / IDE hover 提示。同时按"基础 / 异步任务 / 日志"三组分节注释。
- **修正 `tests/providers/test_sms_base.py` 的基类测试** — 原测试用 `MockSmsProvider` 验证基类严格一次性校验,但 Mock 有意重写 `verify_code` 为宽松校验(任意 4-8 位数字通过,方便 curl 调试),导致基类严格语义未被覆盖。新增本地 `_StrictSmsProvider` 子类(仅实现 `_send`,不重写 `verify_code`)给两个测试使用,真正覆盖基类逻辑。

## 0.7.0

### Minor Changes

- **新增 `dwyeapi.health` 模块** — 提供 `create_health_router(service_name, version, path="/health", include_in_schema=True)` 工厂函数,返回只有一个 GET 端点的 `APIRouter`,响应走 `ApiResponse[dict]` 信封,载荷为 `{"service", "version", "status": "alive"}`。
  - **只探活,不探依赖**:端点**不**连接 PostgreSQL / Redis / 第三方 API。健康端点通常对公网开放,若内置 readiness check,攻击者可以用低频高并发请求把压力放大到 DB/缓存层,变成 DoS 放大器。需要 readiness 语义的业务应在业务项目内自行实现,并挂鉴权或限制在内网。
  - 顶层导出:`from dwyeapi import health` 或 `from dwyeapi.health import create_health_router`。
- **扩展 `register_exception_handlers`** — 新增 3 个 handler,让所有非业务异常也走统一 `ApiResponse` 信封,避免 FastAPI 默认的 `{"detail": ...}` 格式绕过信封。
  - `RequestValidationError` → 422 + `code="VALIDATION_ERROR"`。行为变化:FastAPI 默认 `{"detail":[{"loc":[...], "msg":"..."}]}` → 信封 `{code:"VALIDATION_ERROR", message:"请求参数校验失败", data:{"errors":[{"field": "body.qty", "message": "Input should be a valid integer..."}]}, timestamp}`。field 保留完整路径(含 `body` / `query` 段)便于前端精确定位来源。**注意**:`field` 是 pydantic `loc` tuple 的 `.` 拼接,数组索引会以数字段出现(如 `body.items.0.name`),少数 pydantic 内部段(如 discriminator union 校验失败时的 `tagged-union-tag`)对前端不直接可读,建议前端把 `field` **仅用于错误提示与日志展示**,不要按 dot path 精确回填表单字段。
  - `HTTPException` → 透传原始 `status_code` + `headers` + 信封。`code=f"HTTP_{status_code}"`,`message=str(detail)`。**关键**:`exc.headers` 原样透传,保留 OAuth2 `WWW-Authenticate: Bearer` 等协商头,否则标准客户端无法按规范重试。
  - 未捕获 `Exception` fallback → 500 + `code="INTERNAL_ERROR"` + 脱敏。
    - `is_dev()` 为 True:`message=f"服务器内部错误: {exc!s}"`,方便定位。
    - `is_prod()` 为 True:`message="服务器内部错误"`,防止 KeyError 字段名、文件路径、SQL 片段等内部信息泄露。
    - 两种环境都通过 `logger.exception("未捕获异常")` 把完整 traceback 写到日志,确保排障证据不丢失。
### 示例

```python
# main.py
from fastapi import FastAPI
from dwyeapi import __version__ as eapi_version
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.health import create_health_router

app = FastAPI()
register_exception_handlers(app)  # 自动包含 4 个 AppError + 3 个框架异常 handler
app.include_router(
    create_health_router(service_name="quant-cloud", version="1.0.0"),
)
```

前端/客户端:

```ts
// 422 VALIDATION_ERROR 响应
interface ValidationErrorData {
  errors: Array<{ field: string; message: string }>;
}

// 401 OAuth2 challenge — 响应头保留 WWW-Authenticate: Bearer
if (res.status === 401 && res.headers.get("WWW-Authenticate")) { ... }
```

## 0.6.0

### Breaking Changes

- **响应信封重构为泛型 Pydantic 模型** — `dwyeapi.response` 由 dict 构造函数改为 `ApiResponse[T]` + `PageData[T]` 泛型类,路由 `response_model` 可声明为 `ApiResponse[UserResponse]` / `ApiResponse[PageData[UserResponse]]`,OpenAPI schema 100% 准确,前端可用 openapi-typescript 自动生成 TS 类型。
  - **移除**旧 API:`success(data, message)` / `fail(code, message)` / `paginated(items, total, page, page_size)` 三个函数全部删除,不提供兼容别名。
  - **新增** `ApiResponse[T]`:字段 `code: str = "SUCCESS"` / `message: str = "success"` / `data: T | None = None` / `timestamp: int`(自动取当前秒)。
  - **新增** `ApiResponse.ok(data, message="success") -> ApiResponse[T]` classmethod:构造单体成功响应。
  - **新增** `ApiResponse.page(items, total, page, page_size, message="success") -> ApiResponse[PageData[T]]` classmethod:构造分页成功响应。
  - **新增** `PageData[T]`:字段 `items: list[T]` / `total: int` / `page: int` / `page_size: int`,配合 `ApiResponse` 使用。
  - **两者均从顶层 `dwyeapi` 直接导出**:`from dwyeapi import ApiResponse, PageData`。
- **`code` 字段类型统一为 `str`** — 成功态固定 `"SUCCESS"`,错误态由业务异常 `AppError.code` 决定(如 `"NOT_FOUND"` / `"INSUFFICIENT_BALANCE"`)。旧版成功态 `code: 200`(int)、失败态 `code: str` 的混用被消除,前端拦截器判断逻辑统一。
- **异常 handler 响应格式对齐 ApiResponse 信封** — `register_exception_handlers` 注册的 4 个 handler 不再返回 `{code, message}` 精简字典,改为返回完整 `{code, message, data: null, timestamp}` 信封。HTTP 状态码保持不变(404/422/403/401)。业务错误码(`NOT_FOUND` / `INSUFFICIENT_BALANCE` / `PERMISSION_DENIED` / `AUTHENTICATION_FAILED`)通过 `code` 字段返回,前端可配合状态码与 `code` 做双重判断。

### 迁移指南

```python
# 旧
from dwyeapi.response import success, paginated
return success(data=user.model_dump())
return paginated(items=items, total=total, page=1, page_size=20)

# 新
from dwyeapi import ApiResponse, PageData

@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(...) -> ApiResponse[UserResponse]:
    return ApiResponse.ok(UserResponse(...))

@router.get("/", response_model=ApiResponse[PageData[UserBrief]])
async def list_users(...) -> ApiResponse[PageData[UserBrief]]:
    items, total = await service.list(...)
    return ApiResponse.page(items, total, page, page_size)
```

前端拦截器:

```ts
interface ApiResponse<T> {
  code: string;         // "SUCCESS" | "NOT_FOUND" | ...
  message: string;
  data: T | null;
  timestamp: number;
}

// 成功判断
if (res.data.code === "SUCCESS") { ... }
```

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
