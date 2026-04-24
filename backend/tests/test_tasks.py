"""Tests for dwyeapi.tasks module."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dwyeapi.database import Base
from dwyeapi.tasks.model import Task, TaskStatus
from dwyeapi.tasks.registry import TaskRegistry
from dwyeapi.tasks.schema import TaskCreate, TaskResponse
from dwyeapi.tasks.service import (
    append_task_log,
    create_task,
    get_task,
    list_tasks,
    update_task_progress,
    update_task_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def engine():
    """Create an in-memory SQLite async engine for testing."""
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session_factory(engine):
    """Create an async session factory bound to the test engine."""
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(session_factory) -> AsyncSession:
    """Yield a database session for a single test."""
    async with session_factory() as s:
        yield s


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestTaskModel:
    """Tests for the Task ORM model."""

    async def test_task_has_default_id(self, session):
        """Task should auto-generate an ID when created."""
        task = Task(task_type="test", params={"key": "value"})
        session.add(task)
        await session.commit()
        await session.refresh(task)
        assert task.id.startswith("task_")
        assert len(task.id) == 37  # "task_" + 32 hex chars

    async def test_task_default_status_is_pending(self, session):
        """Default status should be PENDING."""
        task = Task(task_type="test", params={})
        session.add(task)
        await session.commit()
        await session.refresh(task)
        assert task.status == TaskStatus.PENDING

    async def test_task_default_progress_is_zero(self, session):
        """Default progress should be 0."""
        task = Task(task_type="test", params={})
        session.add(task)
        await session.commit()
        await session.refresh(task)
        assert task.progress == 0

    async def test_task_default_result_is_none(self, session):
        """Default result should be None."""
        task = Task(task_type="test", params={})
        session.add(task)
        await session.commit()
        await session.refresh(task)
        assert task.result is None

    async def test_task_stores_params_as_json(self, session):
        """Params should be stored and retrieved as a dict."""
        params = {"file": "data.csv", "count": 100}
        task = Task(task_type="test", params=params)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        assert task.params == params


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_status_values(self):
        """All expected status values should exist."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.SUCCESS == "success"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELED == "canceled"

    def test_status_is_str_compatible(self):
        """TaskStatus values should be usable as strings."""
        assert f"status={TaskStatus.RUNNING}" == "status=running"


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchemas:
    """Tests for Pydantic task schemas."""

    def test_task_create_valid(self):
        """TaskCreate should accept valid input."""
        tc = TaskCreate(task_type="export", params={"format": "csv"})
        assert tc.task_type == "export"
        assert tc.params == {"format": "csv"}

    async def test_task_response_from_attributes(self, session):
        """TaskResponse should be constructible from a persisted Task ORM object."""
        task = Task(
            id="task_abc123",
            task_type="test",
            params={"key": "value"},
            status=TaskStatus.SUCCESS,
            progress=100,
            logs="done",
            result={"ok": True},
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)  # populates server-side defaults (timestamps)

        resp = TaskResponse.model_validate(task)
        assert resp.id == "task_abc123"
        assert resp.status == TaskStatus.SUCCESS
        assert resp.progress == 100

    def test_task_page_response(self):
        """ApiResponse.page wraps tasks into PageData envelope."""
        from dwyeapi.response import ApiResponse, PageData

        resp = ApiResponse.page(items=[], total=0, page=1, page_size=20)
        assert isinstance(resp.data, PageData)
        assert resp.data.items == []
        assert resp.data.total == 0
        assert resp.data.page == 1
        assert resp.data.page_size == 20


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------


class TestServiceCreateTask:
    """Tests for create_task service function."""

    async def test_create_task_returns_task_with_id(self, session):
        """Created task should have a generated ID."""
        task_in = TaskCreate(task_type="process_data", params={"file": "a.csv"})
        task = await create_task(session, task_in)
        assert task.id.startswith("task_")
        assert task.task_type == "process_data"
        assert task.status == TaskStatus.PENDING

    async def test_create_task_persists_to_db(self, session):
        """Created task should be retrievable from the database."""
        task_in = TaskCreate(task_type="export", params={})
        task = await create_task(session, task_in)

        result = await session.execute(select(Task).where(Task.id == task.id))
        db_task = result.scalar_one()
        assert db_task.task_type == "export"

    async def test_create_task_has_initial_log(self, session):
        """Created task should have an initial log entry."""
        task_in = TaskCreate(task_type="test", params={})
        task = await create_task(session, task_in)
        assert "任务已创建" in task.logs


