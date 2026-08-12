---
description: Python 通用代码规范
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python 通用代码规范

适用于所有 Python 代码（脚本 / 库 / 后端 / 数据处理 / CLI / 测试等）。Web 框架、ORM 等领域专属规范见对应 rules / skills。

## 一、依赖与虚拟环境

### 强制规则

- **强制使用 `uv`** 管理虚拟环境与依赖，**禁止** `pip` / `poetry` / `pipenv` / 原生 `venv` / `conda`

### 环境变量

- **禁止**在 shell 前台 `export FOO=...` 注入环境变量
- **禁止**在代码中硬编码以下配置值：
  - **基础设施**：数据库地址、Redis / MQ 地址、密钥、端口、外部 API 地址
  - **业务参数**：缓存 TTL、HTTP 超时、重试次数 / 间隔、批处理大小、限流阈值（rate / burst）、分页默认值与上限、文件大小上限、Token 有效期、定时任务周期
- 判定标准：**任何"运维 / 业务可能想调整、且不希望发版"的值，都必须走配置**。代码中只允许出现：算法常量（PI、HTTP 状态码）、协议规定的固定值、纯类型枚举（如 `Status.ACTIVE = 1`）
- 环境变量统一通过 `.env` 文件加载，由 Pydantic Settings 读取（见「配置管理」节）
- `.env` 必须列入 `.gitignore`，提交 `.env.example` 作为模板

## 二、Python 版本与现代语法

### 强制规则

