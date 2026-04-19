---
description: Python + FastAPI 基础风格(命名/类型/异步/配置/日志/错误处理等)
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python + FastAPI 基础风格

## 一、项目结构

### 强制规则
- 使用 `pyproject.toml` 作为项目元数据和依赖管理的唯一入口（不再使用 `setup.py` / `setup.cfg`）
- 推荐使用 `uv` 管理依赖，次选 `pip` + `requirements.txt`
- 必须有 `.gitignore`（至少包含 `__pycache__/`、`*.pyc`、`.env`、`dist/`、`*.egg-info/`）
- 必须有 `.python-version` 文件声明 Python 版本

### 标准目录结构
```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI 应用入口
│       ├── config.py            # Settings 配置
│       ├── dependencies.py      # 全局依赖（数据库会话、认证等）
│       ├── exceptions.py        # 自定义异常 + 异常处理器
│       ├── models/              # SQLAlchemy / ORM 模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── schemas/             # Pydantic 请求/响应 schema
│       │   ├── __init__.py
│       │   └── user.py
│       ├── routers/             # 路由模块（按业务域拆分）
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/            # 业务逻辑层
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/               # 工具函数
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── alembic/                     # 数据库迁移
│   ├── env.py
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .python-version
├── .env.example
└── .gitignore
```

- 小型脚本/单文件项目可以不使用 `src/` 布局
- 测试文件统一放在 `tests/` 目录，文件名以 `test_` 开头

### 分层原则

| 层 | 职责 | 禁止 |
|---|---|---|
| `routers/` | 接收请求、参数校验、调用 service、返回响应 | 不写业务逻辑、不直接操作数据库 |
| `services/` | 业务逻辑、事务编排 | 不感知 HTTP 概念（Request/Response/状态码） |
| `models/` | ORM 模型定义 | 不包含业务逻辑 |
| `schemas/` | Pydantic 请求/响应模型 | 不依赖 ORM 模型 |
| `dependencies.py` | FastAPI 依赖注入（DB session、当前用户等） | 不写业务逻辑 |

## 二、Python 版本与兼容性

### 强制规则
- 新项目最低支持 Python 3.10+
- 使用现代语法特性：

| 旧写法 | 新写法（强制） |
|---|---|
| `typing.List[int]` | `list[int]` |
| `typing.Dict[str, int]` | `dict[str, int]` |
| `typing.Optional[str]` | `str \| None` |
| `typing.Union[str, int]` | `str \| int` |
| `typing.Tuple[int, ...]` | `tuple[int, ...]` |
| `from __future__ import annotations` | 不需要（3.10+ 原生支持） |

## 三、代码风格

### 格式化与 Lint
- 使用 `ruff` 作为唯一的 linter + formatter（替代 flake8 / black / isort）
- `pyproject.toml` 中的最小 ruff 配置：

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "RUF",  # ruff-specific
]

[tool.ruff.lint.isort]
known-first-party = ["app"]
```

### 命名规范

| 类型 | 风格 | 示例 |
|---|---|---|
| 模块/包 | `snake_case` | `user_service.py` |
| 函数/方法 | `snake_case` | `get_user_by_id()` |
| 变量 | `snake_case` | `user_count` |
| 类 | `PascalCase` | `UserService` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 私有属性/方法 | `_leading_underscore` | `_parse_token()` |
| 类型变量 | `PascalCase` | `T = TypeVar("T")` |
| 协议/抽象基类 | `PascalCase` + 语义后缀 | `Serializable`、`BaseRepository` |
| 路由函数 | `snake_case` 动词开头 | `create_user()`、`list_orders()` |
| Pydantic Schema | `PascalCase` + 用途后缀 | `UserCreate`、`UserResponse`、`UserUpdate` |

### 禁止魔法字符串

同一个字符串字面量在文件内出现 2 次及以上时，**必须**提取为常量。

```python
# ❌ 魔法字符串散落多处
redis.set("user:token:123", token)
cached = redis.get("user:token:123")

# ✅ 提取为常量
USER_TOKEN_KEY = "user:token:{user_id}"
redis.set(USER_TOKEN_KEY.format(user_id=123), token)
cached = redis.get(USER_TOKEN_KEY.format(user_id=123))

# ❌ cache key、队列名、header 名等重复字面量
request.headers.get("X-Request-Id")
response.headers["X-Request-Id"] = rid