class TestServiceGetTask:
    """Tests for get_task service function."""

    async def test_get_existing_task(self, session):
        """Should return the task when it exists."""
        task_in = TaskCreate(task_type="test", params={})
        created = await create_task(session, task_in)
        found = await get_task(session, created.id)
        assert found is not None
        assert found.id == created.id

    async def test_get_nonexistent_task_returns_none(self, session):
        """Should return None for unknown task ID."""
        found = await get_task(session, "task_does_not_exist")
        assert found is None


class TestServiceListTasks:
    """Tests for list_tasks service function."""

    async def test_list_tasks_empty(self, session):
        """Should return empty list when no tasks exist."""
        items, total = await list_tasks(session)
        assert items == []
        assert total == 0

    async def test_list_tasks_returns_all(self, session):
        """Should return all tasks."""
        for i in range(3):
            await create_task(session, TaskCreate(task_type=f"type_{i}", params={}))
        items, total = await list_tasks(session)
        assert total == 3
        assert len(items) == 3

    async def test_list_tasks_pagination(self, session):
        """Should respect page and page_size."""
        for i in range(5):
            await create_task(session, TaskCreate(task_type="test", params={}))
        items, total = await list_tasks(session, page=1, page_size=2)
        assert total == 5
        assert len(items) == 2

    async def test_list_tasks_filter_by_status(self, session):
        """Should filter by status."""
        task_in = TaskCreate(task_type="test", params={})
        t1 = await create_task(session, task_in)
        await create_task(session, task_in)

        await update_task_status(session, t1.id, TaskStatus.RUNNING)

        items, total = await list_tasks(session, status=TaskStatus.RUNNING)
        assert total == 1
        assert items[0].id == t1.id

    async def test_list_tasks_filter_by_task_type(self, session):
        """Should filter by task_type."""
        await create_task(session, TaskCreate(task_type="alpha", params={}))
        await create_task(session, TaskCreate(task_type="beta", params={}))

        items, total = await list_tasks(session, task_type="alpha")
        assert total == 1
        assert items[0].task_type == "alpha"


class TestServiceUpdateStatus:
    """Tests for update_task_status service function."""

    async def test_update_status(self, session):
        """Should update the task status."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await update_task_status(session, task.id, TaskStatus.RUNNING)

        updated = await get_task(session, task.id)
        assert updated.status == TaskStatus.RUNNING

    async def test_update_status_with_result(self, session):
        """Should update status and result together."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await update_task_status(session, task.id, TaskStatus.SUCCESS, result={"ok": True})

        updated = await get_task(session, task.id)
        assert updated.status == TaskStatus.SUCCESS
        assert updated.result == {"ok": True}

    async def test_update_nonexistent_task_is_noop(self, session):
        """Updating a non-existent task should not raise."""
        await update_task_status(session, "task_nope", TaskStatus.FAILED)


class TestServiceUpdateProgress:
    """Tests for update_task_progress service function."""

    async def test_update_progress(self, session):
        """Should update the progress value."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await update_task_progress(session, task.id, 50)

        updated = await get_task(session, task.id)
        assert updated.progress == 50

    async def test_progress_clamped_to_100(self, session):
        """Progress above 100 should be clamped to 100."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await update_task_progress(session, task.id, 150)

        updated = await get_task(session, task.id)
        assert updated.progress == 100

    async def test_progress_clamped_to_0(self, session):
        """Progress below 0 should be clamped to 0."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await update_task_progress(session, task.id, -10)

        updated = await get_task(session, task.id)
        assert updated.progress == 0


class TestServiceAppendLog:
    """Tests for append_task_log service function."""

    async def test_append_log(self, session):
        """Should append a timestamped log entry."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await append_task_log(session, task.id, "step 1 done")

        updated = await get_task(session, task.id)
        assert "step 1 done" in updated.logs

    async def test_append_multiple_logs(self, session):
        """Should preserve all log entries in order."""
        task = await create_task(session, TaskCreate(task_type="test", params={}))
        await append_task_log(session, task.id, "first")
        await append_task_log(session, task.id, "second")

        updated = await get_task(session, task.id)
        assert "first" in updated.logs
        assert "second" in updated.logs
        assert updated.logs.index("first") < updated.logs.index("second")


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestTaskRegistry:
    """Tests for the task registry."""

    def test_register_and_get(self):
        """Registered function should be retrievable."""
        reg = TaskRegistry()

        @reg.register("my_task")
        async def my_task(ctx, params):
            pass

        assert reg.get("my_task") is my_task

    def test_get_unregistered_returns_none(self):
        """Unregistered task type should return None."""
        reg = TaskRegistry()
        assert reg.get("nonexistent") is None

    def test_list_types(self):
        """Should list all registered types sorted."""
        reg = TaskRegistry()

        @reg.register("beta")
        async def beta(ctx, params):
            pass

        @reg.register("alpha")
        async def alpha(ctx, params):
            pass

        assert reg.list_types() == ["alpha", "beta"]

    def test_has(self):
        """has() should return True for registered types."""
        reg = TaskRegistry()

        @reg.register("exists")
        async def exists(ctx, params):
            pass

        assert reg.has("exists") is True
        assert reg.has("nope") is False

    def test_duplicate_registration_raises(self):
        """Registering the same task_type twice should raise ValueError."""
        reg = TaskRegistry()

        @reg.register("dup")
        async def first(ctx, params):
            pass

        with pytest.raises(ValueError, match="already registered"):

            @reg.register("dup")
            async def second(ctx, params):
                pass


