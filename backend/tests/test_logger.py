"""Tests for dwyeapi.logger."""

import io
import logging
import sys
from datetime import date
from pathlib import Path

import pytest

from dwyeapi import logger as logger_mod


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset the global logger state between tests."""
    yield
    logger_mod.close()


class TestConfigureConsole:
    """configure() with console-only output."""

    def test_console_only_does_not_create_file(self, tmp_path: Path) -> None:
        logger_mod.configure(level="INFO", console=True, log_dir=None)
        log = logger_mod.get_logger("demo")
        log.info("hello")

        assert not any(tmp_path.iterdir())

    def test_console_writes_to_stderr_by_default(self, capsys: pytest.CaptureFixture[str]) -> None:
        logger_mod.configure(level="INFO", log_dir=None, console=True, enqueue=False)
        logger_mod.get_logger().info("hello-stderr")

        captured = capsys.readouterr()
        assert "hello-stderr" in (captured.err + captured.out)


class TestConfigureFile:
    """configure() with file output + rotation."""

    def test_writes_dated_file(self, tmp_path: Path) -> None:
        logger_mod.configure(
            level="INFO",
            log_dir=tmp_path,
            filename="app",
            console=False,
            enqueue=False,
        )
        logger_mod.get_logger("demo").info("file-output-line")
        logger_mod.close()  # flush

        today_str = date.today().isoformat()
        matches = list(tmp_path.glob(f"app_{today_str}*.log"))
        assert matches, f"expected app_{today_str}*.log in {list(tmp_path.iterdir())}"
        content = matches[0].read_text(encoding="utf-8")
        assert "file-output-line" in content

    def test_rotation_by_size_creates_multiple_files(self, tmp_path: Path) -> None:
        logger_mod.configure(
            level="INFO",
            log_dir=tmp_path,
            filename="app",
            max_bytes=1024,  # 1KB, trigger fast
            console=False,
            enqueue=False,
        )
        log = logger_mod.get_logger()
        for i in range(200):
            log.info("line-%d-%s", i, "x" * 50)
        logger_mod.close()

        files = sorted(tmp_path.glob("app_*.log"))
        assert len(files) >= 2, f"expected rotation to produce 2+ files, got {files}"


class TestGetLogger:
    """get_logger() binding behaviour."""

    def test_get_logger_with_name_binds_module_field(self, tmp_path: Path) -> None:
        logger_mod.configure(
            level="INFO",
            log_dir=tmp_path,
            filename="bind",
            console=False,
            enqueue=False,
            file_format="{extra[module]} | {message}",
        )
        logger_mod.get_logger("user_service").info("login")
        logger_mod.close()

        files = list(tmp_path.glob("bind_*.log"))
        assert files
        content = files[0].read_text(encoding="utf-8")
        assert "user_service" in content
        assert "login" in content

    def test_get_logger_without_name_returns_root(self) -> None:
        logger_mod.configure(console=True, log_dir=None, enqueue=False)
        assert logger_mod.get_logger() is not None


class TestInterceptStdlib:
    """Standard logging is intercepted into eapi logger."""

    def test_stdlib_logger_reaches_file(self, tmp_path: Path) -> None:
        logger_mod.configure(
            level="INFO",
            log_dir=tmp_path,
            filename="intercept",
            console=False,
            enqueue=False,
            intercept_stdlib=True,
        )
        logging.getLogger("some.third_party").info("from-stdlib")
        logger_mod.close()

        files = list(tmp_path.glob("intercept_*.log"))
        assert files
        content = files[0].read_text(encoding="utf-8")
        assert "from-stdlib" in content


class TestCloseAndReconfigure:
    """close() releases handlers and allows re-configure."""

    def test_close_then_configure_works(self, tmp_path: Path) -> None:
        logger_mod.configure(console=True, log_dir=None, enqueue=False)
        logger_mod.close()

        logger_mod.configure(log_dir=tmp_path, filename="re", console=False, enqueue=False)
        logger_mod.get_logger().info("after-reconfigure")
        logger_mod.close()

        files = list(tmp_path.glob("re_*.log"))
        assert files
        assert "after-reconfigure" in files[0].read_text(encoding="utf-8")
