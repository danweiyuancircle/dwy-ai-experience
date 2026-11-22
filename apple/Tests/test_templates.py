"""通过真实生成物验证单端、双端四层结构及安全追加平台。"""
import os
import plistlib
import subprocess
import tempfile
import unittest
from pathlib import Path

APPLE_ROOT = Path(__file__).resolve().parents[1]


class TemplateSmokeTests(unittest.TestCase):
    """生成到临时目录，不改实际应用、全局配置或远端发布版本。"""

    def generate(self, folder, platform, *extra, name="MigrationApp", bundle="com.example.migration"):
        return subprocess.run([
            "bash", str(APPLE_ROOT / "scripts/new-app.sh"), "--platform", platform,
            "--name", name, "--bundle-id", bundle, "--output", str(folder), *extra,
        ], capture_output=True, text=True)

    def run_boundary(self, root):
        return subprocess.run([
            "python3", "-B", "-m", "unittest", "discover", "-s", "Tests", "-p", "test_ui_boundary.py",
        ], cwd=root, capture_output=True, text=True)

    def check_platform(self, platform, *extra):
        with tempfile.TemporaryDirectory(prefix="apple-template-") as folder:
            result = self.generate(folder, platform, *extra)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = Path(folder) / "MigrationApp"
            core = output / "packages/MigrationAppCore"
            self.assertTrue((core / "Package.swift").is_file())
            manifest = (core / "Package.swift").read_text()
            self.assertIn("https://github.com/danweiyuancircle/dwy-ai-experience.git", manifest)
            self.assertIn('exact: "0.12.0"', manifest)
            self.assertTrue((core / "Sources/BizFoundation/AppConfig.swift").is_file())
            self.assertTrue((core / "Tests/BizFoundationTests/BizFoundationTests.swift").is_file())
            self.assertTrue((output / "scripts/check-architecture.py").is_file())
            self.assertTrue((output / "AGENTS.md").is_file())
            self.assertFalse((output / "Foundation").exists())
            platforms = ("ios", "macos") if platform == "apple" else (platform,)
            for current in ("ios", "macos"):
                self.assertEqual((output / current).exists(), current in platforms)
            for current in platforms:
                root = output / current
                project = (root / "project.yml").read_text()
                self.assertIn("path: ../packages/MigrationAppCore", project)
                self.assertIn("product: BizFoundation", project)
                self.assertIn("exactVersion: 0.12.0", project)
                self.assertIn("- path: BusinessUI", project)
                self.assertTrue((root / "BusinessUI/README.md").is_file())
                self.assertFalse((root / "BizFoundation").exists())
                self.assertFalse((root / "Foundation").exists())
                self.assertFalse((root / "Package.swift").exists())
                self.assertTrue((root / "MigrationAppTests/SmokeTests.swift").is_file())
                bundle = "com.example.migration" + (f".{current}" if platform == "apple" else "")
                self.assertIn(f"PRODUCT_BUNDLE_IDENTIFIER: {bundle}\n", project)
                if current == "macos":
                    self.assertEqual(project.count("ARCHS: arm64"), 2)
                    self.assertIn('MACOSX_DEPLOYMENT_TARGET: "26.0"', project)
                    home = (root / "App/RootView.swift").read_text()
                    self.assertIn("@Environment(\\.eControlTheme)", home)
                    self.assertIn(".background(controlTheme.colors.background)", home)
                    self.assertIn(".font(controlTheme.typography.pageTitle)", home)
                    self.assertIn(".eControlTheme(.standard)", (root / "App/MigrationAppApp.swift").read_text())
                    with (root / "App/Info.plist").open("rb") as stream:
                        self.assertEqual(plistlib.load(stream)["LSMinimumSystemVersion"], "26.0")
                else:
                    self.assertIn('IPHONEOS_DEPLOYMENT_TARGET: "18.0"', project)
                    settings = (root / "Features/Settings/SettingsView.swift").read_text()
                    self.assertIn("EButton(", settings)
                    self.assertIn("ESwitch(", settings)
                    boundary = self.run_boundary(root)
                    self.assertEqual(boundary.returncode, 0, boundary.stderr)
                self.assertIn(".eControlTheme(", (root / "App/MigrationAppApp.swift").read_text())
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertNotRegex(path.read_text(), r"__(?:APP_NAME|BUNDLE_ID|TEAM_ID|PACKAGE_URL|PACKAGE_VERSION|PACKAGE_ID)__", str(path))
            if platform == "apple":
                self.assertTrue((output / "MigrationApp.xcworkspace/contents.xcworkspacedata").is_file())

    def test_ios_template_uses_four_layers(self):
        self.check_platform("ios")

    def test_macos_template_uses_four_layers(self):
        self.check_platform("macos")

    def test_apple_template_shares_one_business_core(self):
        self.check_platform("apple")

    def test_repository_root_override_locates_templates(self):
        self.check_platform("ios", "--skeleton", str(APPLE_ROOT.parent))

    def test_add_platform_preserves_existing_sources_and_version(self):
        for first, added in (("ios", "macos"), ("macos", "ios")):
            with self.subTest(first=first), tempfile.TemporaryDirectory(prefix="apple-add-") as folder:
                self.assertEqual(self.generate(folder, first).returncode, 0)
                output = Path(folder) / "MigrationApp"
                manifest = output / "packages/MigrationAppCore/Package.swift"
                self.assertTrue(manifest.is_file())
                manifest.write_text(manifest.read_text().replace('exact: "0.12.0"', 'exact: "0.8.0-beta.6"'))
                project = output / first / "project.yml"
                project.write_text(project.read_text().replace("exactVersion: 0.12.0", "exactVersion: 0.8.0-beta.6"))
                marker = output / first / "App/Keep.swift"
                marker.write_text("// existing project work\n")
                before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
                result = self.generate(folder, added, "--add-platform", bundle=f"com.example.migration.{added}")
                self.assertEqual(result.returncode, 0, result.stderr)
                for path, data in before.items():
                    self.assertEqual((output / path).read_bytes(), data, str(path))
                self.assertIn("exactVersion: 0.8.0-beta.6", (output / added / "project.yml").read_text())
                repeated = self.generate(folder, added, "--add-platform", bundle=f"com.example.migration.{added}")
                self.assertNotEqual(repeated.returncode, 0)

    def test_rejects_invalid_arguments_and_existing_destinations(self):
        with tempfile.TemporaryDirectory(prefix="apple-invalid-") as folder:
            for platform, extra, name, bundle in (
                ("watchos", (), "Demo", "com.example.demo"),
                ("ios", (), "bad-name", "com.example.demo"),
                ("ios", (), "class", "com.example.demo"),
                ("ios", (), "_", "com.example.demo"),
                ("ios", (), "Demo", 'com.example."broken'),
                ("ios", ("--team-id", 'bad"team'), "Demo", "com.example.demo"),
                ("apple", ("--add-platform",), "Missing", "com.example.demo"),
                ("ios", ("--add-platform",), "Missing", "com.example.demo"),
            ):
                with self.subTest(platform=platform, extra=extra, name=name, bundle=bundle):
                    self.assertNotEqual(self.generate(folder, platform, *extra, name=name, bundle=bundle).returncode, 0)
            self.assertEqual(list(Path(folder).iterdir()), [])
            output = Path(folder) / "MigrationApp"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("keep")
            self.assertNotEqual(self.generate(folder, "ios").returncode, 0)
            self.assertEqual(marker.read_text(), "keep")
            broken = Path(folder) / "Broken"
            broken.symlink_to(Path(folder) / "missing")
            self.assertNotEqual(self.generate(folder, "ios", name="Broken").returncode, 0)
            self.assertTrue(broken.is_symlink())
            missing = subprocess.run(["bash", str(APPLE_ROOT / "scripts/new-app.sh"), "--name"], capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)

    def test_add_platform_rejects_existing_version_disagreement(self):
        with tempfile.TemporaryDirectory(prefix="apple-add-conflict-") as folder:
            self.assertEqual(self.generate(folder, "ios").returncode, 0)
            output = Path(folder) / "MigrationApp"
            project = output / "ios/project.yml"
            project.write_text(project.read_text().replace("exactVersion: 0.12.0", "exactVersion: 0.8.0-beta.6"))
            result = self.generate(folder, "macos", "--add-platform", bundle="com.example.migration.macos")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((output / "macos").exists())

    def test_ui_boundary_allows_only_registered_business_material(self):
        with tempfile.TemporaryDirectory(prefix="apple-ui-boundary-") as folder:
            self.assertEqual(self.generate(folder, "ios").returncode, 0)
            root = Path(folder) / "MigrationApp/ios"
            business = root / "BusinessUI/ConnectionIndicator.swift"
            business.write_text("import SwiftUI\nlet indicator = Color.clear.glassEffect()\n")
            self.assertNotEqual(self.run_boundary(root).returncode, 0)
            checker = root / "Tests/test_ui_boundary.py"
            checker.write_text(checker.read_text().replace(
                "BUSINESS_MATERIAL_SOURCES = ()",
                'BUSINESS_MATERIAL_SOURCES = ("BusinessUI/ConnectionIndicator.swift",)',
            ))
            self.assertEqual(self.run_boundary(root).returncode, 0)
            business.write_text(business.read_text() + "import DesignKitMac\n")
            self.assertNotEqual(self.run_boundary(root).returncode, 0)
            business.write_text("import SwiftUI\n")
            source = root / "Features/Settings/SettingsView.swift"
            source.write_text(source.read_text() + "\nlet illegal = Color.clear.glassEffect()\n")
            checker.write_text(checker.read_text().replace(
                'BUSINESS_MATERIAL_SOURCES = ("BusinessUI/ConnectionIndicator.swift",)',
                'BUSINESS_MATERIAL_SOURCES = ("Features/Settings/SettingsView.swift",)',
            ))
            self.assertNotEqual(self.run_boundary(root).returncode, 0)

    @unittest.skipUnless(os.environ.get("APPLE_TEMPLATE_TOOL_TESTS") == "1", "设置 APPLE_TEMPLATE_TOOL_TESTS=1 执行原生工具验收")
    def test_generated_projects_include_business_ui_and_pass_architecture(self):
        for platform in ("ios", "macos", "apple"):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory(prefix="apple-tools-") as folder:
                self.assertEqual(self.generate(folder, platform).returncode, 0)
                output = Path(folder) / "MigrationApp"
                for current in (("ios", "macos") if platform == "apple" else (platform,)):
                    root = output / current
                    (root / "BusinessUI/Fixture.swift").write_text('import SwiftUI\nstruct Fixture: View { var body: some View { Text("Fixture") } }\n')
                    result = subprocess.run(["xcodegen", "generate"], cwd=root, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("Fixture.swift in Sources", (root / "MigrationApp.xcodeproj/project.pbxproj").read_text())
                result = subprocess.run(["python3", "scripts/check-architecture.py"], cwd=output, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