# ---------------------------------------------------------------------------
# Pool tests
# ---------------------------------------------------------------------------


class TestPool:
    """Tests for the ARQ pool management module."""

    def test_parse_redis_url(self):
        """Should parse a standard redis:// URL."""
        from dwyeapi.tasks.pool import _parse_redis_url

        settings = _parse_redis_url("redis://myhost:6380/2")
        assert settings.host == "myhost"
        assert settings.port == 6380
        assert settings.database == 2

    def test_parse_redis_url_with_password(self):
        """Should extract password from URL."""
        from dwyeapi.tasks.pool import _parse_redis_url

        settings = _parse_redis_url("redis://:secret@localhost:6379/0")
        assert settings.password == "secret"

    def test_parse_redis_url_defaults(self):
        """Should use defaults for minimal URL."""
        from dwyeapi.tasks.pool import _parse_redis_url

        settings = _parse_redis_url("redis://localhost")
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.database == 0

    def test_get_redis_settings_raises_without_configure(self):
        """Should raise RuntimeError if configure() was not called."""
        from dwyeapi.tasks import pool

        # Reset module state
        pool._redis_settings = None
        with pytest.raises(RuntimeError, match="not configured"):
            pool.get_redis_settings()

    def test_configure_stores_settings(self):
        """configure() should store parsed settings."""
        from dwyeapi.tasks import pool

        pool.configure("redis://testhost:6380/3")
        settings = pool.get_redis_settings()
        assert settings.host == "testhost"
        assert settings.port == 6380
        assert settings.database == 3

        # Cleanup
        pool._redis_settings = None


# ---------------------------------------------------------------------------
# Worker factory tests
# ---------------------------------------------------------------------------


class TestWorkerFactory:
    """Tests for create_worker_settings factory."""

    def test_creates_worker_settings_class(self, monkeypatch):
        """Should return a class with ARQ-compatible attributes."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "test")

        from dwyeapi.config import BaseSettings
        from dwyeapi.tasks.worker import create_worker_settings

        settings = BaseSettings()
        ws = create_worker_settings(settings)

        assert hasattr(ws, "functions")
        assert hasattr(ws, "max_jobs")
        assert hasattr(ws, "job_timeout")
        assert hasattr(ws, "redis_settings")
        assert ws.max_jobs == 5
        assert ws.job_timeout == 3600

    def test_respects_custom_settings(self, monkeypatch):
        """Should use task_* values from BaseSettings."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "test")
        monkeypatch.setenv("TASK_MAX_JOBS", "10")
        monkeypatch.setenv("TASK_JOB_TIMEOUT", "7200")

        from dwyeapi.config import BaseSettings
        from dwyeapi.tasks.worker import create_worker_settings

        settings = BaseSettings()
        ws = create_worker_settings(settings)

        assert ws.max_jobs == 10
        assert ws.job_timeout == 7200


# ---------------------------------------------------------------------------
# Config integration tests
# ---------------------------------------------------------------------------


class TestConfigTaskFields:
    """Tests for task_* fields in BaseSettings."""

    def test_task_fields_have_defaults(self, monkeypatch):
        """task_* fields should have sensible defaults."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "test")

        from dwyeapi.config import BaseSettings

        s = BaseSettings()
        assert s.task_max_jobs == 5
        assert s.task_job_timeout == 3600
        assert s.task_failure_ttl == 86400

    def test_task_fields_from_env(self, monkeypatch):
        """task_* fields should be overridable from env."""
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "test")
        monkeypatch.setenv("TASK_MAX_JOBS", "8")
        monkeypatch.setenv("TASK_JOB_TIMEOUT", "1800")
        monkeypatch.setenv("TASK_FAILURE_TTL", "43200")

        from dwyeapi.config import BaseSettings

        s = BaseSettings()
        assert s.task_max_jobs == 8
        assert s.task_job_timeout == 1800
        assert s.task_failure_ttl == 43200
