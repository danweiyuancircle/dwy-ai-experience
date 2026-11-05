"""仅依赖标准库的固定延迟异步执行;任务生命周期由宿主管理。"""

import asyncio
from collections.abc import Awaitable, Callable
from math import isfinite

__all__ = ["run_periodic"]


async def run_periodic(
    callback: Callable[[], Awaitable[None]],
    *,
    interval_seconds: float,
    run_immediately: bool = True,
) -> None:
    """顺序执行回调,每轮完成后再等待指定间隔,不创建额外任务。

    Args:
        callback: 无必填参数的异步函数;可恢复异常须由业务处理,其他异常原样传播并停止循环。
        interval_seconds: 正数且有限的等待秒数,例如 600;不是按墙钟对齐的执行频率。
        run_immediately: 是否立即执行第一轮;False 表示先等待一个间隔。

    Raises:
        ValueError: 间隔非正数或非有限值,且不会执行业务回调。
        asyncio.CancelledError: 宿主取消时原样传播,包括回调执行期间;回调不得吞掉取消。

    宿主应通过 asyncio.create_task 保留句柄、监测异常,关闭时取消并等待退出。
    本函数不提供跨进程互斥;资金等业务仍须使用自己的数据库锁和幂等机制。
    """
    if not isfinite(interval_seconds) or interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive and finite")
    if not run_immediately:
        await asyncio.sleep(interval_seconds)
    while True:
        await callback()
        await asyncio.sleep(interval_seconds)
