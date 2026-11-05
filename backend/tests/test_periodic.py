"""固定延迟循环的业务边界与取消行为;不连接外部服务。"""

import asyncio
import os
import subprocess
import sys
from unittest.mock import AsyncMock

import pytest

from dwyeapi import periodic


@pytest.mark.parametrize("interval", [0, -1, float("nan"), float("inf"), -float("inf")])
async def test_invalid_interval_does_not_execute_callback(interval):
    callback = AsyncMock()
    with pytest.raises(ValueError, match="positive and finite"):
        await periodic.run_periodic(callback, interval_seconds=interval)
    callback.assert_not_awaited()


@pytest.mark.parametrize("run_immediately", [True, False])
async def test_first_execution_and_fixed_delay_order(monkeypatch, run_immediately):
    events = []

    async def callback():
        events.append("callback")

    async def sleep(delay):
        events.append(delay)
        if len(events) >= 3:
            raise asyncio.CancelledError

    monkeypatch.setattr(periodic.asyncio, "sleep", sleep)
    with pytest.raises(asyncio.CancelledError):
        await periodic.run_periodic(callback, interval_seconds=600, run_immediately=run_immediately)
    assert events == (["callback", 600, "callback", 600] if run_immediately else [600, "callback", 600])


async def test_callback_finishes_before_waiting_or_starting_next_iteration(monkeypatch):
    entered, release, waiting = asyncio.Event(), asyncio.Event(), asyncio.Event()
    events = []

    async def callback():
        events.append("started")
        entered.set()
        await release.wait()
        events.append("finished")

    async def sleep(delay):
        assert delay == 600
        events.append("waiting")
        waiting.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(periodic.asyncio, "sleep", sleep)
    task = asyncio.create_task(periodic.run_periodic(callback, interval_seconds=600))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        assert events == ["started"]
        release.set()
        await asyncio.wait_for(waiting.wait(), 1)
        assert events == ["started", "finished", "waiting"]
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


async def test_cancelling_while_waiting_stops_the_loop():
    called = asyncio.Event()
    callback = AsyncMock(side_effect=called.set)
    task = asyncio.create_task(periodic.run_periodic(callback, interval_seconds=600))
    await asyncio.wait_for(called.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert task.cancelled()
    callback.assert_awaited_once()


async def test_cancelling_during_callback_runs_its_cleanup():
    entered, cleaned = asyncio.Event(), asyncio.Event()

    async def callback():
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaned.set()

    task = asyncio.create_task(periodic.run_periodic(callback, interval_seconds=600))
    await asyncio.wait_for(entered.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cleaned.is_set() and task.cancelled()


async def test_unexpected_failure_stops_and_remains_available_to_host():
    error = RuntimeError("isolated unexpected failure")
    callback = AsyncMock(side_effect=error)
    task = asyncio.create_task(periodic.run_periodic(callback, interval_seconds=600))
    with pytest.raises(RuntimeError, match="isolated unexpected failure"):
        await task
    assert task.exception() is error
    callback.assert_awaited_once()


def test_base_import_needs_neither_tasks_extra_nor_service_configuration():
    env = {key: value for key, value in os.environ.items() if key not in {"DATABASE_URL", "REDIS_URL", "SECRET_KEY"}}
    result = subprocess.run(
        [sys.executable, "-c", "from dwyeapi.periodic import run_periodic; import sys; "
         "assert callable(run_periodic); assert 'arq' not in sys.modules; "
         "assert 'dwyeapi.tasks' not in sys.modules"],
        env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