# ✅ 跨模块共享的 key 放到常量模块
# constants.py
HEADER_REQUEST_ID = "X-Request-Id"
CACHE_PREFIX_USER = "user:"
TASK_QUEUE_DEFAULT = "default"
```

**判断标准：** 同一字符串在同一文件出现 ≥ 2 次 → 提取为常量。跨模块使用的 key → 提取到 `constants.py` 共享。

### 禁止的写法

```python
# ❌ 单字母变量（循环索引除外）
d = get_data()

# ✅ 有意义的名称
user_data = get_data()

# ❌ 匈牙利命名法
str_name = "Alice"
lst_users = []

# ✅ 直接命名
name = "Alice"
users = []

# ❌ 布尔变量不带 is/has/can/should 前缀
active = True

# ✅ 布尔变量语义明确
is_active = True
has_permission = False
```

## 四、类型标注

### 强制规则
- 所有公开函数/方法**必须**有参数和返回值类型标注
- 私有函数**推荐**有类型标注
- 类属性**必须**有类型标注

```python
# ❌ 缺少类型标注
def get_user(user_id):
    ...

# ✅ 完整标注
def get_user(user_id: int) -> User | None:
    ...

# ✅ 复杂类型使用 TypeAlias
type UserMap = dict[str, list[User]]

# ✅ 数据类必须标注
@dataclass
class UserProfile:
    name: str
    age: int
    email: str | None = None
```

### 禁止 `Any`
- 不得使用 `Any` 作为"懒标注"，除非与外部动态库交互且无法确定类型
- 使用 `Any` 时必须附注释说明原因

## 十、异步编程

### 强制规则
- FastAPI 路由函数统一使用 `async def`
- 异步函数内**禁止**调用同步阻塞操作（IO、网络、sleep）
- 使用 `asyncio.to_thread()` 包装不可避免的同步调用

```python
# ❌ 异步函数中调用同步阻塞
async def get_data():
    result = requests.get(url)          # 阻塞事件循环
    data = open("file.txt").read()      # 阻塞事件循环

# ✅ 使用异步库
async def get_data():
    async with httpx.AsyncClient() as client:
        result = await client.get(url)
    data = await asyncio.to_thread(Path("file.txt").read_text)
```

- HTTP 客户端使用 `httpx`，**禁止** `requests`
- 数据库使用异步驱动（`asyncpg`、`aiomysql`）

## 十一、中间件与生命周期

### 强制规则

```python
# main.py
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # 启动时执行
    logger.info("应用启动")
    yield
    # 关闭时执行
    await engine.dispose()
    logger.info("应用关闭")

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
)
```

- 使用 `lifespan` 管理应用生命周期，**禁止** `@app.on_event("startup")`（已废弃）
- CORS 中间件必须明确指定允许的域名，**禁止**生产环境使用 `allow_origins=["*"]`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 从环境变量读取
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

## 十二、配置管理

### 强制规则
- 使用 Pydantic Settings 管理配置
- **必须使用嵌套模型分组**，禁止所有字段平铺在一个类中

```python
# config.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# 按领域拆分为独立的配置类（普通 BaseModel，不是 BaseSettings）
class OssConfig(BaseModel):
    endpoint: str = ""
    access_key: str = ""
    secret_key: str = ""
    bucket: str = ""

class AliyunSmsConfig(BaseModel):
    access_key_id: str = ""
    access_key_secret: str = ""
    sign_name: str = ""
    template_code: str = ""

# 主 Settings 类组合嵌套模型
class Settings(BaseSettings):
    # eapi 内置字段（继承 BaseSettings 时自动包含）
    # database_url, redis_url, secret_key, ...

    # 项目专属 — 嵌套分组
    app_name: str = "My App"
    oss: OssConfig = OssConfig()
    aliyun_sms: AliyunSmsConfig = AliyunSmsConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # 关键：启用嵌套分隔符
    )

settings = Settings()
```

**`.env` 文件中用 `__` 分隔层级：**

```bash
# 基础字段（eapi 内置）
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# 嵌套字段 — 用双下划线 __ 分隔
OSS__ENDPOINT=http://localhost:9000
OSS__ACCESS_KEY=minioadmin
OSS__SECRET_KEY=minioadmin
OSS__BUCKET=my-app

ALIYUN_SMS__ACCESS_KEY_ID=AKID123
ALIYUN_SMS__ACCESS_KEY_SECRET=secret456
ALIYUN_SMS__SIGN_NAME=我的应用
ALIYUN_SMS__TEMPLATE_CODE=SMS_123456
```

**代码中通过属性链访问：**

```python
# ✅ 分组清晰
settings.oss.endpoint
settings.oss.bucket
settings.aliyun_sms.access_key_id

