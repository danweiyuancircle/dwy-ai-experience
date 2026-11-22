"""生成四层 Apple 工程；追加平台只写新端，不覆盖已有源码、配置或锁文件。"""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE_URL = "https://github.com/danweiyuancircle/dwy-ai-experience.git"
PACKAGE_VERSION = "0.12.0"


def render_tree(source, destination, replacements):
    """模板只含文本；先复制到临时目录，按占位符替换内容和 AppName 文件名。"""
    shutil.copytree(source, destination)
    for path in destination.rglob("*"):
        if path.is_file():
            text = path.read_text()
            for key, value in replacements.items():
                text = text.replace(key, value)
            path.write_text(text)
    for path in sorted(destination.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if "AppName" in path.name:
            path.rename(path.with_name(path.name.replace("AppName", replacements["__APP_NAME__"])))


def read_tool_json(arguments):
    """使用原生结构化输出；解析失败或工具不可用时停止，不写出部分新平台。"""
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"{arguments[0]} failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def existing_version(core, project):
    """追加时从既有业务包读取精确版本；不把新模板默认版本强加给旧工程。"""
    manifest = read_tool_json(["swift", "package", "--package-path", str(core), "dump-package"])
    for dependency in manifest["dependencies"]:
        for item in dependency.get("sourceControl", []):
            if item["location"].get("remote") == [{"urlString": PACKAGE_URL}]:
                exact = item["requirement"].get("exact")
                if exact:
                    spec = read_tool_json(["xcodegen", "dump", "--spec", str(project), "--type", "json"])
                    for package in spec.get("packages", {}).values():
                        url = package.get("url", "").rstrip("/").removesuffix(".git")
                        if url == PACKAGE_URL.removesuffix(".git") and package.get("exactVersion") != exact[0]:
                            raise ValueError("existing project and business package AppleAppKit versions disagree")
                    return exact[0]
    raise ValueError("existing business package must pin AppleAppKit to an exact version")


def write_workspace(destination, name):
    """已有 workspace 由项目维护；只在两端齐备且不存在时生成组织入口。"""
    workspace = destination / f"{name}.xcworkspace"
    if workspace.exists() or workspace.is_symlink():
        return
    workspace.mkdir()
    root = ET.Element("Workspace", version="1.0")
    for platform in ("ios", "macos"):
        ET.SubElement(root, "FileRef", location=f"group:{platform}/{name}.xcodeproj")
    ET.indent(root)
    ET.ElementTree(root).write(workspace / "contents.xcworkspacedata", encoding="utf-8", xml_declaration=True)


def main():
    """保留 ios/macos 参数，apple 创建双端；--add-platform 要求已有同名四层工程。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("ios", "macos", "apple"), required=True)
    parser.add_argument("--name", required=True, help="合法 Swift 类型标识，如 MyApp")
    parser.add_argument("--bundle-id", required=True, help="单端为完整 ID；apple 模式追加 .ios/.macos")
    parser.add_argument("--output", type=Path, required=True, help="父目录；新布局为 <output>/<name>/ios 或 macos")
    parser.add_argument("--team-id", default="", help="10 位 DEVELOPMENT_TEAM，可稍后配置")
    parser.add_argument("--skeleton", type=Path, default=Path(__file__).resolve().parents[2], help="统一仓库根目录")
    parser.add_argument("--add-platform", action="store_true", help="只追加尚不存在的 ios 或 macos，不覆盖原工程")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.name):
        parser.error("--name must be a valid Swift type identifier")
    # 由 Swift 自身拒绝关键字与特殊标识，不维护容易遗漏的关键字副本。
    syntax = subprocess.run(
        ["swiftc", "-frontend", "-parse", "-"], input=f"struct {args.name} {{}}\n", capture_output=True, text=True,
    )
    if syntax.returncode:
        parser.error("--name must be a valid Swift type identifier")
    if not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", args.bundle_id):
        parser.error("--bundle-id must contain only identifier segments separated by dots")
    if args.team_id and not re.fullmatch(r"[A-Z0-9]{10}", args.team_id):
        parser.error("--team-id must be 10 uppercase letters or digits")
    if args.add_platform and args.platform == "apple":
        parser.error("--add-platform requires ios or macos")
    platforms = ("ios", "macos") if args.platform == "apple" else (args.platform,)
    templates = args.skeleton.resolve() / "apple/Templates"
    for part in ("common", *(f"{platform}-app" for platform in platforms)):
        if not (templates / part).is_dir():
            parser.error(f"template not found: {templates / part}")
    destination = args.output.expanduser().resolve() / args.name
    version = PACKAGE_VERSION
    if args.add_platform:
        core = destination / f"packages/{args.name}Core"
        other = "macos" if args.platform == "ios" else "ios"
        if destination.is_symlink() or not (core / "Package.swift").is_file() or not (destination / other / "project.yml").is_file():
            parser.error("--add-platform requires an existing generated project with the other platform")
        target = destination / args.platform
        if target.exists() or target.is_symlink():
            parser.error(f"platform already exists: {target}")
        try:
            version = existing_version(core, destination / other / "project.yml")
        except (ValueError, OSError, subprocess.TimeoutExpired) as error:
            parser.error(str(error))
    elif destination.exists() or destination.is_symlink():
        parser.error(f"destination already exists: {destination}")

    replacements = {
        "__APP_NAME__": args.name,
        "__BUNDLE_ID__": args.bundle_id,
        "__TEAM_ID__": args.team_id,
        "__PACKAGE_URL__": PACKAGE_URL,
        "__PACKAGE_VERSION__": version,
        "__PACKAGE_ID__": "dwy-ai-experience",
    }
    # 在临时生成物中完成替换，失败不会改动已有平台。
    with tempfile.TemporaryDirectory(prefix="dwy-apple-template-") as folder:
        staged = Path(folder) / args.name
        if args.add_platform:
            staged.mkdir()
        else:
            render_tree(templates / "common", staged, replacements)
        for platform in platforms:
            platform_replacements = dict(replacements)
            if args.platform == "apple":
                platform_replacements["__BUNDLE_ID__"] += f".{platform}"
            render_tree(templates / f"{platform}-app", staged / platform, platform_replacements)
        if args.add_platform:
            shutil.copytree(staged / args.platform, destination / args.platform)
        else:
            # copytree 的 exist_ok=False 同时保护空目录和并发创建的目标。
            shutil.copytree(staged, destination)
    if all((destination / platform / "project.yml").is_file() for platform in ("ios", "macos")):
        write_workspace(destination, args.name)
    print(f"Created {destination}")
    print("Four layers: App -> Features/BusinessUI -> BizFoundation -> AppleAppKit")
    print(f"Business tests: swift test --package-path packages/{args.name}Core")
    for platform in platforms:
        print(f"Generate {platform}: cd {destination / platform} && xcodegen generate")
    print("Architecture: python3 scripts/check-architecture.py")


if __name__ == "__main__":
    main()