- 新项目最低支持 Python 3.11+
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
target-version = "py311"
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
    "D",    # pydocstyle (docstring 规范，强制 Google 风格)
]
ignore = [
    "D100",  # 模块顶层 docstring：脚本/迁移等不强制（按需在文件头补）
    "D104",  # __init__.py 不强制 docstring
    "D107",  # __init__ 方法 docstring 写在类 docstring 里（与本规范一致）
    "D203",  # 与 D211 冲突，二选一（Google 风格选 D211：类 docstring 前不加空行）
    "D213",  # 与 D212 冲突，二选一（Google 风格选 D212：多行 docstring 首行紧跟 """）
    "D401",  # 中文 docstring 不要求祈使句开头
    "D415",  # 中文 docstring 不要求以 . ! ? 结尾（用中文句号 。）
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
# 测试文件不强制 docstring（测试方法名已自描述）
"tests/**/*.py" = ["D100", "D101", "D102", "D103", "D104"]
"**/test_*.py" = ["D100", "D101", "D102", "D103", "D104"]
# 迁移脚本不强制 docstring
"**/migrations/**/*.py" = ["D"]
# CLI 入口脚本不强制模块 docstring
"**/__main__.py" = ["D100"]
```

启用后 ruff 会强制检查：

- 公开模块/类/函数/方法必须有 docstring（D101 / D102 / D103）
- 私有方法以单下划线开头时不强制（pydocstyle 默认）
- Google 风格 section 格式（`Args:` / `Returns:` / `Raises:`）
- docstring 首行必须紧跟 `"""`（D212）
- 类 docstring 前不留空行（D211）

⚠️ **D 规则只校验「有没有 docstring + 格式」，不校验「Args 是否包含类型/示例/边界」**。后者无法静态检查，靠 code review + 本规范第九节强制要求落实。

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

### 禁止魔法字符串

同一字符串字面量在同一文件出现 ≥ 2 次 → **必须**提取为常量；跨模块共享 → 提取到 `constants.py`。

```python
USER_TOKEN_KEY = "user:token:{user_id}"
redis.set(USER_TOKEN_KEY.format(user_id=123), token)
```

### 禁止的写法

| ❌ | ✅ |
|---|---|
| `d = get_data()` | `user_data = get_data()`（单字母变量仅允许循环索引） |
| `str_name = "Alice"` / `lst_users = []` | `name = "Alice"` / `users = []`（不用匈牙利命名法） |
| `active = True` | `is_active = True` / `has_permission = False`（布尔加 is/has/can/should 前缀） |

## 四、类型标注

- 所有公开函数/方法**必须**有参数和返回值类型标注
- 私有函数**推荐**有类型标注
- 类属性**必须**有类型标注
- **禁止** `Any` 作为"懒标注"，除非与外部动态库交互且无法确定类型；使用时必须附注释说明原因

```python
def get_user(user_id: int) -> User | None: ...
type UserMap = dict[str, list[User]]

@dataclass
class UserProfile:
    name: str
    age: int
    email: str | None = None
```

## 五、配置管理

### 强制规则

- 使用 Pydantic Settings 管理配置
- **必须使用嵌套模型分组**，禁止所有字段平铺在一个类中
- **禁止**扁平命名（如 `settings.oss_endpoint`），必须 `settings.oss.endpoint` 属性链访问
- **禁止**在模块顶层执行副作用（网络请求、数据库连接、文件读取）

```python
# config.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class OssConfig(BaseModel):
    endpoint: str = ""

class Settings(BaseSettings):
    app_name: str = "My App"
    oss: OssConfig = OssConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # 关键：启用嵌套分隔符
    )
```

`.env` 用 `__` 分隔层级：`OSS__ENDPOINT=http://localhost:9000`。

### 分组原则

| 场景 | 做法 |
|------|------|
| 同一服务/SDK 的多个配置 | 拆成独立 `BaseModel` 嵌套 |
| 只有 1 个字段 | 保持顶层，不必嵌套 |
| 3 个以上同前缀字段 | 必须嵌套 |

### 什么必须走配置（判定表）

写代码时遇到字面量数字 / 字符串，先对照此表判断是否抽到 Settings：

| 类别 | 示例 | 是否走配置 |
|------|------|-----------|
| 基础设施地址 | `postgresql://...` / `redis://...` / `https://api.xxx.com` | ✅ 必须 |
| 凭证 | SECRET_KEY / API_KEY / DB 密码 / OSS AK·SK | ✅ 必须（致命） |
| 缓存 TTL | `redis.setex(key, 43200, v)` 中的 `43200` | ✅ 必须 → `settings.cache.user_token_ttl` |
| HTTP 超时 / 重试 | `httpx.AsyncClient(timeout=30)` 中的 `30` | ✅ 必须 |
| 限流阈值 | `@rate_limit(100, per=60)` 中的 `100` / `60` | ✅ 必须 |
| 分页默认 / 上限 | `page_size: int = 20` / `le=100` 的 `100` | ✅ 必须 |
| 文件大小上限 | `if size > 10 * 1024 * 1024` 的 `10MB` | ✅ 必须 |
| Token 有效期 | JWT `exp` 的 7 天 / 30 天 | ✅ 必须 |
| 定时任务周期 | Celery / APScheduler 的 cron / interval | ✅ 必须 |
| 算法常量 | `PI = 3.14159` / `EARTH_RADIUS = 6371` | ❌ 不走配置 |
| 协议规定值 | HTTP 状态码 `200` / `404` | ❌ 不走配置 |
| 纯枚举值 | `class Status: ACTIVE = 1` | ❌ 不走配置 |

```python
# ❌ 错误：缓存 TTL 硬编码
await redis.setex(f"user:{uid}", 43200, json.dumps(user))

# ✅ 正确：走 Settings
class CacheConfig(BaseModel):
    user_ttl: int = 43200  # 默认 12h，可通过 CACHE__USER_TTL 覆盖

await redis.setex(f"user:{uid}", settings.cache.user_ttl, json.dumps(user))
```

## 六、函数与类设计

### 强制规则

- 超过 3 个位置参数 → 改用关键字参数或 Pydantic model 包装
- 函数体不超过 50 行（超过则拆分）
- 单个文件不超过 500 行（超过则拆分模块）
- 嵌套不超过 3 层（用 early return 降低嵌套）

```python
# ❌ 深层嵌套
def process(data):
    if data:
        if data.is_valid:
            if data.has_items:
                for item in data.items: ...

# ✅ early return
def process(data):
    if not data: return
    if not data.is_valid: return
    if not data.has_items: return
    for item in data.items: ...
```

## 七、数据校验与序列化

### 强制规则

- 外部输入（用户请求、外部 API 响应、文件读入）使用 **Pydantic v2** 校验
- 内部数据结构优先使用 `dataclass`，需要校验时用 Pydantic
- **禁止**手动校验字典字段（如 `if "name" not in data: raise ...`）

```python
class CreateUserRequest(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: EmailStr
```

## 八、常见反模式（禁止）

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
| 裸 `except:` / `except Exception: pass` | 只捕获预期的具体异常 |
| `print()` 输出调试信息 | 使用 `logging` |

## 九、注释与文档

### 强制规则

- 注释解释 **为什么（why）**，而非 **做了什么（what）**
- 每个 `.py` 文件**必须**有模块级 docstring
- 所有类、所有方法/函数（含私有）**必须**有 docstring
- docstring 统一使用 **Google 风格**

### 临时代码标识（强制）

产品源码中的业务待办、调试旁路、假数据**必须**用固定标签，便于编辑器全局搜索。`tests/` 内正规 mock / fixture **不强制**。

| 标签 | 用途 | 格式 |
|---|---|---|
| `TODO` | 业务/技术未完成 | `# TODO(name, YYYY-MM-DD): 说明`（推荐带责任人与日期） |
| `TESTCODE` | 临时调试、跳过校验、试验开关 | `# TESTCODE: 说明 + 移除条件` |
| `MOCK` | 假数据、假接口、stub 实现 | `# MOCK: 说明 + 将来替换点` |

- 写 mock/调试代码的**同一 diff 必须带标**；接真实现后**删标签与包夹**
- 禁止无标签假返回；禁止自造 `# 假数据`、`# test only` 等替代词
- 发版/提测前 `rg 'MOCK|TESTCODE'`，清单交给负责人确认（允许残留但须知情）

**单行**（仅一行代码）：

```python
# MOCK: 登录假 token，接 POST /auth/login 后删除
return {"token": "fake-token"}

# TESTCODE: 强制测试账号，提测前删除
user_id = 1
```

**多行 / 大段（≥2 行逻辑）强制包夹**：

```text
# MOCK BEGIN: <说明 + 将来替换点>
...
# MOCK END

# TESTCODE BEGIN: <说明 + 移除条件>
...
# TESTCODE END
```

```python
# MOCK BEGIN: 用户详情假数据，接 UserRepository.get 后删除
user = {
    "id": 1,
    "name": "张三",
    "roles": ["admin"],
}
return user
# MOCK END
```

### 完整示例（模块 / 类 / 方法 / 私有方法 docstring）

```python
"""用户数据处理工具。

提供用户对象的序列化、反序列化和缓存键构建。
"""

class UserRepository:
    """用户数据仓储。封装用户表的查询、写入和缓存逻辑。"""

    def __init__(self, db: Database) -> None:
        """初始化 UserRepository。

        Args:
            db (Database): 数据库连接对象。示例：``Database("postgresql+asyncpg://user:pass@localhost:5432/app")``。
        """
        self.db = db

    def get_by_id(self, user_id: int, *, page_size: int = 20) -> User:
        """根据 ID 查询用户。

        Args:
            user_id (int): 用户唯一标识。取值范围 ``[1, 2^31-1]``。示例：``1001``。
            page_size (int): 关联数据分页大小。取值范围 ``[1, 100]``，默认 ``20``。示例：``50``。
        Returns:
            User: 匹配的用户对象。
        Raises:
            UserNotFound: 用户不存在时抛出。
        """
        user = self.db.get(User, user_id)
        if not user:
            raise UserNotFound(user_id)
        return user

    def _build_cache_key(self, user_id: int) -> str:
        """根据用户 ID 构建缓存键。

        Args:
            user_id (int): 用户唯一标识。取值范围 ``[1, 2^31-1]``。示例：``1001``。
        Returns:
            str: 缓存键，形如 ``user:1001``。
        """
        return f"user:{user_id}"
```

### docstring 规范

| 场景 | 要求 |
|---|---|
| 单行可描述清楚 | 使用单行 docstring |
| 有参数/返回值/异常 | 多行 Google 风格，包含 `Args` / `Returns` / `Raises` |
| `__init__` 方法 | 必须有，说明初始化参数 |
| 魔术方法（`__str__` 等） | 必须有，说明行为 |
| 私有方法 | 必须有，至少单行说明 |

### Args 参数注释规范（强制）

每个参数的 `Args` 注释**必须包含四要素**：参数名、类型、描述、示例；**有取值边界的必须显式标注边界**。

格式模板：

```
参数名 (类型): 描述。[取值范围 `[min, max]` / 长度 `[min, max]` / 枚举 `{a, b, c}`，默认 `xxx`。]示例：`具体值`。
```

| 要素 | 写法 | 示例 |
|---|---|---|
| 类型 | 紧跟参数名，括号包裹，与函数签名一致 | `user_id (int)` |
| 描述 | 一句话说明语义，不重复参数名 | `用户唯一标识` |
| 取值边界 | 数值用区间，字符串用长度，离散值用枚举 | `取值范围 [1, 100]` / `长度 [1, 64]` / `枚举 {"asc", "desc"}` |
| 默认值 | 与签名一致，显式写出 | `默认 20` |
| 示例 | 反引号包裹，给出真实可用值 | `示例：1001` |

**强制要求**：

- 凡是函数签名有 `int` / `float` / 字符串长度限制 / 时间窗口 / 分页 / 文件大小 / 比例阈值等**数值或长度型参数**，Args 注释**必须**写取值边界
- 凡是离散取值（状态枚举、排序方向、模式开关）**必须**列出可选值
- 凡是有副作用风险的参数（如 `force=True`、`delete=True`）**必须**在描述中提示风险

正反例：

```python
# ❌ 缺类型、缺示例、缺边界
def search(keyword, limit=20):
    """搜索用户。

    Args:
        keyword: 搜索关键词。
        limit: 返回数量。
    """

# ❌ 有类型但没边界、没示例
def search(keyword: str, limit: int = 20) -> list[User]:
    """搜索用户。

    Args:
        keyword (str): 搜索关键词。
        limit (int): 返回数量。
    """

# ✅ 四要素齐全，边界明确
def search(keyword: str, limit: int = 20, order: str = "desc") -> list[User]:
    """搜索用户。

    Args:
        keyword (str): 搜索关键词。长度范围 ``[1, 64]``。示例：``"alice"``。
        limit (int): 返回数量。取值范围 ``[1, 100]``，默认 ``20``。示例：``50``。
        order (str): 排序方向。枚举 ``{"asc", "desc"}``，默认 ``"desc"``。示例：``"asc"``。
    Returns:
        list[User]: 匹配的用户列表，按创建时间排序。
    """
```

### 行内注释

```python
# ❌ 无用：# 获取用户 \n user = get_user(user_id)
# ✅ 解释原因：# 此处用缓存，因为用户表 QPS 超过 5000
user = cache.get_user(user_id)
```

## 代码自检（写代码时强制执行）

**每次生成或修改 Python 代码后，必须逐条验证以下清单。任何一条未通过 → STOP，立即修正后再继续。**

| # | 检查项 |
|---|--------|
| 1 | 依赖与虚拟环境用 `uv`，不用 pip / poetry / pipenv / venv |
| 2 | 环境变量走 `.env` + Pydantic Settings，不在 shell 前台 export |
| 3 | 所有公开函数有参数 + 返回值类型标注 |
| 4 | 无 `Any` 类型（除非有注释说明原因） |
| 5 | 使用 `list[int]` / `str \| None` 等现代语法，不用 `typing.List` / `Optional` |
| 6 | 无裸 `except:` 或 `except Exception: pass` |
| 7 | 无可变默认参数 `def f(items=[])` |
| 8 | 嵌套不超过 3 层，函数体不超过 50 行 |
| 9 | 所有模块/类/函数有 docstring（Google 风格） |
| 10 | 所有函数的 `Args` 注释包含「类型 + 描述 + 示例」三要素；数值/长度/枚举型参数必须显式标注取值边界 |
| 11 | 外部输入用 Pydantic 校验，不手动校验 dict |
| 12 | 配置必须 Pydantic Settings 嵌套分组；缓存 TTL / 超时 / 重试 / 限流 / 分页上限 / 文件上限 / Token 有效期等业务参数禁止硬编码 |

**不执行自检就提交代码 = 违规。**
