"""基于 loguru 的全局日志,支持按天 + 按大小轮转,并可拦截 stdlib logging。

对外暴露一组生命周期 API(``configure`` / ``get_logger`` / ``close``),
与 ``cache.py`` 保持一致的模式:应用启动阶段调用一次 ``configure``,关闭阶段调用 ``close``。

特性:
    * 彩色控制台输出(stderr)。
    * 文件输出按天滚动(``{filename}_YYYY-MM-DD.log``),同时支持单文件大小上限,
      两个条件任一触发即滚动。
    * 自动清理过期日志(默认保留 30 天)。
    * 可选 JSON 序列化,便于日志聚合系统解析。
    * 可选拦截标准 ``logging`` 模块,让 uvicorn、SQLAlchemy 等三方库共享同一套输出 sink。
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
    """把标准 ``logging`` 记录转发到 loguru sink 链路的拦截 Handler。"""

    def emit(self, record: logging.LogRecord) -> None:
        """转发 stdlib 记录到 loguru,保留原始 level、异常信息以及调用栈深度。"""
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
    """构造 loguru ``rotation`` 回调,按日期变更或大小超限触发滚动。

    Args:
        max_bytes: 单文件最大字节数,超出后新开文件。

    Returns:
        符合 loguru ``rotation`` 协议的回调函数。
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
    """配置全局日志,应用启动时调用一次即可。

    Args:
        level: 最低日志级别(``DEBUG``/``INFO``/``WARNING``/``ERROR``/``CRITICAL``)。
        log_dir: 日志文件目录,``None`` 表示关闭文件输出。
        filename: 文件基础名,最终文件形如 ``{filename}_YYYY-MM-DD.log``。
        max_bytes: 单文件大小上限(字节),默认 100 MB。
        retention: loguru 保留策略(``"30 days"``、``"1 week"``、整数个数等)。
        console: 是否输出带颜色的日志到 stderr。
        console_format: 自定义控制台格式字符串。
        file_format: 自定义文件格式字符串。
        serialize: 文件 sink 是否按 JSON Lines 序列化,便于日志聚合系统使用。
        enqueue: 是否通过队列异步写入,非阻塞且多进程安全。
        intercept_stdlib: 是否把 stdlib ``logging`` 的日志重定向到 loguru。
        intercept_loggers: 拦截时限定的 logger 名前缀(如 ``["uvicorn", "sqlalchemy"]``),
            ``None`` 表示拦截 root logger(捕获全部)。
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
    """把 stdlib logger 的 handlers 替换为 ``_InterceptHandler``,并记住原始 handlers 以便恢复。"""
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
    """移除全部 handlers、恢复 stdlib logger 原状并 flush 未落盘日志。

    可重复调用,调用后可再次 ``configure`` 重新装配。
    """
    for handler_id in _handler_ids:
        # Handler 已被移除的情况为正常情形,忽略即可。
        with contextlib.suppress(ValueError):
            _logger.remove(handler_id)
    _handler_ids.clear()

    for name, original_handlers in _intercept_state.items():
        stdlib_logger = logging.getLogger(name) if name else logging.root
        stdlib_logger.handlers = original_handlers
        stdlib_logger.propagate = True
    _intercept_state.clear()
