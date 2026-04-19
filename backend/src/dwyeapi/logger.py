"""Loguru-based global logger with daily + size rotation and stdlib interception.

Exposes a single lifecycle API (``configure``/``get_logger``/``close``) that mirrors
the pattern used by ``cache.py``. A typical application calls ``configure`` once at
startup (from ``lifespan``) and ``close`` once at shutdown.

Features:
    * Colored console output (stderr).
    * File output with daily rollover (``{filename}_YYYY-MM-DD.log``) and a
      configurable per-file size ceiling — whichever triggers first.
    * Old log retention (default 30 days) with automatic cleanup.
    * Optional JSON serialization for log aggregators.
    * Optional interception of the standard ``logging`` module so libraries like
      uvicorn, SQLAlchemy and third-party packages route through the same sinks.
"""

from __future__ import annotations

import contextlib
import inspect
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger as _logger

if TYPE_CHECKING:
    from loguru import Record


_DEFAULT_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[module]}</cyan> - <level>{message}</level>"
)
_DEFAULT_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[module]} | {name}:{function}:{line} - {message}"
)
_DEFAULT_EXTRA: dict[str, Any] = {"module": "-"}


_handler_ids: list[int] = []
_intercept_state: dict[str, list[logging.Handler]] = {}


class Logger:
    """dwyeapi 日志门面,遵循 stdlib ``logging.Logger`` 语义。

    - 消息用 ``%s`` / ``%d`` 等 stdlib 占位符,位置参数延迟格式化
    - 支持 ``exc_info=True`` 记录当前异常堆栈
    - 底层可为 loguru / stdlib logging / structlog,调用方无感知
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        """保存底层日志对象。

        Args:
            impl: 真正执行日志调用的底层对象。当前由 :func:`get_logger`
                注入 loguru logger,需支持 ``opt(exception=...)`` 与
                ``debug`` / ``info`` / ``warning`` / ``error`` /
                ``critical`` 方法。
        """
        self._impl = impl

    def _emit(self, level: str, msg: str, args: tuple[Any, ...], exc_info: bool) -> None:
        """格式化消息并转发到底层实现。

        Args:
            level: 日志级别方法名(``debug``/``info``/``warning``/
                ``error``/``critical``)。
            msg: 日志消息模板,支持 stdlib ``%`` 占位符。
            args: 用于 ``%``-格式化的位置参数;为空时保留 ``msg`` 原样。
            exc_info: 是否附带当前异常堆栈。
        """
        try:
            formatted = msg % args if args else msg
        except (TypeError, ValueError):
            formatted = f"{msg} args={args!r}"
        target = self._impl.opt(exception=True) if exc_info else self._impl
        getattr(target, level)(formatted)

    def debug(self, msg: str, *args: Any, exc_info: bool = False, **_: Any) -> None:
        """记录 DEBUG 级别日志。"""
        self._emit("debug", msg, args, exc_info)

    def info(self, msg: str, *args: Any, exc_info: bool = False, **_: Any) -> None:
        """记录 INFO 级别日志。"""
        self._emit("info", msg, args, exc_info)

    def warning(self, msg: str, *args: Any, exc_info: bool = False, **_: Any) -> None:
        """记录 WARNING 级别日志。"""
        self._emit("warning", msg, args, exc_info)

    def error(self, msg: str, *args: Any, exc_info: bool = False, **_: Any) -> None:
        """记录 ERROR 级别日志。"""
        self._emit("error", msg, args, exc_info)

    def exception(self, msg: str, *args: Any, **_: Any) -> None:
        """记录 ERROR 级别日志并自动附带当前异常堆栈。"""
        self._emit("error", msg, args, exc_info=True)

    def critical(self, msg: str, *args: Any, exc_info: bool = False, **_: Any) -> None:
        """记录 CRITICAL 级别日志。"""
        self._emit("critical", msg, args, exc_info)


class _InterceptHandler(logging.Handler):
    """Route standard ``logging`` records into the loguru sink chain."""

    def emit(self, record: logging.LogRecord) -> None:
        """Forward a stdlib record to loguru preserving level, exception and frame depth."""
        try:
            level: str | int = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = inspect.currentframe()
        depth = 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _make_rotator(max_bytes: int) -> Any:
    """Build a loguru ``rotation`` callable that rolls on date change or size cap.

    Args:
        max_bytes: Maximum bytes per file before a new file is created.

    Returns:
        A function matching the loguru ``rotation`` callable signature.
    """
    state: dict[str, date | None] = {"date": None}

    def _rotate(message: Record, file: Any) -> bool:
        today = datetime.now().date()
        if state["date"] is None:
            state["date"] = today
            return False
        if today != state["date"]:
            state["date"] = today
            return True
        return file.tell() + len(str(message)) > max_bytes

    return _rotate


def configure(
    *,
    level: str = "INFO",
    log_dir: str | Path | None = None,
    filename: str = "app",
    max_bytes: int = 100 * 1024 * 1024,
    retention: str | int = "30 days",
    console: bool = True,
    console_format: str | None = None,
    file_format: str | None = None,
    serialize: bool = False,
    enqueue: bool = True,
    intercept_stdlib: bool = True,
    intercept_loggers: list[str] | None = None,
) -> None:
    """Configure the global logger. Call once at application startup.

    Args:
        level: Minimum log level (``DEBUG``/``INFO``/``WARNING``/``ERROR``/``CRITICAL``).
        log_dir: Directory for log files. ``None`` disables file output.
        filename: Base filename; final files look like ``{filename}_YYYY-MM-DD.log``.
        max_bytes: Per-file size cap before rotation (default 100 MB).
        retention: Loguru retention spec (``"30 days"``, ``"1 week"``, int count, ...).
        console: Whether to write colored logs to stderr.
        console_format: Override for the console format string.
        file_format: Override for the file format string.
        serialize: Emit JSON lines to the file sink for log aggregators.
        enqueue: Write asynchronously via a queue — non-blocking and multi-process safe.
        intercept_stdlib: Route stdlib ``logging`` records through loguru.
        intercept_loggers: When intercepting, scope to these logger name prefixes
            (e.g. ``["uvicorn", "sqlalchemy"]``). ``None`` means root (catch-all).
    """
    close()

    _logger.configure(extra=_DEFAULT_EXTRA)

    if console:
        handler_id = _logger.add(
            sys.stderr,
            level=level,
            format=console_format or _DEFAULT_CONSOLE_FORMAT,
            colorize=True,
            enqueue=enqueue,
            backtrace=True,
            diagnose=False,
        )
        _handler_ids.append(handler_id)

    if log_dir is not None:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_sink = str(log_path / f"{filename}_{{time:YYYY-MM-DD}}.log")
        handler_id = _logger.add(
            file_sink,
            level=level,
            format=file_format or _DEFAULT_FILE_FORMAT,
            rotation=_make_rotator(max_bytes),
            retention=retention,
            encoding="utf-8",
            enqueue=enqueue,
            serialize=serialize,
            backtrace=True,
            diagnose=False,
        )
        _handler_ids.append(handler_id)

    if intercept_stdlib:
        _install_stdlib_intercept(level, intercept_loggers)


def _install_stdlib_intercept(level: str, targets: list[str] | None) -> None:
    """Replace handlers on stdlib loggers with ``_InterceptHandler``, remembering originals."""
    handler = _InterceptHandler()
    roots = targets or [""]

    for name in roots:
        stdlib_logger = logging.getLogger(name) if name else logging.root
        _intercept_state[name] = list(stdlib_logger.handlers)
        stdlib_logger.handlers = [handler]
        stdlib_logger.setLevel(level)
        stdlib_logger.propagate = False


def get_logger(name: str | None = None) -> Logger:
    """返回 dwyeapi ``Logger`` 门面,可选绑定模块名。

    Args:
        name: 记录到 ``module`` extra 字段的逻辑模块名。

    Returns:
        ``Logger`` 门面实例。底层当前使用 loguru,但此细节对调用方
        不可见,以便后续替换为其他日志库(stdlib logging /
        structlog 等)时无需改动调用点。
    """
    impl = _logger.bind(module=name) if name else _logger
    return Logger(impl)


def close() -> None:
    """Remove all handlers, restore stdlib loggers, and flush pending records.

    Safe to call repeatedly. After ``close`` the module can be reconfigured.
    """
    for handler_id in _handler_ids:
        # Handler already removed — benign.
        with contextlib.suppress(ValueError):
            _logger.remove(handler_id)
    _handler_ids.clear()

    for name, original_handlers in _intercept_state.items():
        stdlib_logger = logging.getLogger(name) if name else logging.root
        stdlib_logger.handlers = original_handlers
        stdlib_logger.propagate = True
    _intercept_state.clear()
