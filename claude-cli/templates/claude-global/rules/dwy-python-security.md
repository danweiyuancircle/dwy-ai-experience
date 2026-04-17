---
description: Python 后端安全编码(认证/校验/注入/存储/RBAC 等)
paths:
  - "**/*.py"
---

# Python 后端安全编码

## 十九、安全编码

### 强制规则
- SQL 查询必须使用参数化绑定，**禁止**字符串拼接
- 用户输入必须校验后使用，**禁止**直接信任
- 文件路径操作必须防止路径遍历攻击
- 序列化/反序列化**禁止**用不安全的反序列化库处理不可信数据
- 密码存储必须使用 `bcrypt` / `argon2`，**禁止**明文或 MD5/SHA
- JWT 密钥从环境变量读取，**禁止**硬编码

```python
# BAD: SQL 注入
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD: 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# BAD: 路径遍历
file_path = f"/uploads/{user_input_filename}"

# GOOD: 路径安全校验
safe_path = Path("/uploads") / Path(user_input_filename).name

# BAD: 硬编码密钥
SECRET_KEY = "my-super-secret-key"

# GOOD: 环境变量
SECRET_KEY = settings.secret_key
```

---

# 后端安全编码规范

FastAPI + PostgreSQL + Redis + MinIO + DolphinDB 项目的安全编码规则。AI 生成或修改代码时，必须严格按照这些规则执行。

## 一、ID 设计（防遍历攻击）

### 核心原则
**数据库内部用自增 ID（性能），对外暴露 UUID（安全）。** 攻击者无法通过递增 ID 遍历所有数据。

### 强制规则

```python
# GOOD: ORM 模型同时有 id 和 uuid
import uuid as uuid_lib
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid_lib.uuid4()), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))


# GOOD: 路由用 UUID 查询
@router.get("/users/{user_uuid}", response_model=UserResponse)
async def get_user(user_uuid: str, service: UserService = Depends(get_user_service)):
    return await service.get_by_uuid(user_uuid)


# GOOD: Response Schema 只返回 uuid，不返回 id
class UserResponse(BaseModel):
    uuid: str
    name: str
    # 不暴露 id 字段


# BAD: 路由直接用自增 ID
@router.get("/users/{user_id}")
async def get_user(user_id: int): ...

# BAD: Response 暴露自增 ID
class UserResponse(BaseModel):
    id: int  # 攻击者可遍历 1,2,3...
```

### 违规检测
如果在路由路径中发现 `/{name}_id` 且类型为 `int`（如 `user_id: int`），必须提示用户改为 UUID。

## 二、密码安全

### 强制规则

```python
# GOOD: bcrypt 存储
from danweiyuan_eapi.security import hash_password, verify_password

hashed = hash_password("user_password")   # 存储到数据库
is_valid = verify_password("input", hashed)  # 验证时比对

# BAD: 明文存储
user.password = "123456"

# BAD: MD5/SHA 存储（可被彩虹表破解）
user.password = hashlib.md5(password.encode()).hexdigest()

# BAD: 接口返回密码字段
class UserResponse(BaseModel):
    id: int
    name: str
    password: str  # 绝对禁止
```

| 规则 | 说明 |
|------|------|
| 存储算法 | **只允许 bcrypt**（或 argon2），禁止 MD5/SHA/明文 |
| 接口返回 | **永远不返回**密码字段，Response Schema 中不包含 |
| 密码强度 | 用户密码最少 8 位，管理员密码最少 12 位 |
| 登录错误 | 返回"用户名或密码错误"，**不区分**是用户名不存在还是密码错误 |

## 三、接口认证与授权

### 强制规则

```python
# GOOD: 所有 API 必须 JWT 认证（白名单除外）
WHITELIST = ["/api/health", "/api/auth/login", "/api/auth/register"]

# GOOD: 路由级别认证
@router.get("/users", dependencies=[Depends(get_current_user)])
async def list_users(): ...

# GOOD: 角色检查
@router.delete("/users/{uuid}", dependencies=[Depends(require_admin)])
async def delete_user(uuid: str): ...

# BAD: 无认证的数据接口
@router.get("/users")
async def list_users(): ...
```

### Token 安全

| 规则 | 说明 |
|------|------|
| Access Token 有效期 | **30 分钟**（最长不超过 2 小时） |
| Refresh Token 有效期 | **7 天** |
| Token 黑名单 | 登出后 token 必须失效（Redis 存黑名单，TTL = 剩余有效期） |
| Token 存储 | 前端存 `localStorage`（SPA），**禁止**存 Cookie 不设 HttpOnly |
| Secret Key | 从环境变量读取，最少 32 位随机字符串 |

## 四、输入校验

### 强制规则

