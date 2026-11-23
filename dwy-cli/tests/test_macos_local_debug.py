import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = (Path(__file__).resolve().parents[1]
          / "templates/ai-tools/skills/Apple/dwy-apple-local-debug/scripts/build_debug.py")
FUNCTIONS = runpy.run_path(str(SCRIPT))
GLOBALS = FUNCTIONS["install"].__globals__


class DebugBuildTests(unittest.TestCase):
    def test_detects_indexed_rollback_and_registered_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            installed = root / "Example.app"
            rollback = root / "Example.previous"
            archive = root / "Archive.noindex/Example.app"
            for app in (installed, rollback, archive):
                app.mkdir(parents=True)
            with patch.dict(GLOBALS, {
                "command": lambda *args, **kwargs: SimpleNamespace(
                    stdout=f"{installed}\0{rollback}\0{root / 'removed.app'}\0"
                ),
                "registered_apps": lambda bundle_id: {installed, archive},
            }):
                with self.assertRaises(RuntimeError) as error:
                    FUNCTIONS["check_visible_copies"]("com.example.fixture", {installed})
                self.assertIn(str(rollback), str(error.exception))
                self.assertIn(str(archive), str(error.exception))
                self.assertNotIn("removed.app", str(error.exception))

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

    def test_install_accepts_build_command_without_data_arguments(self):
        args = ["build_debug.py", "--app", "Example.app", "--bundle-id", "com.example.fixture",
                "--team-id", "ABC123", "--product", "build/Example.app", "--", "xcodebuild", "build"]
        installs = []
        with patch.object(sys, "argv", args), patch.dict(GLOBALS, {"build_and_install": installs.append}):
            self.assertEqual(FUNCTIONS["main"](), 0)
        self.assertEqual([install.build for install in installs], [["xcodebuild", "build"]])


if __name__ == "__main__":
    unittest.main()
