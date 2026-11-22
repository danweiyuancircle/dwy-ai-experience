import runpy
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch


SCRIPT = (Path(__file__).resolve().parents[1]
          / "templates/ai-tools/skills/Apple/dwy-apple-local-debug/scripts/build_debug.py")
FUNCTIONS = runpy.run_path(str(SCRIPT))
GLOBALS = FUNCTIONS["install"].__globals__


class DebugBuildTests(unittest.TestCase):
    def test_second_running_install_blocks_update(self):
        installed = Path("/tmp/target/Example.app")
        running = {42: Path("/tmp/other/Example.app")}
        with patch.dict(GLOBALS, {"running_apps": lambda bundle_id: running}):
            with self.assertRaisesRegex(RuntimeError, "其他应用实例"):
                FUNCTIONS["stop_installed"](installed, "com.example.fixture")

    def test_failed_launch_restores_previous_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed, candidate = root / "ADBox.app", root / "Bundle"
            for path, marker in [(installed, "old"), (candidate, "new")]:
                path.mkdir()
                (path / "marker").write_text(marker)

            with patch.dict(
                GLOBALS, {"stop_installed": lambda app, bundle_id: None}
            ), patch.object(GLOBALS["subprocess"], "run", side_effect=RuntimeError("启动失败")):
                with self.assertRaisesRegex(RuntimeError, "启动失败"):
                    FUNCTIONS["install"](candidate, installed, "com.example.fixture")
            self.assertEqual((installed / "marker").read_text(), "old")

    def test_backup_verifies_uncheckpointed_wal_without_modifying_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, backup = root / "source", root / "backup"
            source.mkdir()
            connect = sqlite3.connect
            with closing(connect(source / "devices.sqlite")) as database:
                database.execute("PRAGMA journal_mode=WAL")
                database.execute("CREATE TABLE devices(id)")
                database.execute("INSERT INTO devices VALUES (1)")
                database.commit()
                FUNCTIONS["command"]("/usr/bin/ditto", source, backup)

                def connect_and_check(*args, **kwargs):
                    copied = connect(*args, **kwargs)
                    self.assertEqual(copied.execute("SELECT id FROM devices").fetchall(), [(1,)])
                    return copied

                with patch.object(sqlite3, "connect", side_effect=connect_and_check):
                    FUNCTIONS["verify_backup"](source, backup)
                FUNCTIONS["verify_backup"](source, backup)
                (backup / "extra").touch()
                with self.assertRaisesRegex(RuntimeError, "不一致"):
                    FUNCTIONS["verify_backup"](source, backup)

    def test_multiple_data_sources_only_replace_last_backup_after_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data, prefs, state = root / "AppData", root / "account.plist", root / "state"
            data.mkdir()
            prefs.write_bytes(b"previous")
            state.mkdir()
            with patch.dict(GLOBALS, {"running_apps": lambda bundle_id: {}}):
                FUNCTIONS["backup_data"]([data, prefs], state, "com.example.fixture")
            snapshot = state / "Data/2-account.plist"
            self.assertEqual(snapshot.read_bytes(), b"previous")
            prefs.write_bytes(b"current")
            with patch.dict(GLOBALS, {"running_apps": lambda bundle_id: {42: root / "Example.app"}}):
                with self.assertRaisesRegex(RuntimeError, "备份期间"):
                    FUNCTIONS["backup_data"]([data, prefs], state, "com.example.fixture")
            self.assertEqual(snapshot.read_bytes(), b"previous")


if __name__ == "__main__":
    unittest.main()