```python
# GOOD: Pydantic Schema 严格校验
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    age: int = Field(ge=0, le=150)

# GOOD: 列表查询参数限制
class ListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)  # 上限 100

# BAD: 不校验直接使用
@router.post("/users")
async def create_user(data: dict): ...

# BAD: page_size 无上限
class ListParams(BaseModel):
    page_size: int = 20  # 攻击者可传 999999
```

### 校验规则清单

| 字段类型 | 校验 |
|---------|------|
| 字符串 | `min_length` + `max_length` |
| 数字 | `ge` + `le`(最小值 + 最大值) |
| 邮箱 | `EmailStr` |
| 手机号 | `pattern=r"^1[3-9]\d{9}$"` |
| URL | `HttpUrl` |
| 列表 | `max_length`（限制数组长度） |
| 文件大小 | 后端二次校验（不信任前端） |

## 五、响应安全

### 强制规则

```python
# GOOD: Response Schema 严格控制返回字段
class UserResponse(BaseModel):
    uuid: str
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# BAD: 直接返回 ORM 对象
@router.get("/users/{uuid}")
async def get_user(uuid: str, db=Depends(get_db)):
    user = await db.get(User, uuid)
    return user  # 可能暴露 password、内部 ID 等

# GOOD: 列表接口必须分页
@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(params: PaginationParams = Depends()): ...

# BAD: 无分页返回全量数据
@router.get("/users")
async def list_users():
    return await db.execute(select(User))  # 全量泄露
```

### PII 脱敏

```python
# GOOD: 工具函数
def mask_phone(phone: str) -> str:
    """138****5678"""
    if len(phone) != 11:
        return phone
    return phone[:3] + "****" + phone[7:]

def mask_id_card(id_card: str) -> str:
    """420***********1234"""
    if len(id_card) != 18:
        return id_card
    return id_card[:3] + "***********" + id_card[14:]

# GOOD: 在 Response Schema 中使用 validator 脱敏
class UserResponse(BaseModel):
    phone: str

    @field_validator("phone", mode="before")
    @classmethod
    def mask_phone_field(cls, v: str) -> str:
        return mask_phone(v) if v else v
```

## 六、错误处理安全

### 强制规则

```python
# GOOD: 生产环境只返回通用错误
raise NotFoundError("用户")
raise BusinessError("操作失败")

# BAD: 回显用户输入
raise BusinessError(f"未找到: {user_input}")  # XSS/信息泄露

# BAD: 暴露内部错误
except Exception as e:
    return {"error": str(e)}  # 可能包含 SQL、文件路径、堆栈

# BAD: 暴露数据库结构
except IntegrityError as e:
    return {"error": f"数据库错误: {e}"}  # 暴露表名、字段名

# GOOD: 统一错误处理
except IntegrityError:
    raise BusinessError("数据冲突，请检查是否重复提交", code="CONFLICT")
```

### 生产环境禁止

| 禁止返回的内容 | 原因 |
|--------------|------|
| 完整异常堆栈 | 暴露代码结构和文件路径 |
| SQL 语句 | 暴露表结构和查询逻辑 |
| 文件系统路径 | 暴露服务器目录结构 |
| 用户输入回显 | XSS 和信息泄露 |
| 数据库字段名 | 暴露数据模型 |
| 第三方 API Key | 凭证泄露 |

## 七、注入防护

### SQL 注入

```python
# GOOD: ORM 参数化查询（安全）
result = await session.execute(select(User).where(User.id == user_id))

# GOOD: 原生 SQL 参数化（安全）
result = await session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})

# BAD: 字符串拼接（SQL 注入）
result = await session.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))
```

### 命令注入

```python
# BAD: shell 命令注入(禁止)
# 使用 os 模块的 system 调用执行用户输入拼接的命令 → 注入风险
# 使用 subprocess.run(... , shell=True) 执行用户输入拼接的字符串 → 注入风险

# GOOD: 参数列表（不经过 shell）
subprocess.run(["convert", safe_filename, "output.png"], shell=False)

# BEST: 不调用外部命令，用 Python 库
from PIL import Image
img = Image.open(safe_path)
```

### 路径遍历

```python
# BAD: 用户控制文件路径
file_path = f"/uploads/{user_input_filename}"

# GOOD: 安全提取文件名
from pathlib import Path
safe_name = Path(user_input_filename).name  # 去除 ../../../ 等
file_path = Path("/uploads") / safe_name
```

### SSRF（服务端请求伪造）

```python
# BAD: 用户控制 URL 发起请求
url = request_body.url  # 用户传入
response = await httpx.get(url)  # 可能访问内网 169.254.169.254

# GOOD: 白名单限制
ALLOWED_HOSTS = ["api.example.com", "cdn.example.com"]
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_HOSTS:
    raise BusinessError("不允许的目标地址")
```

## 八、软删除

### 强制规则

