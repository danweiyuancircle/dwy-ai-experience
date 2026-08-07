# dwyeapi Tasks 集成指南

基于 ARQ 的全异步耗时任务处理系统。开箱即用，3 步接入。

## 1. 安装

```bash
pip install dwyeapi[tasks]
# 或
uv add "dwyeapi[tasks]"
```

自动安装 `arq` 异步任务队列依赖。需要运行中的 Redis 实例。

## 2. 快速接入

### 第一步：写任务函数

```python
# app/tasks.py
from dwyeapi.tasks import register, TaskContext


@register("process_data")
async def process_data(ctx: TaskContext, params: dict):
    """数据处理任务。"""
    file_path = params["file"]
    await ctx.log(f"开始处理文件: {file_path}")

    async with ctx.db() as session:
        # 查询数据库
        result = await session.execute(select(RawData).where(...))
        rows = result.scalars().all()

    for i, row in enumerate(rows):
        # 业务处理...
        await ctx.update_progress(int((i + 1) / len(rows) * 100))

        if await ctx.is_cancelled():
            await ctx.log("用户取消, 已停止")
            return

    return {"processed": len(rows)}


@register("export_file")
async def export_file(ctx: TaskContext, params: dict):
    """文件导出任务。"""
    await ctx.log("开始导出")
    # ... 业务逻辑 ...
    return {"file_url": "/files/report.csv"}
```

### 第二步：FastAPI 接入

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dwyeapi.database import create_async_engine_factory, create_session_factory
from dwyeapi.exceptions import register_exception_handlers
from dwyeapi.tasks import setup_tasks, task_router

from app.config import settings

import app.tasks  # noqa: 触发 @register 装饰器

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_tasks(app, settings, session_factory)
    yield


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(task_router)  # 挂载 /tasks API
```

### 第三步：启动 Worker

```python
# app/worker.py
from dwyeapi.database import create_async_engine_factory, create_session_factory
from dwyeapi.tasks import create_worker_settings

from app.config import settings

import app.tasks  # noqa: 触发 @register 装饰器

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)
WorkerSettings = create_worker_settings(settings, session_factory=session_factory)
```

```bash
# 终端 1: FastAPI
uvicorn app.main:app --reload

# 终端 2: Worker
arq app.worker.WorkerSettings

# 终端 3 (可选): Redis
redis-server
```

## 3. .env 配置

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# 任务模块配置 (均有默认值, 可不配)
TASK_MAX_JOBS=5           # Worker 最大并发任务数 (默认 5)
TASK_JOB_TIMEOUT=3600     # 单个任务超时秒数 (默认 3600)
TASK_FAILURE_TTL=86400    # 失败任务在 Redis 中保留秒数 (默认 86400)
```

## 4. API 接口

挂载 `task_router` 后自动获得以下接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/tasks` | 提交任务 |
| GET | `/tasks/{task_id}` | 查询单个任务状态 |
| GET | `/tasks` | 任务列表 (分页 + 筛选) |
| POST | `/tasks/{task_id}/cancel` | 取消任务 |

### 提交任务

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type": "process_data", "params": {"file": "data.csv"}}'
```

```json
{
  "code": "SUCCESS",
  "message": "success",
  "data": {
    "id": "task_a1b2c3d4...",
    "task_type": "process_data",
    "status": "pending",
    "progress": 0,
    "logs": "[2026-04-05 10:00:00] 任务已创建, 等待执行\n",
    "result": null,
    "params": {"file": "data.csv"},
    "created_at": "2026-04-05T10:00:00",
    "updated_at": "2026-04-05T10:00:00"
  },
  "timestamp": 1775000000
}
```

### 查询状态 (轮询)

```bash
curl http://localhost:8000/tasks/task_a1b2c3d4...
```

`status` 会从 `pending` → `running` → `success`/`failed`/`canceled` 变化，`progress` 从 0 递增到 100。

### 任务列表

```bash
# 分页 + 状态筛选
curl "http://localhost:8000/tasks?page=1&page_size=20&status=running"

# 按类型筛选
curl "http://localhost:8000/tasks?task_type=process_data"
```

### 取消任务

```bash
curl -X POST http://localhost:8000/tasks/task_a1b2c3d4.../cancel
```

仅 `pending` 和 `running` 状态的任务可取消。已结束的任务抛 `BusinessError`，HTTP **422**（`TASK_ALREADY_FINISHED`）。

### 自定义路由前缀

```python
app.include_router(task_router, prefix="/api/jobs")  # /api/jobs/*
```

## 5. TaskContext API

任务函数收到的 `ctx` 对象，提供以下方法：

| 方法 | 签名 | 说明 |
|------|------|------|
| ctx.log | `async (message: str) -> None` | 追加带时间戳的日志 |
| ctx.update_progress | `async (value: int, message: str = "") -> None` | 更新进度 0-100, 可选附日志 |
| ctx.is_cancelled | `async () -> bool` | 检查是否被取消 (读 Redis 标记) |
| ctx.db | `() -> AsyncContextManager[AsyncSession]` | 获取数据库 session |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| ctx.task_id | str | 当前任务唯一 ID |
| ctx.task_type | str | 任务类型 |
| ctx.params | dict | 提交时的入参 |

### 生命周期 (框架自动管理)

