"""生成真实 iOS/macOS 模板，防止新项目继续绑定旧仓库或本机来源路径。"""
import subprocess
import tempfile
import unittest
from pathlib import Path

APPLE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/danweiyuancircle/dwy-ai-experience.git"


class TemplateSmokeTests(unittest.TestCase):
    """覆盖生成结果中的远端身份、版本及占位符替换，不执行真实 OAuth。"""

    def check_platform(self, platform, skeleton_root=None):
        """各平台生成到临时目录，读取实际输出以避免只检查模板文本。"""
        with tempfile.TemporaryDirectory(prefix="apple-template-smoke-") as folder:
            name = "MigrationIOS" if platform == "ios" else "MigrationMac"
            arguments = [
                "bash", str(APPLE_ROOT / "scripts/new-app.sh"), "--platform", platform,
                "--name", name, "--bundle-id", "com.example.migration", "--output", folder,
            ]
            if skeleton_root is not None:
                arguments += ["--skeleton", str(skeleton_root)]
            result = subprocess.run(arguments, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = Path(folder) / name
            manifest = (output / "Package.swift").read_text()
            project = (output / "project.yml").read_text()
            self.assertIn(REPOSITORY_URL, manifest)
            self.assertIn(REPOSITORY_URL, project)
            self.assertIn('from: "0.4.0"', manifest)
            self.assertIn("from: 0.4.0", project)
            self.assertIn('package: "dwy-ai-experience"', manifest)
            self.assertTrue((output / (name + "Tests") / "SmokeTests.swift").is_file())
            for path in output.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text()
                for stale in ["apple-app-kit", "/ios-arc", "__SKELETON_PATH__", "__APP_NAME__", "__BUNDLE_ID__", "__TEAM_ID__", "__PACKAGE_URL__", "__PACKAGE_VERSION__", "__PACKAGE_ID__"]:
                    self.assertNotIn(stale, text, str(path))

    def test_ios_template_uses_private_versioned_package(self):
        """iOS 生成物通过统一私有包 URL 按 0.4.0 版本引用。"""
        self.check_platform("ios")

    def test_macos_template_uses_private_versioned_package(self):
        """macOS 生成物通过统一私有包 URL 按 0.4.0 版本引用。"""
        self.check_platform("macos")

    def test_repository_root_override_locates_templates(self):
        """保留 --skeleton 的仓库根目录语义，兼容统一仓库的 apple 子目录。"""
        self.check_platform("ios", APPLE_ROOT.parent)


if __name__ == "__main__":
    unittest.main()
