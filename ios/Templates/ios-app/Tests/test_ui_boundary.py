"""新项目 UI 边界检查；从工程根运行 python3 -m unittest discover -s Tests -p 'test_*.py'。"""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def ui_sources():
    """只检查本壳源码；基础库源码和测试不在项目 UI 边界内。"""
    # shortcut: 文本检查不替代 Swift 语法与依赖解析，复杂条件编译须结合构建审查。
    for folder in ("App", "Features", "BusinessUI"):
        for path in (ROOT / folder).rglob("*.swift"):
            source = re.sub(r"//[^\n]*|/\*[\s\S]*?\*/", "", path.read_text())
            yield path.relative_to(ROOT), source


class UIComponentBoundaryTests(unittest.TestCase):
    """保留原生导航、菜单项、toolbar、alert，禁止项目重做通用材质适配。"""

    def test_ui_product_is_linked(self):
        project = (ROOT / "project.yml").read_text()
        self.assertIn("product: DesignKitIOS", project)
        self.assertNotIn("product: DesignKitMac", project)

    def test_package_versions_match(self):
        manifest = (ROOT / "Package.swift").read_text()
        project = (ROOT / "project.yml").read_text()
        package = re.search(r'\.package\(url: "https://github\.com/danweiyuancircle/dwy-ai-experience\.git", exact: "([^"]+)"\)', manifest)
        xcode = re.search(r"AppleAppKit:\n    url: https://github\.com/danweiyuancircle/dwy-ai-experience\.git\n    exactVersion: ([^\n]+)", project)
        self.assertIsNotNone(package, "Package.swift 须精确依赖已发布基础库")
        self.assertIsNotNone(xcode, "project.yml 须精确依赖同一基础库")
        self.assertEqual(package.group(1), xcode.group(1))

    def test_theme_is_assembled_at_app_root(self):
        roots = "\n".join(path.read_text() for path in (ROOT / "App").glob("*App.swift"))
        self.assertIn(".eControlTheme(", roots)

    def test_ios_sources_do_not_import_mac_ui(self):
        violations = [str(path) for path, source in ui_sources()
                      if re.search(r"\bimport\s+(?:AppKit|DesignKitMac|MacUI)\b", source)]
        self.assertEqual(violations, [], "iOS 壳禁止依赖 Mac UI")

    def test_material_adaptation_stays_in_base_components(self):
        violations = [str(path) for path, source in ui_sources()
                      if re.search(r"\.glassEffect\s*\(|\.buttonStyle\s*\(\s*\.glass(?:Prominent)?\b", source)]
        self.assertEqual(violations, [], "使用基础组件的 placement，不在页面复制系统材质分支")


if __name__ == "__main__":
    unittest.main()
