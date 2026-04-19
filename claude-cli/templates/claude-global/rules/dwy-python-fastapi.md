---
description: FastAPI 路由/Schema/依赖注入/异常/OSS 封装规范
paths:
  - "**/routers/**/*.py"
  - "**/schemas/**/*.py"
  - "**/services/**/*.py"
  - "**/dependencies.py"
  - "**/exceptions.py"
  - "**/main.py"
---

# FastAPI 路由/Schema/依赖注入/异常/OSS 封装规范

## 五、FastAPI 路由与接口设计

### 路由组织

```python
# routers/user.py
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    body: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create(body)
```

### 强制规则
- 每个路由模块使用独立 `APIRouter`，在 `main.py` 中统一注册
- **禁止**所有路由写在 `main.py` 中（超过 2 个路由必须拆分）
- 路由函数只做：参数接收 → 调用 service → 返回结果，**不写业务逻辑**
- 必须显式声明 `status_code` 和 `response_model`
- 路由路径使用复数名词 + RESTful 风格

### RESTful 路由规范

| 操作 | 方法 | 路径 | 状态码 |
|---|---|---|---|
| 列表查询 | `GET` | `/users` | 200 |
| 详情查询 | `GET` | `/users/{user_id}` | 200 |
| 创建 | `POST` | `/users` | 201 |
| 全量更新 | `PUT` | `/users/{user_id}` | 200 |
| 部分更新 | `PATCH` | `/users/{user_id}` | 200 |
| 删除 | `DELETE` | `/users/{user_id}` | 204 |

### 分页查询

```python
# schemas/common.py
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int

# routers/user.py
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    return await service.list(pagination)
```

## 六、Pydantic Schema 规范

### 强制规则
- 请求和响应使用不同的 Schema，**禁止**复用同一个 Model

```python
# schemas/user.py

class UserBase(BaseModel):
    """共享字段基类"""
    name: str = Field(max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """创建请求"""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """更新请求 - 所有字段可选"""
    name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None

class UserResponse(UserBase):
    """响应"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

- **禁止**在响应 Schema 中暴露密码、内部 ID、敏感字段
- 使用 `Field()` 添加校验约束（`min_length`、`ge`、`le`、`pattern` 等）
- 更新 Schema 的字段必须全部可选（`None` 默认值）

## 七、依赖注入

### 强制规则
- 数据库会话、当前用户、配置等通过 `Depends()` 注入
- **禁止**在路由函数中直接创建数据库会话或实例化 service

```python
# dependencies.py
from collections.abc import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await authenticate(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="认证失败")
    return user

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
```

```python
# ❌ 路由中直接创建会话
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    async with async_session_factory() as db:
        user = await db.get(User, user_id)
        return user

# ✅ 依赖注入
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.get_by_id(user_id)
```

## 八、异常处理

### 统一异常体系

直接使用 `dwyeapi` 提供的异常体系，禁止自造异常基类：

```python
# 从 eapi 导入（禁止自定义 AppError 子类体系）
from dwyeapi.exceptions import (
    AppError,               # 基类
    NotFoundError,          # 404 — NotFoundError("用户") → {"code": "NOT_FOUND", "message": "用户不存在"}
    BusinessError,          # 422 — BusinessError("余额不足", code="INSUFFICIENT_BALANCE")
    PermissionDeniedError,  # 403 — PermissionDeniedError()
    AuthenticationError,    # 401 — AuthenticationError()
    register_exception_handlers,  # 一次性注册全部 handler
)

# main.py 中注册
from dwyeapi.exceptions import register_exception_handlers
register_exception_handlers(app)
```

项目如需扩展异常，必须继承 `AppError`：

```python
# app/exceptions.py — 项目级异常（继承 eapi AppError）
from dwyeapi.exceptions import AppError

class QuotaExceededError(AppError):
    def __init__(self) -> None:
        super().__init__(message="配额已用尽", code="QUOTA_EXCEEDED")
```

### 强制规则
- **禁止**在 service 层抛出 `HTTPException`（service 不感知 HTTP）
- service 层抛出业务异常，由异常处理器统一转换为 HTTP 响应
- **禁止**裸 `except:` 或 `except Exception: pass`
- 错误响应格式统一为 `{"code": "ERROR_CODE", "message": "描述"}`
- **禁止**在错误消息中回显用户输入

```python
# ❌ service 中抛 HTTPException
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404)  # 耦合 HTTP
        return user

# ✅ service 中抛业务异常
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError("用户")
        return user
```

---

## OSS 规范（MinIO / S3 兼容）

### 核心原则

**代码只用 S3 协议，不用任何云厂商专有 API。** 通过环境变量切换 dev/prod 存储。

### 后端封装

```python
# services/oss.py
import boto3
from app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.oss_endpoint,       # dev: http://localhost:19000
        aws_access_key_id=settings.oss_access_key,
        aws_secret_access_key=settings.oss_secret_key,
    )

async def upload_file(key: str, data: bytes, content_type: str = "") -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.oss_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key

async def get_presigned_url(key: str, expires: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.oss_bucket, "Key": key},
        ExpiresIn=expires,
    )
```

### 环境变量

```bash
# .env.development（MinIO）
OSS_ENDPOINT=http://localhost:19000
OSS_ACCESS_KEY=minioadmin
OSS_SECRET_KEY=minioadmin
OSS_BUCKET=my-app

# .env.production（阿里云 OSS / AWS S3）
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY=your-key
OSS_SECRET_KEY=your-secret
OSS_BUCKET=my-app-prod
```

### 禁止事项

- 禁止使用 `minio` Python 库（用 `boto3`，S3 协议通用）
- 禁止代码中出现 MinIO / 阿里云 / AWS 等厂商名称判断逻辑
- 禁止硬编码 bucket 名、endpoint 地址
