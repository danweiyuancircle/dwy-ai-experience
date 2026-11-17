"""用真实 XcodeGen/SwiftPM 解析临时工程，验证四层检查器的拒绝边界。"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[1] / "Templates/common/scripts/check-architecture.py"
URL = "https://github.com/danweiyuancircle/dwy-ai-experience.git"


class ArchitectureTests(unittest.TestCase):
    """不解析远端依赖，不读取或修改真实项目的锁文件。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="apple-architecture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assertTrue(CHECKER.is_file(), "生成物必须包含架构检查器")
        self.write("scripts/check-architecture.py", CHECKER.read_text())
        self.core = self.root / "packages/DemoCore"
        self.manifest = '''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "DemoCore", products: [.library(name: "BizFoundation", targets: ["BizFoundation"])], dependencies: [
    .package(url: "URL", exact: "0.8.0")
], targets: [.target(name: "BizFoundation", dependencies: [.product(name: "CoreKit", package: "dwy-ai-experience")])])
'''.replace("URL", URL)
        self.write("packages/DemoCore/Package.swift", self.manifest)
        self.write("packages/DemoCore/Sources/BizFoundation/Rule.swift", "import Foundation\n")
        self.platform("ios")

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return target

    def platform(self, platform):
        self.write(f"{platform}/App/Main.swift", "import SwiftUI\n")
        self.write(f"{platform}/Features/Settings/Settings.swift", "import SwiftUI\n")
        self.write(f"{platform}/BusinessUI/Card.swift", "import SwiftUI\n")
        value = "iOS" if platform == "ios" else "macOS"
        self.write(f"{platform}/project.yml", f'''name: Demo
packages:
  DemoCore:
    path: ../packages/DemoCore
  AppleAppKit:
    url: {URL}
    exactVersion: 0.8.0
targets:
  Demo:
    type: application
    platform: {value}
    sources:
      - path: App
      - path: Features
      - path: BusinessUI
    dependencies:
      - package: DemoCore
        product: BizFoundation
''')

    def run_check(self):
        env = dict(os.environ)
        if "DEVELOPER_DIR" not in env and Path("/Applications/Xcode.app").exists():
            env["DEVELOPER_DIR"] = "/Applications/Xcode.app/Contents/Developer"
        return subprocess.run(
            ["python3", "-B", str(self.root / "scripts/check-architecture.py")],
            cwd="/", env=env, capture_output=True, text=True,
        )

    def assert_rejected(self, message):
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stdout + result.stderr)

    def test_single_and_dual_platform_projects_pass(self):
        for platform in ("ios", "macos"):
            self.platform(platform)
            result = self.run_check()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_core_cannot_import_ui(self):
        self.write("packages/DemoCore/Sources/BizFoundation/Rule.swift", "import SwiftUI\nstruct BusinessRule {}\n")
        self.assert_rejected("BizFoundation")

    def test_core_manifest_cannot_depend_on_ui(self):
        (self.core / "Package.swift").write_text(self.manifest.replace('name: "CoreKit"', 'name: "DesignKitIOS"'))
        self.assert_rejected("DesignKitIOS")

    def test_project_cannot_compile_other_platform_sources(self):
        self.platform("macos")
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("- path: App", "- path: App\n      - path: ../macos/App"))
        self.assert_rejected("macos/App/Main.swift")

    def test_project_cannot_compile_shared_package_sources(self):
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("- path: App", "- path: App\n      - path: ../packages/DemoCore/Sources"))
        self.assert_rejected("packages/DemoCore/Sources")

    def test_app_cannot_link_other_platform_ui_product(self):
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("dependencies:\n", "dependencies:\n      - package: AppleAppKit\n        product: DesignKitMac\n"))
        self.assert_rejected("DesignKitMac")

    def test_app_cannot_reference_other_platform_package(self):
        self.platform("macos")
        self.write("macos/Platform/MacPlatform/Service.swift", "import Foundation\n")
        self.write("macos/Package.swift", '''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "DemoMac", products: [.library(name: "MacPlatform", targets: ["MacPlatform"])], targets: [.target(name: "MacPlatform", path: "Platform/MacPlatform")])
''')
        mac = self.root / "macos/project.yml"
        mac.write_text(mac.read_text().replace("packages:\n", "packages:\n  DemoMac:\n    path: .\n").replace("dependencies:\n", "dependencies:\n      - package: DemoMac\n        product: MacPlatform\n"))
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("packages:\n", "packages:\n  WrongPlatform:\n    path: ../macos\n"))
        self.assert_rejected("另一平台")

    def test_business_ui_must_be_in_app_sources(self):
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("      - path: BusinessUI\n", ""))
        self.assert_rejected("BusinessUI/Card.swift")

    def test_excluded_business_ui_is_not_counted_as_compiled(self):
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace(
            "- path: BusinessUI", "- path: BusinessUI\n        excludes: [Card.swift]",
        ))
        generated = subprocess.run(["xcodegen", "generate"], cwd=spec.parent, capture_output=True, text=True)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        project = (spec.parent / "Demo.xcodeproj/project.pbxproj").read_text()
        self.assertNotIn("Card.swift in Sources", project)
        self.assert_rejected("BusinessUI/Card.swift")

    def test_source_includes_do_not_hide_missing_business_ui(self):
        self.write("ios/BusinessUI/Other.swift", "import SwiftUI\n")
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace(
            "- path: BusinessUI", "- path: BusinessUI\n        includes: [Other.swift]",
        ))
        generated = subprocess.run(["xcodegen", "generate"], cwd=spec.parent, capture_output=True, text=True)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        project = (spec.parent / "Demo.xcodeproj/project.pbxproj").read_text()
        self.assertNotIn("Card.swift in Sources", project)
        self.assertIn("Other.swift in Sources", project)
        self.assert_rejected("BusinessUI/Card.swift")

    def test_platform_sources_must_have_an_owner(self):
        self.write("ios/Platform/IOSPlatform/Service.swift", "import Foundation\n")
        self.assert_rejected("未编译")

    def test_platform_sources_can_be_compiled_by_app(self):
        self.write("ios/Platform/IOSPlatform/Service.swift", "import Foundation\n")
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("- path: App", "- path: App\n      - path: Platform"))
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def platform_package(self):
        self.write("ios/Platform/IOSPlatform/Service.swift", "import Foundation\n")
        self.write("ios/Package.swift", '''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "DemoIOS", products: [.library(name: "IOSPlatform", targets: ["IOSPlatform"])], targets: [
    .target(name: "IOSPlatform", path: "Platform/IOSPlatform")
])
''')
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("packages:\n", "packages:\n  DemoIOS:\n    path: .\n").replace("dependencies:\n", "dependencies:\n      - package: DemoIOS\n        product: IOSPlatform\n"))

    def test_platform_sources_can_be_compiled_by_package(self):
        self.platform_package()
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_platform_sources_cannot_be_compiled_twice(self):
        self.platform_package()
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("- path: App", "- path: App\n      - path: Platform"))
        self.assert_rejected("重复编译")

    def test_platform_target_can_be_transitively_linked(self):
        self.platform_package()
        self.write("ios/Platform/IOSFacade/API.swift", "import Foundation\n")
        manifest = self.root / "ios/Package.swift"
        manifest.write_text(manifest.read_text().replace(
            'targets: ["IOSPlatform"]', 'targets: ["IOSFacade"]',
        ).replace(
            '.target(name: "IOSPlatform", path: "Platform/IOSPlatform")',
            '.target(name: "IOSPlatform", path: "Platform/IOSPlatform"), .target(name: "IOSFacade", dependencies: ["IOSPlatform"], path: "Platform/IOSFacade")',
        ))
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_targets_cannot_compile_same_source(self):
        self.platform_package()
        manifest = self.root / "ios/Package.swift"
        manifest.write_text(manifest.read_text().replace(
            '.target(name: "IOSPlatform", path: "Platform/IOSPlatform")',
            '.target(name: "IOSPlatform", path: "Platform/IOSPlatform"), .target(name: "Duplicate", path: "Platform/IOSPlatform")',
        ))
        self.assert_rejected("重复编译")

    def test_package_target_cannot_compile_other_platform(self):
        self.platform_package()
        self.platform("macos")
        manifest = self.root / "ios/Package.swift"
        manifest.write_text(manifest.read_text().replace('path: "Platform/IOSPlatform"', 'path: "../macos/App"'))
        self.assert_rejected("macos/App")

    def test_versions_must_match_between_manifests_and_projects(self):
        spec = self.root / "ios/project.yml"
        spec.write_text(spec.read_text().replace("exactVersion: 0.8.0", "exactVersion: 0.9.0"))
        self.assert_rejected("版本")

    def test_lock_version_must_match_exact_requirement(self):
        self.write("ios/Package.resolved", json.dumps({"version": 3, "pins": [{
            "identity": "dwy-ai-experience", "location": URL,
            "state": {"version": "0.7.0", "revision": "old"},
        }]}))
        self.assert_rejected("锁文件")

    def test_same_locked_version_cannot_have_different_revisions(self):
        self.platform("macos")
        for platform in ("ios", "macos"):
            self.write(f"{platform}/Package.resolved", json.dumps({"version": 3, "pins": [{
                "identity": "dwy-ai-experience", "location": URL,
                "state": {"version": "0.8.0", "revision": platform},
            }]}))
        self.assert_rejected("revision")

    def test_apple_appkit_must_use_exact_version(self):
        (self.core / "Package.swift").write_text(self.manifest.replace('exact: "0.8.0"', 'from: "0.8.0"'))
        self.assert_rejected("exact")

    def test_lock_version_must_fit_declared_range(self):
        (self.core / "Package.swift").write_text(self.manifest.replace(
            '.package(url: "' + URL + '", exact: "0.8.0")',
            '.package(url: "' + URL + '", exact: "0.8.0"), .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0")',
        ))
        self.write("packages/DemoCore/Package.resolved", json.dumps({"version": 3, "pins": [{
            "identity": "swift-log", "location": "https://github.com/apple/swift-log.git",
            "state": {"version": "2.0.0", "revision": "outside"},
        }]}))
        self.assert_rejected("锁文件")

    def test_foundation_target_name_is_rejected(self):
        (self.core / "Package.swift").write_text(self.manifest.replace('"BizFoundation"', '"Foundation"'))
        self.assert_rejected("Foundation")

    def test_comments_do_not_create_fake_ui_imports(self):
        self.write("packages/DemoCore/Sources/BizFoundation/Rule.swift", "// import SwiftUI\n/* import AppKit */\nimport Foundation\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_native_tool_is_not_reported_as_pass(self):
        env = dict(os.environ, PATH="")
        result = subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/check-architecture.py")],
            cwd="/", env=env, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("架构检查未完成", result.stderr)


if __name__ == "__main__":
    unittest.main()
