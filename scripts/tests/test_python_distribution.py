"""公开分发前的归档安全与独立安装验收。"""

import importlib.util
import io
import sys
import sysconfig
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "check_python_distribution.py"


class PythonDistributionTests(unittest.TestCase):
    """构造真实归档，验证泄漏阻断及隔离安装失败时的资源清理。"""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.package = Path(self.temporary.name) / "package"
        self.package.mkdir()
        (self.package / "pyproject.toml").write_text('[project]\nname="example-pkg"\nversion="1.2.3"\n')
        self.dist = self.package / "dist"
        self.dist.mkdir()

    def module(self):
        self.assertTrue(SCRIPT.is_file(), "distribution safety checker must exist")
        spec = importlib.util.spec_from_file_location("distribution_check", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def archives(self, *, wheel_extra=None, source_extra=None, requirement="normal>=1", version="1.2.3"):
        metadata = (f"Metadata-Version: 2.3\nName: example-pkg\nVersion: {version}\n"
                    f"Requires-Dist: {requirement}\n")
        wheel = self.dist / "example_pkg-1.2.3-py3-none-any.whl"
        files = {"example/__init__.py": "", "example_pkg-1.2.3.dist-info/METADATA": metadata,
                 "example_pkg-1.2.3.dist-info/WHEEL": "Wheel-Version: 1.0\n"}
        files.update(wheel_extra or {})
        with zipfile.ZipFile(wheel, "w") as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        files = {"src/example/__init__.py": "", "PKG-INFO": metadata,
                 "pyproject.toml": (self.package / "pyproject.toml").read_text()}
        files.update(source_extra or {})
        with tarfile.open(self.dist / "example_pkg-1.2.3.tar.gz", "w:gz") as archive:
            for name, content in files.items():
                member = tarfile.TarInfo("example_pkg-1.2.3/" + name)
                data = content.encode()
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return wheel

    def test_accepts_only_requested_module_and_matching_metadata(self):
        wheel = self.archives()
        self.assertEqual(self.module().inspect_distribution(self.package, "example"),
                         (wheel, "example-pkg", "1.2.3"))

    def test_allows_uv_generated_dist_ignore_marker(self):
        wheel = self.archives()
        (self.dist / ".gitignore").write_text("*")
        self.assertEqual(self.module().inspect_distribution(self.package, "example")[0], wheel)

    def test_allows_standard_source_documentation_and_ignore_files(self):
        wheel = self.archives(source_extra={"CHANGELOG.md": "release notes", ".gitignore": "dist/",
                                           "examples/new_project/app.py": "import example"})
        self.assertEqual(self.module().inspect_distribution(self.package, "example")[0], wheel)

    def test_rejects_other_products_secrets_caches_and_traversal_in_wheel(self):
        module = self.module()
        for name, content in {"other_product/__init__.py": "", "example/.env.production": "SECRET=x",
                              "example/key.pem": "secret", "example/__pycache__/x.pyc": "cache",
                              "../escape.py": "", "example/config.py": "-----BEGIN PRIVATE KEY-----"}.items():
            with self.subTest(name=name):
                self.archives(wheel_extra={name: content})
                with self.assertRaises(module.DistributionError):
                    module.inspect_distribution(self.package, "example")

    def test_rejects_unsafe_source_archive_and_unrelated_source_product(self):
        module = self.module()
        for name in (".env", "src/other_product/__init__.py", "../escape", "tests/__pycache__/x.pyc"):
            with self.subTest(name=name):
                self.archives(source_extra={name: "unsafe"})
                with self.assertRaises(module.DistributionError):
                    module.inspect_distribution(self.package, "example")

    def test_rejects_direct_dependency_sources_and_version_drift(self):
        module = self.module()
        for requirement in ("dep @ file:///tmp/dep.whl", "dep @ git+https://example.com/repo", "dep @ https://example.com/dep.whl"):
            with self.subTest(requirement=requirement):
                self.archives(requirement=requirement)
                with self.assertRaises(module.DistributionError):
                    module.inspect_distribution(self.package, "example")
        self.archives(version="0.0.1")
        with self.assertRaises(module.DistributionError):
            module.inspect_distribution(self.package, "example")

    def test_rejects_missing_or_stale_extra_distribution_artifacts(self):
        module = self.module()
        with self.assertRaises(module.DistributionError):
            module.inspect_distribution(self.package, "example")
        self.archives()
        (self.dist / "old-0.0.1.whl").write_bytes(b"old")
        with self.assertRaises(module.DistributionError):
            module.inspect_distribution(self.package, "example")

    def test_optional_capability_is_imported_by_the_isolated_probe(self):
        module = self.module()
        calls = []
        with patch.object(
            module.subprocess, "run", side_effect=lambda command, **kwargs: calls.append(command),
        ):
            module.verify_installation(
                self.archives(), "example-pkg", "1.2.3", "example", "reviews",
                import_modules=("example.reviews.client",),
            )
        probe = calls[-1]
        root = Path(sysconfig.get_path("purelib"))
        distribution = SimpleNamespace(version="1.2.3", locate_file=lambda _: root)

        def imported(name):
            return SimpleNamespace(__file__=root / name.replace(".", "/") / "__init__.py")

        with patch.object(sys, "argv", ["-c", *probe[4:]]), \
                patch("importlib.metadata.distribution", return_value=distribution), \
                patch("importlib.import_module", side_effect=imported) as imports:
            exec(probe[3], {})
        self.assertEqual(
            [call.args[0] for call in imports.call_args_list], ["example", "example.reviews.client"],
        )

    def test_optional_imports_must_belong_to_the_distribution_namespace(self):
        module = self.module()
        with patch.object(module.subprocess, "run") as run:
            with self.assertRaises(module.DistributionError):
                module.verify_installation(
                    self.archives(), "example-pkg", "1.2.3", "example",
                    import_modules=("other_product.client",),
                )
        run.assert_not_called()

    def test_installation_is_isolated_uses_official_index_and_cleans_after_failure(self):
        module = self.module()
        wheel = self.archives()
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            if len(calls) == 3:
                raise module.subprocess.CalledProcessError(1, command)

        with patch.object(module.subprocess, "run", side_effect=run):
            with self.assertRaises(module.DistributionError):
                module.verify_installation(wheel, "example-pkg", "1.2.3", "example", "one,two")
        self.assertEqual(len(calls), 3)
        install, options = calls[1]
        self.assertIn("https://pypi.org/simple", install)
        self.assertIn(str(wheel.resolve()) + "[one,two]", install)
        self.assertIn("--no-config", install)
        self.assertNotIn("PYTHONPATH", options["env"])
        self.assertNotIn("UV_INDEX_URL", options["env"])
        self.assertEqual(calls[2][0][1], "-I")
        self.assertFalse(Path(options["cwd"]).is_relative_to(self.package))
        self.assertFalse(Path(options["cwd"]).exists())


if __name__ == "__main__":
    unittest.main()