# ❌ 禁止扁平命名
settings.oss_endpoint
settings.oss_access_key
settings.aliyun_sms_access_key_id
```

### 分组原则

| 场景 | 做法 |
|------|------|
| eapi 内置字段（database_url 等） | 保持顶层，不嵌套 |
| 同一服务/SDK 的多个配置 | 拆成独立 `BaseModel` 嵌套 |
| 只有 1 个字段 | 保持顶层，不必嵌套 |
| 3 个以上同前缀字段 | 必须嵌套 |

- **禁止**在代码中硬编码配置值（数据库地址、密钥、端口等）
- **禁止**在模块顶层执行副作用（网络请求、数据库连接、文件读取）

## 十三、日志

### 强制规则
- 使用标准库 `logging` 或 `structlog`，**禁止** `print()` 出现在非调试代码中
- 使用 `%s` 占位符或 structlog 的结构化日志，**禁止** f-string 拼接日志

```python
# ❌ print 调试
print(f"User {user_id} not found")

# ❌ f-string 日志（参数不会延迟求值，且无法被日志聚合工具解析）
logger.info(f"User {user_id} created")

# ✅ 占位符日志
logger.info("User %s created", user_id)

# ✅ structlog
logger.info("user_created", user_id=user_id)
```

### 日志级别使用规范

| 级别 | 使用场景 |
|---|---|
| `DEBUG` | 开发调试信息，生产环境不输出 |
| `INFO` | 关键业务流程节点（用户注册、订单创建等） |
| `WARNING` | 异常但可恢复的情况（重试、降级） |
| `ERROR` | 错误但服务仍可用（单次请求失败） |
| `CRITICAL` | 服务不可用（数据库连接断开、必要服务宕机） |

## 十五、函数与类设计

### 强制规则

```python
# ❌ 超过 3 个位置参数
def create_user(name, age, email, role, department):
    ...

# ✅ 使用关键字参数或 Pydantic model
def create_user(request: CreateUserRequest) -> User:
    ...
```

- 函数体不超过 50 行（超过则拆分）
- 单个文件不超过 500 行（超过则拆分模块）
- 嵌套不超过 3 层（使用 early return 降低嵌套）

```python
# ❌ 深层嵌套
def process(data):
    if data:
        if data.is_valid:
            if data.has_items:
                for item in data.items:
                    ...

# ✅ 提前返回
def process(data):
    if not data:
        return
    if not data.is_valid:
        return
    if not data.has_items:
        return
    for item in data.items:
        ...
```

## 十六、数据校验与序列化

### 强制规则
- API 输入/输出使用 **Pydantic v2** 进行校验
- 内部数据结构优先使用 `dataclass`，需要校验时用 Pydantic
- **禁止**在业务逻辑中手动校验字典字段

```python
# ❌ 手动校验字典
def create_user(data: dict):
    if "name" not in data:
        raise ValueError("name required")

