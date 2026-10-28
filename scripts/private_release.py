#!/usr/bin/env python3
"""核查源码仓库访问并校验可选 GitHub 快照；公开 registry 发布由 OIDC 工作流负责。"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ARTIFACT_SUFFIXES = (".whl", ".tgz", ".tar.gz")
METADATA = {"release-manifest.json", "SHA256SUMS"}
REPOSITORY = "danweiyuancircle/dwy-ai-experience"
VERSION_PATTERN = r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?"


class ReleaseError(Exception):
    """安全边界或校验失败；调用方不得继续发布/安装。"""


def require_repository_access(repository: str) -> None:
    """允许公开或私有仓库；使用已有 gh 身份验证访问，不传递或打印 token。"""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ReleaseError("invalid repository name")
    try:
        response = subprocess.check_output(
            ["gh", "api", f"repos/{repository}"], text=True, stderr=subprocess.PIPE, timeout=30
        )
        data = json.loads(response)
        private = data.get("private") if isinstance(data, dict) else None
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        raise ReleaseError("cannot verify repository access") from exc
    if not isinstance(private, bool):
        raise ReleaseError("invalid repository visibility")


def artifact_paths(directory: Path) -> list[Path]:
    """仅允许平铺的包产物与两个元数据文件；禁止目录、符号链接和环境文件。"""
    if not directory.is_dir():
        raise ReleaseError("artifact directory does not exist")
    artifacts = []
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file():
            raise ReleaseError("artifact directory must contain regular files only")
        if path.name in METADATA:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", path.name) or not path.name.endswith(ARTIFACT_SUFFIXES):
            raise ReleaseError("unexpected file in artifact directory")
        if not 0 < path.stat().st_size <= 512 * 1024 * 1024:
            raise ReleaseError("artifact size is invalid")
        artifacts.append(path)
    if not 1 <= len(artifacts) <= 64:
        raise ReleaseError("release must contain between 1 and 64 artifacts")
    return artifacts


def digest(path: Path) -> str:
    """流式计算真实字节摘要，避免把大包整体读入内存。"""
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def write_manifest(directory: Path, tag: str, revision: str) -> None:
    """固定发布身份、源提交、包大小和 SHA256；同标签后续不得静默改包。"""
    if not re.fullmatch(VERSION_PATTERN, tag):
        raise ReleaseError("tag must be a SwiftPM-compatible semantic version")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ReleaseError("revision must be a full Git commit")
    entries = [
        {"name": path.name, "size": path.stat().st_size, "sha256": digest(path)}
        for path in artifact_paths(directory)
    ]
    manifest = {"schema_version": 1, "repository": REPOSITORY, "tag": tag,
                "revision": revision, "artifacts": entries}
    (directory / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (directory / "SHA256SUMS").write_text(
        "".join(f"{entry['sha256']}  {entry['name']}\n" for entry in entries), encoding="utf-8"
    )


def verify_manifest(directory: Path) -> dict:
    """外部清单也需校验，不接受路径逃逸、重复项或未列出的可安装包。"""
    manifest_path = directory / "release-manifest.json"
    if not manifest_path.is_file() or manifest_path.stat().st_size > 128 * 1024:
        raise ReleaseError("release manifest is missing or too large")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["artifacts"]
        if (manifest["schema_version"] != 1 or manifest["repository"] != REPOSITORY
                or not isinstance(manifest["tag"], str)
                or not re.fullmatch(VERSION_PATTERN, manifest["tag"])
                or not isinstance(manifest["revision"], str)
                or not re.fullmatch(r"[0-9a-f]{40}", manifest["revision"])
                or not isinstance(entries, list) or not 1 <= len(entries) <= 64):
            raise ReleaseError("unsupported manifest")
        names = []
        for entry in entries:
            name = entry["name"]
            if (not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name)
                    or not name.endswith(ARTIFACT_SUFFIXES) or name in names):
                raise ReleaseError("unsafe or duplicate artifact name")
            path = directory / name
            if (path.is_symlink() or not path.is_file() or path.stat().st_size != entry["size"]
                    or digest(path) != entry["sha256"]):
                raise ReleaseError("artifact checksum or size mismatch")
            names.append(name)
        if names != [path.name for path in artifact_paths(directory)]:
            raise ReleaseError("manifest does not cover every artifact")
        expected = "".join(f"{entry['sha256']}  {entry['name']}\n" for entry in entries)
        if (directory / "SHA256SUMS").read_text(encoding="utf-8") != expected:
            raise ReleaseError("checksum list does not match manifest")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        raise ReleaseError("invalid release manifest") from exc
    return manifest


def download(repository: str, tag: str, destination: Path) -> None:
    """认证下载固定版本，校验后才允许调用者安装；不读取或打印认证配置。"""
    require_repository_access(repository)
    if repository != REPOSITORY or not re.fullmatch(VERSION_PATTERN, tag):
        raise ReleaseError("unsupported repository or tag")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ReleaseError("download destination must be empty")
    subprocess.run(
        ["gh", "release", "download", tag, "--repo", repository, "--dir", str(destination)],
        check=True, timeout=180,
    )
    manifest = verify_manifest(destination)
    if manifest["tag"] != tag:
        raise ReleaseError("release tag does not match manifest")


def main() -> None:
    """仅输出发布阶段和安全错误分类，不输出外部 CLI 的原始异常正文。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--repository", default=REPOSITORY)
    manifest = sub.add_parser("manifest")
    manifest.add_argument("--directory", type=Path, required=True)
    manifest.add_argument("--tag", required=True)
    manifest.add_argument("--revision", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--directory", type=Path, required=True)
    fetch = sub.add_parser("download")
    fetch.add_argument("--repository", default=REPOSITORY)
    fetch.add_argument("--tag", required=True)
    fetch.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "check":
            require_repository_access(args.repository)
        elif args.command == "manifest":
            write_manifest(args.directory, args.tag, args.revision)
            verify_manifest(args.directory)
        elif args.command == "verify":
            verify_manifest(args.directory)
        else:
            download(args.repository, args.tag, args.directory)
    except (ReleaseError, subprocess.SubprocessError, OSError) as exc:
        # ReleaseError 均为本模块固定文案；外部异常仍只输出类型，避免泄露凭据/原始响应。
        reason = str(exc) if isinstance(exc, ReleaseError) else type(exc).__name__
        parser.exit(1, f"Release failed: {reason}\n")
    print(f"Release {args.command}: verified")


if __name__ == "__main__":
    main()
