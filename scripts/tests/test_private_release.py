"""公开包发布回归，以及 GitHub 快照产物的完整性校验。"""

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

    def test_npm_packages_are_publicly_publishable_but_workspace_is_not(self):
        """根工作区不得作为包上传，独立分发包允许公开发布。"""
        self.assertIs(json.loads((ROOT / "package.json").read_text())["private"], True)
        for directory in ("frontend/eui", "frontend/ekit", "frontend/admin-shell", "frontend/auth-web", "dwy-cli"):
            with self.subTest(directory=directory):
                value = json.loads((ROOT / directory / "package.json").read_text())
                self.assertIsNot(value.get("private"), True)
                self.assertEqual(value["publishConfig"]["access"], "public")

    def test_public_publishing_uses_oidc_and_checks_repository_access(self):
        """每个公开发布入口使用短期身份，并在发布前核查仓库访问。"""
        workflows = {
            "publish-eui.yml": "npm publish --access public",
            "publish-ekit.yml": "npm publish --access public",
            "publish-admin.yml": "npm publish --access public",
            "publish-auth-web.yml": "npm publish --access public",
            "publish-cli.yml": "npm publish --access public",
            "publish-eapi.yml": "pypa/gh-action-pypi-publish@",
            "publish-auth.yml": "pypa/gh-action-pypi-publish@",
            "publish-webhooks.yml": "pypa/gh-action-pypi-publish@",
            "publish-device-fingerprint.yml": "pypa/gh-action-pypi-publish@",
        }
        for filename, publish in workflows.items():
            path = ROOT / ".github/workflows" / filename
            with self.subTest(path=path.name):
                value = path.read_text()
                self.assertIn(publish, value)
                self.assertIn("id-token: write", value)
                self.assertIn("scripts/private_release.py check", value)
                self.assertNotIn("--provenance", value)
                self.assertNotIn("secrets.NPM_TOKEN", value)
                self.assertNotIn("secrets.PYPI_API_TOKEN", value)

    def test_python_packages_allow_public_uploads(self):
        """三个 Python 分发包都允许上传公开 PyPI。"""
        for directory in ("backend", "backend/packages/auth", "backend/packages/device-fingerprint",
                          "backend/packages/webhooks"):
            with self.subTest(directory=directory):
                value = tomllib.loads((ROOT / directory / "pyproject.toml").read_text())
                self.assertNotIn("Private :: Do Not Upload", value["project"].get("classifiers", []))

    def test_webhooks_are_tested_and_built_in_the_shared_release(self):
        """共享轮包必须经过同一验收与构建，不能只在业务项目本地存在。"""
        workflow = (ROOT / ".github/workflows/private-release.yml").read_text()
        self.assertIn("backend/packages/webhooks/tests", workflow)
        self.assertIn("uv build --project backend/packages/webhooks", workflow)
        manifest = tomllib.loads((ROOT / "ci/pyproject.toml").read_text())
        self.assertTrue(any(value.startswith("dwy-webhooks[") for value in manifest["project"]["dependencies"]))

    def test_github_public_and_private_repositories_are_accessible(self):
        """切换可见性不影响发布，仍须拿到服务端有效响应。"""
        module = self.module()
        for private in (False, True):
            with self.subTest(private=private):
                with patch.object(subprocess, "check_output", return_value=json.dumps({"private": private})):
                    module.require_repository_access("owner/repo")

    def test_repository_access_rejects_invalid_responses_and_network_errors(self):
        """API 响应不完整或访问失败时仍中止发布。"""
        module = self.module()
        for response in ('{}', '[]', '{"private":"false"}', 'invalid JSON'):
            with self.subTest(response=response):
                with patch.object(subprocess, "check_output", return_value=response):
                    with self.assertRaises(module.ReleaseError):
                        module.require_repository_access("owner/repo")
        with patch.object(subprocess, "check_output", side_effect=subprocess.TimeoutExpired("gh", 30)):
            with self.assertRaises(module.ReleaseError):
                module.require_repository_access("owner/repo")
        with patch.object(subprocess, "check_output") as command:
            with self.assertRaises(module.ReleaseError):
                module.require_repository_access("owner/repo/extra")
            command.assert_not_called()

    def test_manifest_checks_every_artifact_and_detects_tampering(self):
        """校验实际字节，而非仅确认产物文件存在。"""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            package = output / "dwy_auth-0.1.0-py3-none-any.whl"
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
