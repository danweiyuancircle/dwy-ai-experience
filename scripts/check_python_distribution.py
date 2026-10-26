#!/usr/bin/env python3
"""上传前检查 dist 归档，并从仓库外通过官方 PyPI 安装实际 wheel。"""

import argparse
import email.parser
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath


class DistributionError(Exception):
    """产物或隔离安装不符合公开分发约束，调用方必须停止上传。"""


def _normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "_", name).lower()


def _safe_member(name: str, content: bytes) -> PurePosixPath:
    path = PurePosixPath(name)
    if (path.is_absolute() or ".." in path.parts or "\\" in name
            or any(part.startswith(".env") or part in {".git", ".venv", "venv", "__pycache__",
                                                      ".pytest_cache", ".ruff_cache"} for part in path.parts)
            or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".pyc", ".pyo"}
            or re.search(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----", content)):
        raise DistributionError("archive contains unsafe paths, credentials or caches")
    return path


def _metadata(content: bytes, name: str, version: str) -> None:
    metadata = email.parser.BytesParser().parsebytes(content)
    if _normalized(metadata.get("Name", "")) != _normalized(name) or metadata.get("Version") != version:
        raise DistributionError("distribution metadata does not match project name and version")
    for requirement in metadata.get_all("Requires-Dist", []):
        if re.search(r"@|://|(?:file|git|ssh):|(?:^|\s)(?:/|\.\.?[/\\])", requirement, re.I):
            raise DistributionError("distribution dependency contains a local or direct URL source")


def inspect_distribution(package: Path, module: str) -> tuple[Path, str, str]:
    """只检查本次单包产物；拒绝混入模块、私钥、缓存及本地依赖元数据。"""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", module) is None:
        raise DistributionError("module must be a top-level Python package namespace")
    project = tomllib.loads((package / "pyproject.toml").read_text())["project"]
    name, version = project["name"], project["version"]
    dist = package / "dist"
    # uv build 自动生成忽略标记；它不是待上传的分发产物。
    files = [path for path in dist.iterdir() if path.name != ".gitignore"] if dist.is_dir() else []
    wheels, sources = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    if (len(files) != 2 or len(wheels) != 1 or len(sources) != 1
            or any(path.is_symlink() or not path.is_file() for path in files)):
        raise DistributionError("dist must contain exactly one wheel and one source archive")
    identity = f"{_normalized(name)}-{version}"
    info = identity + ".dist-info"
    with zipfile.ZipFile(wheels[0]) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or f"{module}/__init__.py" not in names:
            raise DistributionError("wheel has duplicate entries or is missing the requested module")
        for member in archive.infolist():
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise DistributionError("archive must not contain symbolic links")
            path = _safe_member(member.filename, archive.read(member))
            if not path.parts or path.parts[0] not in {module, info}:
                raise DistributionError("wheel contains another module or unrelated distribution metadata")
        if f"{info}/METADATA" not in names:
            raise DistributionError("wheel metadata is missing")
        _metadata(archive.read(f"{info}/METADATA"), name, version)
    with tarfile.open(sources[0], "r:gz") as archive:
        seen, metadata_found = set(), False
        for member in archive.getmembers():
            path = _safe_member(member.name, b"")
            if not (member.isfile() or member.isdir()) or member.name in seen:
                raise DistributionError("source archive contains links or duplicate entries")
            seen.add(member.name)
            if not path.parts or _normalized(path.parts[0]) != _normalized(identity):
                raise DistributionError("source archive has an unexpected root")
            if member.isdir():
                continue
            content = archive.extractfile(member).read()
            relative = _safe_member(str(path.relative_to(path.parts[0])), content)
            parts = relative.parts
            if ((parts[0] == "src" and (len(parts) < 2 or parts[1] not in {
                    module, _normalized(name) + ".egg-info"}))
                    or (parts[0] != "src" and parts[0] not in {
                        module, "tests", "docs", "examples", "pyproject.toml", ".gitignore",
                        "PKG-INFO", "setup.py", "setup.cfg", "MANIFEST.in"}
                        and not re.fullmatch(
                            r"(?:README|CHANGELOG|LICENSE|COPYING|NOTICE|THIRD_PARTY_NOTICES)(?:\..+)?",
                            parts[0], re.I))):
                raise DistributionError("source archive contains another product or unrelated files")
            if relative.name == "PKG-INFO":
                _metadata(content, name, version)
                metadata_found = True
        if not metadata_found:
            raise DistributionError("source distribution metadata is missing")
    return wheels[0], name, version


def verify_installation(wheel: Path, name: str, version: str, module: str, extras: str = "") -> None:
    """临时新环境只从官方 PyPI 解析依赖，退出或失败时清理，不读取发布凭据。"""
    if extras and re.fullmatch(r"[A-Za-z0-9_-]+(?:,[A-Za-z0-9_-]+)*", extras) is None:
        raise DistributionError("extras must be comma-separated package extra names")
    wheel = wheel.resolve()
    with tempfile.TemporaryDirectory(prefix="python-distribution-") as temporary:
        root = Path(temporary)
        environment = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT") if key in os.environ}
        # 不继承项目索引、PYTHONPATH、代理或认证配置；不修改 HOME。
        (root / "netrc").touch()
        environment.update(UV_NO_CONFIG="1", UV_CACHE_DIR=str(root / "cache"),
                           XDG_DATA_HOME=str(root / "data"), XDG_CONFIG_HOME=str(root / "config"),
                           NETRC=str(root / "netrc"), UV_PYTHON_DOWNLOADS="never")
        options = dict(cwd=root, env=environment, check=True, capture_output=True, text=True, timeout=600)
        python = root / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        try:
            subprocess.run(
                [sys.executable, "-I", "-m", "venv", "--without-pip", str(root / "venv")], **options)
            subprocess.run(["uv", "pip", "install", "--python", str(python), "--no-config", "--no-sources",
                            "--default-index", "https://pypi.org/simple", "--keyring-provider", "disabled",
                            "--no-cache", str(wheel) + (f"[{extras}]" if extras else "")], **options)
            code = (
                "import importlib,importlib.metadata as m,pathlib,sys,sysconfig; "
                "name,version,module=sys.argv[1:]; d=m.distribution(name); "
                "assert d.version==version, 'installed version mismatch'; "
                "p=pathlib.Path(importlib.import_module(module).__file__).resolve(); "
                "roots=[pathlib.Path(sysconfig.get_path(k)).resolve() for k in ('purelib','platlib')]; "
                "assert any(p.is_relative_to(r) for r in roots), 'module is outside site-packages'; "
                "assert p.is_relative_to(pathlib.Path(sys.prefix).resolve()), 'module is outside venv'; "
                "assert pathlib.Path(d.locate_file('')).resolve() in roots, "
                "'metadata is outside site-packages'"
            )
            subprocess.run([str(python), "-I", "-c", code, name, version, module], **options)
        except (subprocess.SubprocessError, OSError) as error:
            raise DistributionError("isolated official-PyPI wheel installation or import failed") from error


def main() -> None:
    """命令行接收包目录、唯一模块及可选 extras；成功后才允许 workflow 上传。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--module", required=True)
    parser.add_argument("--extras", default="")
    args = parser.parse_args()
    try:
        wheel, name, version = inspect_distribution(args.package.resolve(), args.module)
        verify_installation(wheel, name, version, args.module, args.extras)
    except (DistributionError, OSError, ValueError, KeyError, zipfile.BadZipFile, tarfile.TarError) as error:
        reason = str(error) if isinstance(error, DistributionError) else type(error).__name__
        parser.exit(1, f"Python distribution check failed: {reason}\n")
    print(f"Python distribution verified: {name}=={version} ({args.module})")


if __name__ == "__main__":
    main()
