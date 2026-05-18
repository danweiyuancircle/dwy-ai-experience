---
description: Python 后端（FastAPI + SQLAlchemy）应用层开发规范 — 路由 / Schema / 依赖注入 / ORM / 安全编码 / 注入防护 / 限流 / 审计 / 违规检测清单
category: Python
paths:
  - "**/*.py"
---

# Python 后端开发规范（FastAPI + ORM + 安全）

适用于基于 FastAPI + SQLAlchemy 的应用层规范。基础设施专项规范（PostgreSQL / Redis / 对象存储 / 时序数据库等）见对应独立 rule。

---

## 零、优先使用 `dwyeapi` 基础框架库（强制）

`dwyeapi` 是团队内部 PyPI 基础设施包，已封装后端项目所需的通用能力。**凡是 dwyeapi 已提供的能力，禁止自行实现，也禁止引入其他库重复造轮子。**

### 必须复用 dwyeapi 的能力域

| 能力域 | 内容 |
|--------|------|
| 配置管理 | 应用 Settings 基类、运行环境识别（dev / prod） |
| 异常体系 | 业务异常基类与全局异常处理器注册 |
| 统一响应 | `{ code, message, data, timestamp }` 包装 |
| 分页 | 分页查询参数模型与分页响应封装 |
| 数据库 | ORM 声明式基类、时间戳 Mixin、异步引擎与会话工厂 |
| 依赖注入 | FastAPI `get_db` 工厂 |
| 安全 | 密码哈希、JWT 创建与解码 |
| 缓存 | 共享异步 Redis 客户端 |
| 时间 | 业务时间统一入口（Asia/Shanghai） |
| 脱敏 | PII 数据脱敏函数 |
| 日志 | 全局日志配置与门面 |
| 健康检查 | 健康检查路由工厂 |
| 异步任务 | 耗时任务队列与上下文 |
| 邮件 | 邮件验证码可插拔通道 |

### 查阅方式（关键）

**在编写任何后端代码前，以及调用任何 dwyeapi 提供的 API 之前，必须先用 `Skill` 工具加载 `dwy-eapi` skill 查阅当前最新接口。** 本文件**只规定约束与边界**，**不固化** dwyeapi 的具体模块路径、类名、函数签名、参数 —— 这些会随版本演进，固化在 rules 里会与实际包不同步。

```
Skill 工具调用：skill="dwy-eapi"
```

### 强制规则

- 涉及上表任一能力域，**先查 skill 拿到当前 API，再写代码**
- **禁止**自造异常基类，必须复用 dwyeapi 异常体系
- **禁止**手写 bcrypt / PyJWT 调用，必须走 dwyeapi 安全模块
- **禁止**自定义统一响应包装函数，必须用 dwyeapi 响应模块
- **禁止**自定义分页模型，必须用 dwyeapi 分页模块
- **禁止**自定义 `DeclarativeBase`，模型必须继承 dwyeapi 提供的基类
- **禁止**在路由函数中直接创建数据库会话，必须用 dwyeapi 依赖工厂
- **禁止**自建 Redis 连接池，必须用 dwyeapi 共享客户端
- **禁止**在业务代码中直接使用 `datetime.now()`，必须用 dwyeapi 时间模块
- **禁止**自行 `logging.basicConfig`，必须用 dwyeapi 日志模块

---

## 一、项目结构与业务聚合（强制）

### 核心原则

**按功能模块（feature / domain）聚合，禁止按技术层散落。** 同一业务功能的 router / schema / service / model / dependency 必须集中在同一个功能目录下；**禁止**全局存在 `routers/` / `services/` / `models/` / `schemas/` 等"技术层"顶级目录，把不相关功能的同类型文件强行揉到一起。

### 为什么

- **跨项目迁移**：复制单个功能目录即可携带该功能全部代码；技术层散落需在 4+ 目录里翻找
- **可读性**：阅读功能时所有相关代码在同一目录，无需跨目录跳转
- **变更影响域清晰**：一次改动 diff 集中，code review 更高效
- **删除友好**：删功能时整个目录删掉即可，不会留下孤儿文件

### 标准结构（参考）

```
app/
├── users/                  # 用户功能（一个业务模块自成一个目录）
│   ├── __init__.py
│   ├── router.py           # FastAPI 路由
│   ├── schemas.py          # Pydantic 请求 / 响应模型
│   ├── service.py          # 业务逻辑
│   ├── models.py           # ORM 模型
│   ├── dependencies.py     # 该功能专用 Depends（可选）
│   └── exceptions.py       # 该功能专用异常（可选）
├── orders/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── models.py
├── core/                   # 跨功能共享：配置 / 全局中间件 / 启动逻辑
│   ├── config.py
│   ├── middleware.py
│   └── lifespan.py
└── main.py                 # 注册各功能 router
```

