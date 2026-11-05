# 固定间隔异步任务

`dwyeapi.periodic.run_periodic` 只使用 Python 标准库，不加载 ARQ，不需要数据库、Redis 或服务配置。基础安装 `dwyeapi` 即可使用；它适合定期核对、清理、刷新等轻量进程内任务。

## 行为

- 默认启动即执行；传 `run_immediately=False` 则先等待一个间隔。
- 等待从上一轮完成后开始计算，不重叠执行同一循环，不按墙钟对齐。
- `interval_seconds` 必须为正数且有限；无效值在业务调用前抛出 `ValueError`。
- 未处理异常原样传播并终止循环。宿主必须保留任务句柄、记录异常并按自身健康检查策略告警；可恢复的业务异常应在业务回调内处理。
- 取消可以打断等待和正在执行的异步回调；业务应在 `finally` 中释放资源，不得吞掉取消异常。
- 每个进程各自执行；涉及支付等状态修改时，继续使用业务数据库锁与幂等机制。

## 纯 asyncio

```python
import asyncio
from contextlib import suppress

from dwyeapi.periodic import run_periodic


async def refresh_once() -> None:
    """一次业务执行，不包含无限循环。"""
    print("refresh")


async def main() -> None:
    task = asyncio.create_task(
        run_periodic(refresh_once, interval_seconds=600), name="refresh"
    )
    try:
        await task
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    asyncio.run(main())
```

## FastAPI lifespan

```python
import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from dwyeapi.periodic import run_periodic


async def refresh_once() -> None:
    """业务自行创建短生命周期资源，并处理可恢复的异常。"""
    print("refresh")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(
        run_periodic(refresh_once, interval_seconds=600), name="refresh"
    )
    # 健康检查可以读取句柄；done 且非正常取消时，应及时上报告警。
    app.state.refresh_task = task
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(lifespan=lifespan)
```

这是宿主进程中的周期执行能力。若需要 Cron 日历调度、持久队列或独立 Worker，使用对应调度器或现有 `dwyeapi.tasks`，不将这些机制加入本模块。