```python
# GOOD: 模型添加软删除字段
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

# GOOD: 删除操作只更新标记
async def delete_user(self, user_uuid: str) -> None:
    user = await self.get_by_uuid(user_uuid)
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    await self.db.commit()

# GOOD: 查询时自动排除已删除
async def list_users(self) -> list[User]:
    result = await self.db.execute(
        select(User).where(User.is_deleted == False)
    )
    return list(result.scalars().all())

# BAD: 物理删除
async def delete_user(self, user_id: int) -> None:
    user = await self.db.get(User, user_id)
    await self.db.delete(user)  # 数据永久丢失
    await self.db.commit()
```

### 例外
以下场景允许物理删除（但需用户确认）：
- 合规要求的数据清除（如 GDPR 被遗忘权）
- 临时数据清理（验证码、过期 session）

## 九、审计日志

### 强制规则

需要记录审计日志的操作：

| 操作 | 记录内容 |
|------|---------|
| 登录成功/失败 | 用户名、IP、时间、User-Agent |
| 权限变更 | 操作人、目标用户、旧角色、新角色 |
| 数据删除 | 操作人、删除的资源类型和 UUID |
| 敏感数据查询 | 查询人、查询条件（脱敏） |
| 密码修改 | 操作人、时间 |
| 导出操作 | 操作人、导出数据范围 |

```python
# GOOD: 审计日志示例
import logging

audit_logger = logging.getLogger("audit")

async def delete_user(self, user_uuid: str, operator: dict) -> None:
    user = await self.get_by_uuid(user_uuid)
    user.is_deleted = True
    await self.db.commit()

    audit_logger.info(
        "user_deleted operator=%s target=%s",
        operator["uuid"],
        user_uuid,
    )
```

## 十、PostgreSQL 安全

### 强制规则

| 规则 | 说明 |
|------|------|
| 参数化查询 | **禁止**字符串拼接 SQL，必须 ORM 或参数化 |
| 应用用户权限 | 应用数据库用户**只给** SELECT/INSERT/UPDATE/DELETE，**不给** DROP/CREATE/ALTER |
| 连接池限制 | `pool_size` 不超过 20，`max_overflow` 不超过 10 |
| SSL 连接 | 生产环境建议启用 SSL（`sslmode=require`） |
| 敏感字段加密 | 身份证号等字段使用 AES 加密存储，不只是展示时脱敏 |

### 应用用户权限配置
```sql
-- 创建应用专用用户（非超级用户）
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- 禁止给应用用户的权限
-- GRANT ALL PRIVILEGES
-- SUPERUSER
-- CREATEDB
-- CREATEROLE
```

## 十一、Redis 安全

### 强制规则

| 规则 | 说明 |
|------|------|
| 认证 | **必须设置密码**（`requirepass`），不允许无密码 Redis |
| 绑定地址 | `bind 127.0.0.1`，**禁止** `bind 0.0.0.0` |
| 危险命令 | **禁用** `FLUSHALL`/`FLUSHDB`/`CONFIG`/`KEYS`/`DEBUG` |
| Key TTL | 所有 key **必须设置过期时间**，禁止无 TTL 的 key |
| Key 前缀 | 所有 key 必须有项目前缀（如 `myapp:token:xxx`） |
| 存储内容 | **禁止**在 Redis 存储敏感原文（密码、身份证明文） |

### Redis 配置
```
# redis.conf
requirepass your_strong_password
bind 127.0.0.1
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Key 设计规范
```python
# GOOD: 有前缀、有 TTL
await redis.set("myapp:token:blacklist:abc123", "1", ex=3600)
await redis.set("myapp:cache:user:uuid123", json.dumps(user_data), ex=300)

# BAD: 无前缀
await redis.set("abc123", "1")

# BAD: 无 TTL
await redis.set("myapp:data:xxx", value)  # 永不过期，内存泄漏

# BAD: 存储敏感原文
await redis.set("myapp:user:password", "123456")
```

## 十二、MinIO / 文件存储安全

### 强制规则

| 规则 | 说明 |
|------|------|
| Bucket 访问 | **默认私有**，不开放 public 读 |
| 文件访问 | 通过**预签名 URL** 限时访问（默认 15 分钟） |
| 文件名 | **UUID 重命名**，禁止保留用户原始文件名做存储路径 |
| 文件类型 | 校验文件 **magic bytes**（不只检查扩展名） |
| 文件大小 | 后端二次校验大小限制（不信任前端或 Nginx） |

```python
# GOOD: UUID 重命名 + 预签名 URL
import uuid as uuid_lib
from minio import Minio