### 强制规则

- **禁止**顶级 `routers/` / `services/` / `models/` / `schemas/` 把不同功能的同类文件混放
- 一个功能目录内文件名固定：`router.py` / `schemas.py` / `service.py` / `models.py`（单数，不带功能前缀）
- 跨功能真正共享的代码放 `core/` 或 `shared/`，**禁止**为"可能复用"把单一功能逻辑提前抽离
- 单文件超过约 400 行时再考虑拆分（如 `service.py` → `services/create.py` + `services/query.py`），**禁止**未到规模就预拆分
- 功能间引用通过明确 import，**禁止**循环依赖
- 测试镜像功能聚合结构：`tests/users/test_router.py` / `tests/users/test_service.py`（详见第九节）

### 例外
- 通用基础设施代码（如 dwyeapi 内部）可保持技术层结构

---

## 二、FastAPI 路由与接口设计

### 强制规则

- 每个路由模块独立 `APIRouter`，在 `main.py` 统一注册
- **禁止**所有路由写在 `main.py` 中（超过 2 个路由必须拆分）
- 路由函数只做：参数接收 → 调用 service → 返回结果，**不写业务逻辑**
- 必须显式声明 `status_code` 和 `response_model`
- 所有路由统一加 `/api` 前缀

### URL 命名

- 资源名用**复数**、**kebab-case**：`/api/upload-tasks`，**禁止** `/api/uploadTasks` 或 `/api/upload_task`
- 路径参数用 `{xxx_uuid}: str`（详见 7.1 ID 设计），**禁止** `{id}: int`
- 查询参数用 **snake_case**：`?page_size=20&task_type=export`
- **禁止**在 URL 中包含动词（用 HTTP 方法表达 CRUD）
- 非 CRUD 动作用 `POST + 动词`：`POST /api/users/{uuid}/activate`、`POST /api/tasks/{uuid}/cancel`

### RESTful 路由规范

| 操作 | 方法 | 路径 | 状态码 |
|---|---|---|---|
| 列表查询 | `GET` | `/api/users` | 200 |
| 详情查询 | `GET` | `/api/users/{user_uuid}` | 200 |
| 创建 | `POST` | `/api/users` | 201 |
| 全量更新 | `PUT` | `/api/users/{user_uuid}` | 200 |
| 部分更新 | `PATCH` | `/api/users/{user_uuid}` | 200 |
| 删除 | `DELETE` | `/api/users/{user_uuid}` | 204 |
| 子资源 | `GET` | `/api/users/{user_uuid}/orders` | 200 |
| 动作 | `POST` | `/api/users/{user_uuid}/activate` | 200 |

### HTTP 状态码

| 场景 | 状态码 |
|------|--------|
| 查询 / 更新成功 | 200 |
| 创建成功 | 201 |
| 删除成功 | 204（无响应体） |
| 参数格式错误 | 400 |
| 未认证（Token 缺失或过期） | 401 |
| 无权限（认证通过但权限不足） | 403 |
| 资源不存在 | 404 |
| 业务规则不允许 | 422 |

```python
# routers/user.py
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    body: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create(body)
```

### 统一响应格式

所有成功 / 分页 / 错误响应统一走 dwyeapi 响应与异常模块（具体 API 与字段结构查 `dwy-eapi` skill），**禁止**自造响应包装函数，**禁止**在 router 中手动构造 `{"success": true, ...}` 等非标准格式。

### 分页

分页参数模型与响应包装统一走 dwyeapi（具体 API 查 `dwy-eapi` skill），**禁止**自定义。

---

## 三、Pydantic Schema 规范

### 命名约定

| Schema 类型 | 命名 | 用途 |
|------------|------|------|
| 创建请求 | `XxxCreate` | POST body |
| 更新请求（字段全可选） | `XxxUpdate` | PATCH body |
| 响应（完整字段） | `XxxResponse` | 详情接口返回 |
| 响应（精简字段） | `XxxBrief` | 列表接口返回 |

### 强制规则

- 请求与响应使用**不同**的 Schema，**禁止**复用同一个 Model
- 更新 Schema 的字段必须全部可选
- **禁止**在响应 Schema 中暴露密码、内部自增 ID、敏感字段
- 必须使用 `Field()` 添加校验约束（`min_length` / `max_length` / `ge` / `le` / `pattern` 等）
- **禁止**用松散字典 / `dict` / `Any` 直接接收 body，必须有显式 Schema

