"""私有发布回归：公开仓库拒绝发布，产物必须完整、可校验且无路径逃逸。"""

import importlib.util
import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


class PrivateReleaseTests(unittest.TestCase):
    """测试真实文件与摘要行为，仅将 GitHub 外部命令替换为固定响应。"""

    def module(self):
        """显式加载发布脚本，使脚本缺失时成为清楚的失败。"""
        path = ROOT / "scripts/private_release.py"
        self.assertTrue(path.is_file(), "private release tool is missing")
        spec = importlib.util.spec_from_file_location("private_release", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_npm_packages_cannot_be_accidentally_published(self):
        """私有源码也可能被 npm publish 公开，包级必须有拒绝保护。"""
        for directory in ("frontend/eui", "frontend/ekit", "frontend/admin-shell", "dwy-cli"):
            with self.subTest(directory=directory):
                value = json.loads((ROOT / directory / "package.json").read_text())
                self.assertIs(value.get("private"), True)
                self.assertNotEqual(value.get("publishConfig", {}).get("access"), "public")

    def test_legacy_workflows_no_longer_publish_public_packages(self):
        """即使管理员重新启用旧工作流，源码也不能恢复公共 registry 发布。"""
        for path in (ROOT / ".github/workflows").glob("publish-*.yml"):
            with self.subTest(path=path.name):
                value = path.read_text()
                self.assertNotIn("npm publish", value)
                self.assertNotIn("pypa/gh-action-pypi-publish", value)

    def test_python_packages_reject_accidental_public_uploads(self):
        """PyPI 原生拒绝 Private classifier，为 Python 包保留第二层防误发布。"""
        for directory in ("backend", "modules/auth/backend"):
            with self.subTest(directory=directory):
                value = tomllib.loads((ROOT / directory / "pyproject.toml").read_text())
                self.assertIn("Private :: Do Not Upload", value["project"].get("classifiers", []))

    def test_github_public_repository_is_rejected(self):
        """服务端真实可见性与预期不符时 fail closed。"""
        module = self.module()
        with patch.object(subprocess, "check_output", return_value='{"private":false}'):
            with self.assertRaises(module.ReleaseError):
                module.require_private_repository("owner/repo")
        with patch.object(subprocess, "check_output", return_value='{"private":true}'):
            module.require_private_repository("owner/repo")

    def test_manifest_checks_every_artifact_and_detects_tampering(self):
        """校验实际字节，而非仅确认产物文件存在。"""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            package = output / "dwy-app-auth-0.1.0-py3-none-any.whl"
            package.write_bytes(b"wheel snapshot")
            module.write_manifest(output, "0.4.0", "a" * 40)
            module.verify_manifest(output)
            package.write_bytes(b"changed after publication")
            with self.assertRaises(module.ReleaseError):
                module.verify_manifest(output)

    def test_manifest_rejects_path_traversal_and_unlisted_packages(self):
        """下载的清单本身也是外部输入，不能借路径读取目标目录之外。"""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "package.tgz").write_bytes(b"archive")
            module.write_manifest(output, "0.4.0", "a" * 40)
            path = output / "release-manifest.json"
            value = json.loads(path.read_text())
            value["artifacts"][0]["name"] = "../outside.whl"
            path.write_text(json.dumps(value))
            with self.assertRaises(module.ReleaseError):
                module.verify_manifest(output)
            module.write_manifest(output, "0.4.0", "a" * 40)
            (output / "unlisted.whl").write_bytes(b"unexpected")
            with self.assertRaises(module.ReleaseError):
                module.verify_manifest(output)

    def test_manifest_cannot_be_built_with_secrets_or_empty_output(self):
        """明确的文件白名单阻止环境文件进入发布目录。"""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with self.assertRaises(module.ReleaseError):
                module.write_manifest(output, "0.4.0", "a" * 40)
            (output / ".env").write_text("DO_NOT_PUBLISH=example")
            (output / "package.tgz").write_bytes(b"archive")
            with self.assertRaises(module.ReleaseError):
                module.write_manifest(output, "0.4.0", "a" * 40)

    def test_external_manifest_requires_a_valid_release_identity(self):
        """清单身份不能缺失或伪装成其他类型；错误统一为可处理的发布异常。"""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "package.tgz").write_bytes(b"archive")
            module.write_manifest(output, "0.4.0", "a" * 40)
            path = output / "release-manifest.json"
            original = json.loads(path.read_text())
            invalid = [[], {**original, "tag": "../main"},
                       {**original, "revision": "short"}, {**original, "artifacts": [None]}]
            for value in invalid:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value))
                    with self.assertRaises(module.ReleaseError):
                        module.verify_manifest(output)


if __name__ == "__main__":
    unittest.main()