```
任务入队
  → 状态设为 RUNNING + 记日志 "任务开始执行"
    → 调用业务函数 func(ctx, params)
      → 正常返回 dict → 状态设为 SUCCESS, result = 返回值, progress = 100
      → 抛异常       → 状态设为 FAILED, result = {"error": "..."}
      → 取消退出     → 状态设为 CANCELED
```

业务代码**不需要**手动管理 RUNNING/SUCCESS/FAILED 状态转换。

## 6. 任务注册

### @register 装饰器

```python
from dwyeapi.tasks import register, TaskContext

@register("unique_task_type")
async def my_task(ctx: TaskContext, params: dict):
    ...
```

- `task_type` 全局唯一，重复注册抛 `ValueError`
- 必须是 `async def`
- 签名固定为 `(ctx: TaskContext, params: dict)`
- 返回 `dict` 或 `None`

### 确保装饰器被执行

任务模块必须被导入才能触发 `@register`：

```python
# main.py 和 worker.py 中都要加
import app.tasks  # noqa
```

## 7. 任务取消机制

协作式取消 — 框架设置 Redis 标记，任务函数自行检查并退出。

```python
@register("batch_import")
async def batch_import(ctx: TaskContext, params: dict):
    for batch in batches:
        # 每批处理前检查
        if await ctx.is_cancelled():
            await ctx.log("用户取消, 已导入到第 N 批")
            return  # 框架自动设为 CANCELED

        await process_batch(batch)
        await ctx.update_progress(...)
```

**注意：** 取消不会回滚已执行的操作。已插入的数据不会被撤销。如需回滚，在检测到取消后执行自定义清理逻辑。

## 8. 任务状态

| 状态 | 值 | 说明 |
|------|------|------|
| PENDING | `"pending"` | 已创建, 等待 Worker 执行 |
| RUNNING | `"running"` | 正在执行中 |
| SUCCESS | `"success"` | 执行成功 |
| FAILED | `"failed"` | 执行失败 (异常) |
| CANCELED | `"canceled"` | 已取消 |

终态：SUCCESS / FAILED / CANCELED，不可再变更。

## 9. Task 数据模型

Task 表自动随业务数据库创建 (复用 eapi 的 `Base`)。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(64) | 主键, 自动生成 `task_{uuid}` |
| task_type | String(50) | 任务类型, 有索引 |
| status | Enum(TaskStatus) | 任务状态 |
| params | JSON | 提交时的入参 |
| result | JSON, nullable | 执行结果 |
| progress | Integer | 进度 0-100 |
| logs | Text | 带时间戳的执行日志 |
| created_at | DateTime | 创建时间 (TimestampMixin) |
| updated_at | DateTime | 更新时间 (TimestampMixin) |

## 10. Worker 配置

### create_worker_settings

从 eapi 的 `BaseSettings` 自动生成 ARQ Worker 配置：

```python
from dwyeapi.tasks import create_worker_settings

WorkerSettings = create_worker_settings(settings, session_factory=session_factory)
```

自动映射：
- `settings.redis_url` → ARQ `RedisSettings`
- `settings.task_max_jobs` → `max_jobs` (默认 5)
- `settings.task_job_timeout` → `job_timeout` (默认 3600s)

### 并发控制

```env
# 单 Worker, 5 个协程并发
TASK_MAX_JOBS=5

# 多 Worker 实例: 总并发 = max_jobs x Worker 数
# 终端 1: arq app.worker.WorkerSettings
# 终端 2: arq app.worker.WorkerSettings
# 总并发 = 5 + 5 = 10
```

IO 密集型任务 (文件导出、第三方 API) 可设 5-10；CPU 密集型任务 (AI 推理) 建议等于 CPU 核心数。

## 11. 公共 API 速查

```python
from dwyeapi.tasks import (
    setup_tasks,              # 一站式初始化
    task_router,              # 开箱即用 APIRouter
    register,                 # @register 装饰器
    TaskContext,              # 任务上下文类型
    TaskStatus,               # 状态枚举
    create_worker_settings,   # Worker 工厂
)
```

| 导出项 | 用途 |
|--------|------|
| `setup_tasks(app, settings, session_factory)` | lifespan 中调用, 初始化 ARQ pool |
| `task_router` | APIRouter, include_router 挂载 |
| `register(task_type)` | 装饰器, 注册异步任务函数 |
| `TaskContext` | 任务函数第一个参数的类型 |
| `TaskStatus` | 枚举: PENDING/RUNNING/SUCCESS/FAILED/CANCELED |
| `create_worker_settings(settings, session_factory)` | 生成 ARQ WorkerSettings 类 |

## 12. 完整最小示例

```
myproject/
├── app/
│   ├── config.py       # Settings(BaseSettings)
│   ├── main.py         # FastAPI + setup_tasks + task_router
│   ├── tasks.py        # @register 任务函数
│   └── worker.py       # WorkerSettings
├── .env
└── pyproject.toml
```

```toml
# pyproject.toml
[project]
dependencies = ["dwyeapi[tasks]", "asyncpg"]
```

```env
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

```bash
# 启动
uvicorn app.main:app --reload   # API
arq app.worker.WorkerSettings   # Worker

# 测试
curl -X POST http://localhost:8000/tasks \
  -d '{"task_type": "process_data", "params": {"file": "test.csv"}}'
```