```python
class UserBase(BaseModel):
    name: str = Field(max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)  # 72 = bcrypt 输入上限

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None

class UserResponse(UserBase):
    uuid: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 输入校验清单

| 字段类型 | 校验 |
|---------|------|
| 数字 | `ge` + `le`（最小值 + 最大值） |
| 邮箱 | `EmailStr` |
| 手机号 | `pattern=r"^1[3-9]\d{9}$"` |
| URL | `HttpUrl` |
| 分页 page_size | 必须有上限（≤ 100） |
| 字符串 | 必须显式 `max_length` |
| 文件上传 | 后端二次校验大小 + magic bytes，**禁止**只信任前端或 Nginx |

---

## 四、依赖注入

### 强制规则

- 数据库会话、当前用户、配置等**必须**通过 `Depends()` 注入
- **禁止**在路由函数中直接创建数据库会话或实例化 service
- `get_db` 依赖必须用 dwyeapi 提供的工厂生成（具体 API 查 `dwy-eapi` skill）

```python
# 反例：路由中直接创建会话
@router.get("/users/{user_uuid}")
async def get_user(user_uuid: str):
    async with async_session_factory() as db:
        ...

# 正例：依赖注入
@router.get("/users/{user_uuid}", response_model=UserResponse)
async def get_user(
    user_uuid: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.get_by_uuid(user_uuid)
```

---

## 五、异常处理

### 强制规则

- **必须**复用 dwyeapi 异常体系与全局处理器（具体异常类与注册方法查 `dwy-eapi` skill），**禁止**自造异常基类
- 项目级扩展异常必须继承 dwyeapi 异常基类
- **service 层**抛业务异常，**禁止**抛 `HTTPException`（service 不感知 HTTP）
- **router 层**不写 `try / except`，由全局 handler 统一处理
- **禁止**裸 `except:` 或 `except Exception: pass`
- **禁止**在错误消息中回显用户输入
- **禁止**将原始异常信息（`str(e)`）泄露给客户端

---

## 六、数据库与 ORM（SQLAlchemy 2.0 异步）

### 强制规则

- 必须使用 **SQLAlchemy 2.0** 声明式映射 + async
- 模型继承 dwyeapi 提供的声明式基类与时间戳 Mixin（具体类名查 `dwy-eapi` skill），**禁止**自定义 `DeclarativeBase`
- 数据库迁移使用 **Alembic**，**禁止**手动执行 DDL
- **禁止**在路由层直接写 SQL 查询
- **禁止**使用 SQLAlchemy 1.x 风格的 `session.query(...)`

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
import uuid as uuid_lib

class User(BaseFromDwyeapi, TimestampMixinFromDwyeapi):  # 实际基类名以 skill 为准
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        default=lambda: str(uuid_lib.uuid4()),
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)
```

### 查询规范

```python
# 反例：旧式查询
session.query(User).filter(User.id == user_id).first()

# 正例：SQLAlchemy 2.0
result = await session.execute(select(User).where(User.uuid == user_uuid))
user = result.scalar_one_or_none()
```

---

## 七、安全编码

### 7.1 ID 设计（防遍历攻击）

**核心原则**：数据库内部用自增 ID（性能），对外暴露 UUID（安全）。

- 所有 ORM 模型必须同时有 `id`（自增）和 `uuid`（对外）
- 路由路径参数**必须**为 `{xxx_uuid}: str`，**禁止** `{xxx_id}: int`
- Response Schema **只返回 uuid**，**禁止**暴露自增 id

### 7.2 密码安全

| 规则 | 说明 |
|------|------|
| 存储算法 | **只允许 bcrypt**，必须走 dwyeapi 安全模块，**禁止**手写 bcrypt 调用或使用 MD5 / SHA / 明文 |
| 接口返回 | **永远不返回**密码字段，Response Schema 中不包含 |
| 密码强度 | **长度 ≥ 8 字符**，且**必须**包含 **大写字母、小写字母、数字、特殊符号** 中的至少 **3 类** |
| 密码长度上限 | Schema 必须 `max_length=72`（bcrypt 输入硬上限，超过会被静默截断），除非 dwyeapi 已做 SHA-256 预哈希 |
| 登录错误 | 返回"用户名或密码错误"，**不区分**是用户名不存在还是密码错误 |
| 强度校验位置 | Pydantic Schema 层用 `field_validator` 校验复杂度，**禁止**只校长度 |

**密码复杂度校验示例**：

```python
import re
from pydantic import BaseModel, Field, field_validator

PASSWORD_PATTERNS = [
    re.compile(r"[A-Z]"),       # 大写
    re.compile(r"[a-z]"),       # 小写
    re.compile(r"\d"),          # 数字
    re.compile(r"[^A-Za-z0-9]"),  # 特殊符号
]

class UserCreate(BaseModel):
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def check_complexity(cls, v: str) -> str:
        """密码必须包含大写/小写/数字/特殊符号中至少 3 类。"""
        matched = sum(1 for p in PASSWORD_PATTERNS if p.search(v))
        if matched < 3:
            raise ValueError("密码必须包含大写、小写、数字、特殊符号中至少 3 类")
        return v
```

> 该 validator 建议下沉到 dwyeapi 提供统一的 `PasswordStr` 类型，避免每个项目重复实现。

### 7.3 接口认证与授权

- 所有 API **必须** JWT 认证（白名单除外：`/health` / `/auth/login` / `/auth/register`）
- JWT 创建与解码**必须**走 dwyeapi 安全模块，**禁止**直接调用 PyJWT
- Token 黑名单存 Redis（登出后失效，TTL = 剩余有效期）
- Secret Key 必须从环境变量读取，**禁止**硬编码
- Secret Key 长度与生成方式（按字节算，不按字符算）：

| JWT 算法 | 最小长度 | 推荐生成命令 |
|---------|---------|------------|
| HS256 | **32 字节 / 256 bit** | `openssl rand -hex 32`（输出 64 个十六进制字符 = 32 字节） |
| HS512 | **64 字节 / 512 bit** | `openssl rand -hex 64`（输出 128 个十六进制字符 = 64 字节） |
| Python 等价 | — | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

- **禁止**使用：`uuid.uuid4().hex`（熵不足且非密码学 PRNG 推荐用途）、`random` 模块、手写字符串拼接
- 轮换策略：每 90 天 / 安全事件后立即轮换；新旧 Key 共存 1 个 Access Token 有效期窗口，避免在线用户被强制登出

| Token 类型 | 有效期 |
|------------|--------|
| Access Token | 30 分钟（最长 ≤ 2 小时） |
| Refresh Token | 7 天 |

### 7.4 响应安全

- **禁止**直接返回 ORM 对象（可能暴露 password、内部 ID 等）
- 列表接口**必须**分页，**禁止**返回全量数据
- PII 字段（手机号 / 邮箱 / 身份证 / 银行卡 / 姓名 / 地址 / IP / 车牌）必须使用 dwyeapi 脱敏函数处理

### 7.5 错误处理安全

生产环境**禁止**返回以下内容：

| 禁止内容 | 原因 |
|---------|------|
| 完整异常堆栈 | 暴露代码结构和文件路径 |
| 原始 SQL 语句 | 暴露表结构和查询逻辑 |
| 文件系统路径 | 暴露服务器目录结构 |
| 用户输入回显 | XSS 和信息泄露 |
| 数据库字段名 | 暴露数据模型 |
| 第三方 API Key | 凭证泄露 |

### 7.6 注入防护

#### SQL 注入

```python
# 反例：字符串拼接
result = await session.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))

# 正例：ORM 参数化
result = await session.execute(select(User).where(User.id == user_id))

# 正例：原生 SQL 参数化
result = await session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

#### 命令注入

- **禁止**通过 shell 拼接用户输入执行外部命令
- 必须使用参数列表 + `shell=False` 调用 `subprocess`
- 最佳实践：改用 Python 库实现同等功能（如图像处理用 Pillow，文件压缩用 zipfile），避免外部命令

#### 路径遍历

```python
# 反例
file_path = f"/uploads/{user_input_filename}"

# 正例
from pathlib import Path
safe_name = Path(user_input_filename).name
file_path = Path("/uploads") / safe_name
```

#### SSRF（服务端请求伪造）

用户控制的 URL 必须经白名单 host 校验后再发起请求，防止访问内网（如 `169.254.169.254`）。

### 7.7 软删除

- 业务数据**必须**软删除（`is_deleted` + `deleted_at`），**禁止**物理删除
- 查询时自动 `where(Model.is_deleted == False)`
- **例外**：GDPR 被遗忘权、验证码 / session 等临时数据，允许物理删除

### 7.8 审计日志

通过 dwyeapi 日志模块获取审计 logger，记录以下操作：

| 操作 | 记录内容 |
|------|---------|
| 登录成功/失败 | 用户名、IP、时间、User-Agent |
| 权限变更 | 操作人、目标用户、旧角色、新角色 |
| 数据删除 | 操作人、删除资源类型和 UUID |
| 敏感数据查询 | 查询人、查询条件（脱敏） |
| 密码修改 | 操作人、时间 |
| 导出操作 | 操作人、导出数据范围 |

---

## 八、API 限流

使用 `slowapi`，按接口类型设置不同限流策略：

| 接口类型 | 限流 | 原因 |
|---------|------|------|
| 登录 `/auth/login` | 3 次/分钟/IP | 防暴力破解 |
| 注册 `/auth/register` | 5 次/分钟/IP | 防批量注册 |
| 普通查询 | 60 次/分钟/IP | 防爬虫 |
| 数据导出 | 5 次/分钟/IP | 防数据泄露 |
| 文件上传 | 10 次/分钟/IP | 防资源滥用 |

---

## 九、测试组织

### 核心约束（强制）

- **测试目录与业务源码并列、独立存放**，禁止混入源码目录
- **禁止**在源码目录中放任何 `test_*.py` / `*_test.py` 文件（如 `app/services/user.py` 旁放 `app/services/test_user.py` 是违规）
- 测试目录内部结构应**镜像**对应源码结构，便于定位被测对象
- 测试文件命名：`test_{被测模块名}.py`
- pytest 配置在 `pyproject.toml`（`[tool.pytest.ini_options]`）中显式声明 `testpaths`
- 测试相关依赖放 `[dev]` 或独立 `[test]` extras / group，**禁止**进生产依赖
- 跨包发布的代码不得 import 测试目录下的内容

> 具体目录布局由项目结构决定（单包、monorepo 子包、扁平 `app/` 等），AI 自行判断；唯一不变的是"测试目录独立、与源码并列"。

具体 pytest fixture、AsyncClient、Arrange-Act-Assert 等编写规范见 `dwy-python-testing` rule。

---

## 十、违规检测清单

AI 编写或审查后端代码时，**必须**检查以下违规模式，按严重程度执行对应动作：

### 严重程度与动作

| 严重程度 | 动作 |
|---------|------|
| **致命** | **立即 STOP，不得继续编写或提交代码**，必须修正后重新检查 |
| **高** | 必须修正后才能继续，向用户说明违规点和修正方案 |
| **中** | 提示用户存在风险，建议修正，用户确认后可继续 |

### 检查清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 重复造轮子 | 自造异常基类 / 自封装统一响应 / 手写 bcrypt 或 JWT 调用 / 自建 Redis 连接池 等 dwyeapi 已提供能力 | 高 |
| 未查 skill | 调用 dwyeapi 能力域却未先查 `dwy-eapi` skill 拿当前 API | 高 |
| 技术层散落 | 顶级出现 `routers/` / `services/` / `models/` / `schemas/` 等技术层目录把不同功能文件混放，未按功能聚合 | 高 |
| 测试与源码混放 | 测试文件放在源码目录中（如 `app/users/test_router.py`），未独立到测试目录 | 高 |
| 密码明文 | `password` 字段出现在 Response Schema | **致命 → STOP** |
| 密码弱存储 | 使用 MD5 / SHA 而非 bcrypt | **致命 → STOP** |
| SQL 拼接 | f-string 拼接 SQL 语句 | **致命 → STOP** |
| 命令注入 | shell 拼接用户输入执行外部命令 | **致命 → STOP** |
| 硬编码密钥 | SECRET_KEY / DB 密码等硬编码 | **致命 → STOP** |
| 自增 ID 暴露 | 路由参数为 `int` 类型的 ID / Response 含 `id: int` | 高 |
| 无认证接口 | 数据接口无 `Depends(get_current_user)` | 高 |
| 全量返回 | 列表接口无分页限制 | 高 |
| 松散 body | 用 `dict` / `Any` 接收请求体 | 高 |
| 错误回显 | `str(exception)` 返回给客户端 / 错误消息含用户输入 | 高 |
| 文件名不安全 | 使用用户原始文件名做存储路径 | 高 |
| service 抛 HTTPException | service 层直接 `raise HTTPException` | 高 |
| 路由中开会话 | 路由函数中 `async with session_factory()` | 高 |
| 旧式查询 | `session.query(...)` 而非 `select(...)` | 高 |
| `datetime.now()` 直用 | 业务代码直接 `datetime.now()` 而非走 dwyeapi 时间模块 | 高 |
| 物理删除业务数据 | 对业务数据执行物理删除 | 中 |
