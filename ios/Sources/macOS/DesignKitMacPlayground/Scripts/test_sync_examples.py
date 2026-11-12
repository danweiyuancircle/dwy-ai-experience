"""验证发布版本元数据失配会被同源检查拒绝，不修改真实资源。"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PlaygroundMetadataTests(unittest.TestCase):
    def test_check_rejects_stale_bilingual_package_versions(self):
        for language in ("en", "zh-Hans"):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "Playground"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("__pycache__"))
                document = root / "Resources/Documentation" / language / "button.md"
                source = document.read_text()
                package_line = next(line for line in source.splitlines() if line.startswith("Package: "))
                document.write_text(source.replace(package_line, "Package: 0.0.0-stale"))
                script = root / "Scripts/sync-examples.py"
                # 即使先重建 Index，错误版本仍须独立于同源内容比较被拒绝。
                subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
                result = subprocess.run([sys.executable, str(script), "--check"], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"Resources/Documentation/{language}/button.md: Package version must match", result.stdout)
                self.assertNotIn("\nResources/Index.md\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