async def upload_file(file: UploadFile) -> str:
    # 校验文件类型（magic bytes）
    header = await file.read(8)
    await file.seek(0)
    if not is_allowed_file_type(header):
        raise BusinessError("不允许的文件类型")

    # UUID 重命名
    ext = Path(file.filename).suffix
    safe_name = f"{uuid_lib.uuid4()}{ext}"

    client.put_object("uploads", safe_name, file.file, file.size)
    return safe_name

def get_download_url(filename: str) -> str:
    # 预签名 URL，15 分钟有效
    return client.presigned_get_object("uploads", filename, expires=timedelta(minutes=15))


# BAD: 用户原始文件名
safe_name = file.filename  # 可能包含 ../../../etc/passwd

# BAD: 公开 bucket
client.set_bucket_policy("uploads", public_read_policy)

# BAD: 只检查扩展名
if file.filename.endswith(".jpg"):  # 攻击者可改扩展名
```

## 十三、DolphinDB 安全

### 强制规则

| 规则 | 说明 |
|------|------|
| 输入白名单 | 所有外部输入**必须经过正则白名单**验证后才能插入 DolphinDB 脚本 |
| 禁止拼接 | **禁止**将用户输入直接拼接到 DolphinDB 脚本字符串中 |
| 连接认证 | DolphinDB 连接**必须使用账号密码**，从环境变量读取 |
| 端口隔离 | DolphinDB 端口**禁止对外暴露**，仅 Docker 内部网络或 127.0.0.1 |

```python
# GOOD: 白名单验证后再插入脚本
import re

SAFE_COLUMN_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$')
SAFE_TABLE_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,63}$')

def validate_column_name(name: str) -> str:
    if not SAFE_COLUMN_NAME.match(name):
        raise BusinessError(f"非法字段名: {name}")
    return name

# 使用
col = validate_column_name(user_input_column)
script = f"select {col} from loadTable('dfs://mydb', 'mytable')"


# BAD: 直接拼接用户输入
script = f"select * from loadTable('dfs://mydb', '{user_input}')"  # DolphinDB 注入

# BAD: 无验证
factor_name = request.query_params.get("factor")
script = f"select * from factors where factor_name = '{factor_name}'"
```

### DolphinDB 连接安全
```python
# GOOD: 从环境变量读取
ddb_conn = ddb.Session()
ddb_conn.connect(
    host=settings.dolphindb_host,
    port=settings.dolphindb_port,
    userid=settings.dolphindb_user,
    password=settings.dolphindb_password,
)

# BAD: 硬编码
ddb_conn.connect("localhost", 8848, "admin", "123456")
```

## 十四、API 限流

### 强制规则

不同接口使用不同的限流策略：

| 接口类型 | 限流 | 原因 |
|---------|------|------|
| 登录 `/auth/login` | 3 次/分钟/IP | 防暴力破解 |
| 注册 `/auth/register` | 5 次/分钟/IP | 防批量注册 |
| 普通查询 | 60 次/分钟/IP | 防爬虫 |
| 数据导出 | 5 次/分钟/IP | 防数据泄露 |
| 文件上传 | 10 次/分钟/IP | 防资源滥用 |

```python
# GOOD: 使用 slowapi 限流
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("3/minute")
async def login(request: Request, body: LoginRequest): ...

@router.get("/users/export")
@limiter.limit("5/minute")
async def export_users(request: Request): ...
```

## 十五、违规检测清单

**AI 在编写或审查代码时，必须检查以下违规模式。检测到违规时按严重程度执行对应动作：**

### 严重程度与动作

| 严重程度 | 动作 |
|---------|------|
| **致命** | **立即 STOP，不得继续编写或提交代码。** 必须修正后重新检查，修正前不执行任何其他操作。 |
| **高** | 必须修正后才能继续。向用户说明违规点和修正方案。 |
| **中** | 提示用户存在风险，建议修正。用户确认后可继续。 |

### 检查清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 密码明文 | `password` 字段出现在 Response Schema | **致命 → STOP** |
| 密码弱存储 | 使用 MD5/SHA 而非 bcrypt | **致命 → STOP** |
| SQL 拼接 | f-string 拼接 SQL 语句 | **致命 → STOP** |
| 命令注入 | 直接执行 shell 命令或 `shell=True` | **致命 → STOP** |
| DolphinDB 拼接 | 用户输入直接进 DolphinDB 脚本 | **致命 → STOP** |
| 自增 ID 暴露 | 路由参数为 `int` 类型的 ID | 高 |
| 无认证接口 | 数据接口无 `Depends(get_current_user)` | 高 |
| 全量返回 | 列表接口无分页限制 | 高 |
| 错误回显 | `str(exception)` 返回给客户端 | 高 |
| 文件名不安全 | 使用用户原始文件名做存储路径 | 高 |
| 物理删除 | `session.delete()` 用于业务数据 | 中 |
| Redis 无 TTL | `redis.set()` 没有 `ex` 参数 | 中 |