# ✅ Pydantic 自动校验
class CreateUserRequest(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: EmailStr
```

## 十七、常见反模式（禁止）

| 反模式 | 正确做法 |
|---|---|
| 可变默认参数 `def f(items=[])` | `def f(items: list \| None = None)` |
| `import *` | 显式导入 |
| 循环导入 | 重构模块或延迟导入 |
| 全局可变状态 | 依赖注入 |
| `os.path` 字符串拼接 | `pathlib.Path` |
| `datetime.now()` 无时区 | `datetime.now(tz=UTC)` |
| 手动拼接 SQL | ORM 或参数化查询 |
| `== True` / `== None` | `is True` / `is None` |
| `len(x) == 0` | `not x` |
| `type(x) == SomeType` | `isinstance(x, SomeType)` |
| `dict.keys()` 遍历 | 直接 `for k in dict` |
| 嵌套字典传递数据 | `dataclass` / `TypedDict` / Pydantic model |
| `@app.on_event("startup")` | `lifespan` context manager |
| service 层抛 `HTTPException` | 抛业务异常，异常处理器转换 |
| 路由里写数据库查询 | 调用 service 层 |
| `allow_origins=["*"]`（生产） | 明确列出允许的域名 |

## 十八、注释与文档

### 强制规则
- 注释用于解释 **为什么（why）**，而非 **做了什么（what）**
- 每个 `.py` 文件**必须**在顶部添加模块级 docstring，说明该文件的主要功能
- 所有类**必须**有 docstring，说明类的职责和用途
- 所有方法/函数（包括公开和私有）**必须**有 docstring，说明功能、参数和返回值
- docstring 统一使用 **Google 风格**

### 模块级 docstring

每个 `.py` 文件的第一行必须是模块 docstring：

```python
# ✅ 模块 docstring
"""用户相关的路由模块。

提供用户的 CRUD 接口，包括注册、查询、更新和删除。
"""

from fastapi import APIRouter
...
```

```python
# ❌ 缺少模块 docstring
from fastapi import APIRouter
...
```

### 类 docstring

```python
# ✅ 类 docstring
class UserService:
    """用户业务逻辑服务。

    负责用户的创建、查询、更新和删除操作，
    封装所有与用户相关的业务规则。
    """

    def __init__(self, db: AsyncSession) -> None:
        """初始化 UserService。

        Args:
            db: 异步数据库会话。
        """
        self.db = db
```

```python
# ❌ 缺少类 docstring
class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
```

### 方法/函数 docstring

```python
# ✅ 完整的 Google 风格 docstring
async def get_by_id(self, user_id: int) -> User:
    """根据 ID 查询用户。

    Args:
        user_id: 用户唯一标识。

    Returns:
        匹配的用户对象。

    Raises:
        NotFoundError: 用户不存在时抛出。
    """
    user = await self.db.get(User, user_id)
    if not user:
        raise NotFoundError("用户", user_id)
    return user
```

```python
# ✅ 简单函数可以使用单行 docstring
def _build_cache_key(self, user_id: int) -> str:
    """根据用户 ID 构建缓存键。"""
    return f"user:{user_id}"
```

```python
# ❌ 缺少 docstring
async def get_by_id(self, user_id: int) -> User:
    user = await self.db.get(User, user_id)
    if not user:
        raise NotFoundError("用户", user_id)
    return user
```

### docstring 规范

| 场景 | 要求 |
|---|---|
| 单行可描述清楚 | 使用单行 docstring：`"""根据用户 ID 构建缓存键。"""` |
| 有参数/返回值/异常 | 使用多行 Google 风格，包含 `Args`/`Returns`/`Raises` |
| `__init__` 方法 | 必须有 docstring，说明初始化参数 |
| 魔术方法（`__str__` 等） | 必须有 docstring，说明行为 |
| 私有方法 | 必须有 docstring，至少单行说明 |

### 行内注释
```python
# ❌ 无用注释
# 获取用户
user = get_user(user_id)

# ✅ 解释原因
# 此处使用缓存查询，因为用户表 QPS 超过 5000
user = cache.get_user(user_id)
```

### API 文档
- 路由函数的 docstring 会自动生成 OpenAPI 描述，保持简洁
- 使用 `summary` 参数替代 docstring 标题

```python
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="创建用户",
)
async def create_user(body: UserCreate) -> UserResponse:
    """根据提交的信息创建新用户，邮箱不可重复。"""
    ...
```

## 二十、dwyeapi 优先使用

### 适用条件

项目依赖中包含 `dwyeapi` 时，以下规则生效。

### 强制规则

编写 FastAPI 后端代码时，**必须优先使用 eapi 已有的类和函数**，禁止重复实现。

| 需求 | 使用 eapi | 禁止自建 |
|------|----------|---------|
| 配置管理 | `dwyeapi.config.BaseSettings` | 自写 Pydantic Settings 基类 |
| ORM 基类 | `dwyeapi.database.Base` + `TimestampMixin` | 自定义 DeclarativeBase |
| 异步引擎 | `create_async_engine_factory()` + `create_session_factory()` | 手动创建 engine/session |
| 依赖注入 | `create_get_db(session_factory)` | 手写 get_db 生成器 |
| 密码哈希 | `hash_password()` / `verify_password()` | 直接调用 bcrypt |
| JWT | `create_token()` / `decode_token()` | 直接调用 python-jose |
| 异常体系 | `NotFoundError` / `BusinessError` / `register_exception_handlers()` | 自定义异常 + 手写 handler |
| 响应格式 | `success()` / `fail()` / `paginated()` | 自定义响应包装函数 |
| 分页 | `PaginationParams` + `paginate()` | 自写分页参数类 |
| Redis 缓存 | `cache.configure()` / `cache.get_redis()` | 手动管理 Redis 连接 |
| 异步任务 | `tasks.setup_tasks()` / `@register` / `TaskContext` (需 `[tasks]` extra) | 手写 ARQ/Celery 集成 |

### 决策流程

```
需要某项基础设施功能
  → 1. 检查 eapi 是否已提供（查阅 dwy-backend-eapi skill）
    → 已提供：直接使用，不重复实现
    → 未提供：自行实现，代码注释中说明 eapi 不覆盖此功能
