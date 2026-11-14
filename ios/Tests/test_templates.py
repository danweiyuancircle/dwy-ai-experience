"""生成真实 iOS/macOS 模板，防止新项目继续绑定旧仓库或本机来源路径。"""
import subprocess
import plistlib
import tempfile
import unittest
from pathlib import Path

IOS_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/danweiyuancircle/dwy-ai-experience.git"


class TemplateSmokeTests(unittest.TestCase):
    """覆盖生成结果中的远端身份、版本及占位符替换，不执行真实 OAuth。"""

    def check_platform(self, platform, skeleton_root=None):
        """各平台生成到临时目录，读取实际输出以避免只检查模板文本。"""
        with tempfile.TemporaryDirectory(prefix="ios-template-smoke-") as folder:
            name = "MigrationIOS" if platform == "ios" else "MigrationMac"
            arguments = [
                "bash", str(IOS_ROOT / "scripts/new-app.sh"), "--platform", platform,
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
            version = "0.8.0-beta.4" if platform == "ios" else "0.4.1"
            self.assertIn(f'exact: "{version}"', manifest)
            self.assertIn(f"exactVersion: {version}", project)
            self.assertIn('package: "dwy-ai-experience"', manifest)
            self.assertIn('.macOS("26.0")', manifest)
            if platform == "macos":
                self.assertIn('macOS: "26.0"', project)
                self.assertIn('MACOSX_DEPLOYMENT_TARGET: "26.0"', project)
                self.assertIn('LSMinimumSystemVersion: "26.0"', project)
                self.assertEqual(project.count('ARCHS: arm64'), 2)
                with (output / "App/Info.plist").open("rb") as plist:
                    self.assertEqual(plistlib.load(plist)["LSMinimumSystemVersion"], "26.0")
                self.assertNotIn("EXCLUDED_ARCHS", project)
                self.assertNotIn("ONLY_ACTIVE_ARCH", project)
            else:
                self.assertIn('.iOS(.v18)', manifest)
                self.assertIn('iOS: "18.0"', project)
                self.assertIn('IPHONEOS_DEPLOYMENT_TARGET: "18.0"', project)
                app = (output / f"App/{name}App.swift").read_text()
                settings = (output / "Features/Settings/SettingsView.swift").read_text()
                self.assertIn(".eControlTheme(.standard)", app)
                self.assertIn("EButton(", settings)
                self.assertIn("ESwitch(", settings)
                boundary = ["python3", "-B", "-m", "unittest", "discover", "-s", "Tests", "-p", "test_ui_boundary.py"]
                check = subprocess.run(boundary, cwd=output, capture_output=True, text=True)
                self.assertEqual(check.returncode, 0, check.stderr)
                # 在临时生成物中注入三类越界，防止检查器始终返回成功。
                source = output / "Features/Settings/SettingsView.swift"
                source.write_text(settings + "\nimport DesignKitMac\n// .glassEffect is documentation only\nlet illegal = Color.clear.glassEffect()\n")
                (output / "project.yml").write_text(project.replace(f"exactVersion: {version}", "exactVersion: 0.0.0"))
                rejected = subprocess.run(boundary, cwd=output, capture_output=True, text=True)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("FAILED (failures=3)", rejected.stderr)
                source.write_text(settings)
                (output / "project.yml").write_text(project)
            self.assertTrue((output / (name + "Tests") / "SmokeTests.swift").is_file())
            for path in output.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text()
                for stale in ["apple-app-kit", "/ios-arc", "__SKELETON_PATH__", "__APP_NAME__", "__BUNDLE_ID__", "__TEAM_ID__", "__PACKAGE_URL__", "__PACKAGE_VERSION__", "__PACKAGE_ID__"]:
                    self.assertNotIn(stale, text, str(path))

    def test_ios_template_uses_versioned_components(self):
        """iOS 新项目真实使用已发布组件，并能拒绝平台、材质和版本越界。"""
        self.check_platform("ios")

    def test_macos_template_uses_private_versioned_package(self):
        """macOS 生成物通过统一私有包 URL 按 0.4.1 版本引用。"""
        self.check_platform("macos")

    def test_repository_root_override_locates_templates(self):
        """保留 --skeleton 的仓库根目录语义，从统一仓库的 ios 子目录读取模板。"""
        self.check_platform("ios", IOS_ROOT.parent)


if __name__ == "__main__":
    unittest.main()