```

## 二十一、代码简约原则

### 核心思想

代码只写**必要的逻辑**，不写"以防万一"的冗余代码。信任内部代码和框架保证，只在系统边界（用户输入、外部 API）做校验。

### 禁止的冗余模式

```python
# ❌ 不必要的 fallback — 值已经有明确来源
name = user.name or ""           # user.name 不可能是 None
result = data.get("key", None)   # get 默认就返回 None

# ✅ 直接使用
name = user.name
result = data.get("key")

# ❌ 不必要的类型转换 — 值已经是目标类型
count = int(params.page)         # Pydantic 已校验为 int
text = str(title)                # title 声明为 str

# ✅ 直接使用
count = params.page
text = title

# ❌ 不必要的条件检查 — 逻辑上不可能走到 else
if task:
    return task
else:
    return None                  # 上面已经 return 了

# ✅ 直接返回
return task

# ❌ 不必要的默认值 — 调用方已保证传值
def process(data: dict = None):  # 所有调用方都传了 data
    if data is None:
        data = {}

# ✅ 去掉默认值和检查
def process(data: dict):
    ...

# ❌ 不必要的异常兜底 — 掩盖真正的 bug
try:
    result = calculate(x)
except Exception:
    result = 0                   # 吞掉异常，bug 永远不会被发现

# ✅ 让异常暴露，或只捕获预期的异常
result = calculate(x)
```

### 判断标准

写每一行防御代码前问自己：**这个情况在当前上下文下真的会发生吗？**

- 如果**会** → 写防御，加注释说明什么情况下触发
- 如果**不会** → 不写，信任上游保证
- 如果**不确定** → 查看调用链确认，不要"以防万一"

## 代码自检（写代码时强制执行）

**每次生成或修改 Python 代码后，必须逐条验证以下清单。任何一条未通过 → STOP，立即修正后再继续。**

| # | 检查项 | 违规即 STOP |
|---|--------|------------|
| 1 | 所有公开函数有参数 + 返回值类型标注 | ✓ |
| 2 | 无 `Any` 类型（除非有注释说明原因） | ✓ |
| 3 | 使用 `list[int]` / `str \| None` 等现代语法，不用 `typing.List` / `Optional` | ✓ |
| 4 | service 层不抛 `HTTPException`，只抛业务异常 | ✓ |
| 5 | 无裸 `except:` 或 `except Exception: pass` | ✓ |
| 6 | 路由函数只做参数接收 → 调用 service → 返回结果，无业务逻辑 | ✓ |
| 7 | HTTP 请求用 `httpx`，不用 `requests` | ✓ |
| 8 | 日志用 `%s` 占位符或 structlog，不用 f-string | ✓ |
| 9 | 生命周期用 `lifespan`，不用 `@app.on_event` | ✓ |
| 10 | 无可变默认参数 `def f(items=[])` | ✓ |
| 11 | Pydantic Schema 请求/响应分离，不复用 | ✓ |
| 12 | 嵌套不超过 3 层，函数体不超过 50 行 | ✓ |
| 13 | 所有模块/类/函数有 docstring（Google 风格） | ✓ |
| 14 | 依赖通过 `Depends()` 注入，不在路由中直接创建 | ✓ |
| 15 | 项目依赖 eapi 时，未重复实现 eapi 已有功能 | ✓ |

**不执行自检就提交代码 = 违规。**

---

## 错误处理规范(后端)

**唯一方式：** 使用 eapi exceptions 体系。

```python
from dwyeapi.exceptions import (
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

---

## 环境变量管理(后端:eapi BaseSettings + 嵌套分组)

**必须使用嵌套模型分组配置**，禁止所有字段平铺。同一服务/SDK 的多个字段拆成独立 `BaseModel`。

```python
# app/config.py
from pydantic import BaseModel
from dwyeapi.config import BaseSettings

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

详细规则见 `dwy-python-core.md` 第十二节。

---

## 日志规范

### 后端

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

### 日志级别规则

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 开发调试信息，生产环境不输出 | 变量值、SQL 语句 |
| INFO | 关键业务流程节点 | 用户登录、任务提交、导出完成 |
| WARNING | 异常但可恢复的情况 | 重试成功、降级处理 |
| ERROR | 错误但服务仍可用（单次请求失败） | 外部 API 超时、单个任务失败 |
| CRITICAL | 服务不可用 | 数据库连接断开、必要服务宕机 |

### 禁止事项

- 禁止 `print()`，全部用 `logger`
- 禁止在循环体内打 INFO/WARNING 日志（大量重复）
- 禁止日志中包含密码、token、密钥等敏感信息
- 禁止用 f-string 格式化日志消息（用 `%s` 占位符，支持日志聚合延迟求值）
