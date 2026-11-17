#!/usr/bin/env python3
"""从任意目录检查生成项目；需要 SwiftPM 与 XcodeGen，不解析或更新远端依赖。"""
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPKIT = "https://github.com/danweiyuancircle/dwy-ai-experience"
UI_MODULES = {"SwiftUI", "UIKit", "AppKit", "StoreKit", "PurchaseCore", "DesignCore"}


def run_json(arguments):
    """只调用原生结构化输出；工具失败时不能把未检查的项目当作通过。"""
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"{arguments[0]} 失败：{result.stderr.strip()[:2000]}")
    return json.loads(result.stdout)


def location(url):
    return url.rstrip("/").removesuffix(".git")


def sources(directory, entries=None, excludes=(), includes=()):
    """按原生配置的 sources/exclude 收集文件；不重新实现 Swift 或 YAML 语法。"""
    files = set()
    for entry in entries if entries is not None else ["."]:
        path = (directory / entry).resolve()
        candidates = [path] if path.is_file() else path.rglob("*.swift")
        for file in candidates:
            relative = file.relative_to(directory).as_posix()
            if includes and not any(fnmatch.fnmatch(relative, pattern) for pattern in includes):
                continue
            if file.suffix == ".swift" and not any(
                relative == pattern or relative.startswith(pattern.rstrip("/") + "/")
                or fnmatch.fnmatch(relative, pattern) for pattern in excludes
            ):
                files.add(file.resolve())
    return files


def imports(path):
    # shortcut: 文本导入检查不识别宏展开或动态引用，复杂语义仍由编译和架构审查验证。
    text = re.sub(r"//[^\n]*|/\*[\s\S]*?\*/", "", path.read_text())
    return re.findall(
        r"^[\t ]*(?:@\w+(?:\([^\n]*?\))?[\t ]+)*import[\t ]+"
        r"(?:(?:typealias|struct|class|enum|protocol|let|var|func)[\t ]+)?([A-Za-z_]\w*)",
        text, re.M,
    )


def version_key(version):
    release, _, prerelease = version.split("+", 1)[0].partition("-")
    numbers = tuple(int(value) for value in release.split("."))
    suffix = (1,) if not prerelease else (0, tuple(
        (0, int(value)) if value.isdigit() else (1, value) for value in prerelease.split(".")
    ))
    return numbers, suffix


def version_requirement(requirement):
    if "exact" in requirement:
        return ("exact", requirement["exact"][0])
    if "range" in requirement:
        value = requirement["range"][0]
        return ("range", value["lowerBound"], value["upperBound"])
    return tuple((key, tuple(value)) for key, value in sorted(requirement.items()))


def project_requirement(package):
    if "exactVersion" in package:
        return ("exact", package["exactVersion"])
    for key in ("from", "minimumVersion", "majorVersion", "minorVersion"):
        if key in package:
            lower = str(package[key])
            parts = [int(part) for part in lower.split(".")]
            upper = f"{parts[0]}.{parts[1] + 1}.0" if key == "minorVersion" else f"{parts[0] + 1}.0.0"
            return ("range", lower, upper)
    for key in ("branch", "revision"):
        if key in package:
            return ((key, (package[key],)),)
    raise ValueError("远端 package 缺少可核对的版本约束")


def check(root):
    """校验四层与平台边界；返回问题列表，不修改工程、锁文件或环境设置。"""
    errors = []
    manifests = {}
    projects = {}
    requirements = {}
    compiled_by_package = {}
    target_modules = {}
    app_modules = set()

    def report(path, message):
        errors.append(f"{path.relative_to(root) if path.is_relative_to(root) else path}: {message}")

    def register(url, requirement, path):
        key = location(url)
        if key == APPKIT and requirement[0] != "exact":
            report(path, "AppleAppKit 必须使用 exact 精确版本")
        previous = requirements.get(key)
        if previous and previous[0] != requirement:
            report(path, f"依赖版本不一致，与 {previous[1].relative_to(root)} 冲突")
        requirements[key] = (requirement, path)

    for platform in ("ios", "macos"):
        spec = root / platform / "project.yml"
        if spec.is_file():
            project = run_json(["xcodegen", "dump", "--spec", str(spec), "--type", "json"])
            projects[platform] = project
            app_modules.update(name for name, target in project["targets"].items() if target["type"] == "application")
    if not projects:
        return ["没有找到 ios/project.yml 或 macos/project.yml"]

    pending = list((root / "packages").glob("*/Package.swift"))
    pending += [root / platform / "Package.swift" for platform in projects if (root / platform / "Package.swift").is_file()]
    for platform, project in projects.items():
        spec = root / platform / "project.yml"
        for package in project.get("packages", {}).values():
            if "url" in package:
                register(package["url"], project_requirement(package), spec)
            elif "path" in package:
                path = (spec.parent / package["path"] / "Package.swift").resolve()
                if not path.is_relative_to(root):
                    report(spec, "内部包 path 必须位于项目内")
                elif not path.is_file():
                    report(spec, f"找不到本地包 {path.relative_to(root)}")
                else:
                    if path.relative_to(root).parts[0] in ("ios", "macos") and path.relative_to(root).parts[0] != platform:
                        report(spec, "禁止引用另一平台的本地包")
                    pending.append(path)

    while pending:
        path = pending.pop().resolve()
        if path in manifests:
            continue
        package = run_json(["swift", "package", "--package-path", str(path.parent), "dump-package"])
        manifests[path] = package
        for dependency in package["dependencies"]:
            if "sourceControl" in dependency:
                value = dependency["sourceControl"][0]
                remote = value["location"].get("remote")
                if remote:
                    register(remote[0]["urlString"], version_requirement(value["requirement"]), path)
            elif "fileSystem" in dependency:
                local = (Path(dependency["fileSystem"][0]["path"]) / "Package.swift").resolve()
                if not local.is_relative_to(root):
                    report(path, "内部包 path 必须位于项目内")
                elif not local.is_file():
                    report(path, f"找不到本地包 {local.relative_to(root)}")
                else:
                    owner = local.relative_to(root).parts[0]
                    current = path.relative_to(root).parts[0]
                    if owner in ("ios", "macos") and owner != current:
                        report(path, "共享包或本端包禁止依赖另一平台实现")
                    pending.append(local)

        platform = path.relative_to(root).parts[0]
        for target in package["targets"]:
            name = target["name"]
            target_modules[name] = platform
            if name == "Foundation":
                report(path, "target 禁止命名为 Foundation（与系统框架冲突）")
            folder = (path.parent / target.get("path", f"{'Tests' if target['type'] == 'test' else 'Sources'}/{name}")).resolve()
            if not folder.is_relative_to(path.parent):
                report(path, f"target {name} 源码越出包目录：{folder.relative_to(root) if folder.is_relative_to(root) else folder}")
                continue
            files = sources(folder, target.get("sources"), target["exclude"])
            for file in files:
                compiled_by_package.setdefault(file, []).append((path, name, target["type"]))

    def forbidden(module):
        return module in UI_MODULES or module.startswith("DesignKit") or module.endswith("UI") or module in app_modules

    for file, owners in compiled_by_package.items():
        if len(owners) > 1:
            report(file, "源码重复编译：同时属于多个 SPM target")

    for path, package in manifests.items():
        platform = path.relative_to(root).parts[0]
        is_core = platform == "packages" and path.parent.name.endswith("Core")
        for target in package["targets"]:
            if target["type"] == "test":
                continue
            name = target["name"]
            dependencies = [value[0] for dependency in target["dependencies"] for value in dependency.values()]
            for module in dependencies:
                owner = target_modules.get(module)
                if is_core and (forbidden(module) or owner in ("ios", "macos")):
                    report(path, f"{name}（③ BizFoundation）禁止依赖 {module}")
                if platform in ("ios", "macos") and owner in ("ios", "macos") and owner != platform:
                    report(path, f"{name} 禁止依赖另一平台 {module}")
            for file, owners in compiled_by_package.items():
                if (path, name, target["type"]) not in owners:
                    continue
                for module in imports(file):
                    owner = target_modules.get(module)
                    if is_core and (forbidden(module) or owner in ("ios", "macos")):
                        report(file, f"{name}（③ BizFoundation）禁止 import {module}")
                    if platform == "ios" and (module in {"AppKit", "DesignKitMac", "MacUI"} or owner == "macos"):
                        report(file, f"iOS 禁止 import {module}")
                    if platform == "macos" and (module in {"UIKit", "DesignKitIOS", "IOSUI"} or owner == "ios"):
                        report(file, f"macOS 禁止 import {module}")

    for platform, project in projects.items():
        spec = root / platform / "project.yml"
        app_files = set()
        linked_targets = {}
        for app in project["targets"].values():
            if app["type"] != "application":
                continue
            for dependency in app.get("dependencies", []):
                alias = dependency.get("package")
                package = project.get("packages", {}).get(alias, {})
                if "path" not in package:
                    continue
                manifest = (spec.parent / package["path"] / "Package.swift").resolve()
                if manifest not in manifests:
                    continue
                value = manifests[manifest]
                targets = {target["name"]: target for target in value["targets"]}
                pending = [target for product in value["products"] if product["name"] == dependency.get("product", alias) for target in product["targets"]]
                reached = linked_targets.setdefault(manifest, set())
                while pending:
                    target = pending.pop()
                    if target in reached:
                        continue
                    reached.add(target)
                    if target in targets:
                        pending.extend(
                            names[0] for item in targets[target]["dependencies"]
                            for kind, names in item.items() if kind in ("byName", "target") and names[0] in targets
                        )
        for name, target in project["targets"].items():
            if target["type"] != "application":
                continue
            for dependency in target.get("dependencies", []):
                module = dependency.get("product", dependency.get("target", dependency.get("package", "")))
                owner = target_modules.get(module)
                if platform == "ios" and (module in {"DesignKitMac", "MacUI", "AuthGoogleMac", "PermissionMac"} or owner == "macos"):
                    report(spec, f"iOS 禁止链接另一平台 product {module}")
                if platform == "macos" and (module in {"DesignKitIOS", "IOSUI", "AuthGoogleIOS", "AuthAppleIOS", "PermissionIOS"} or owner == "ios"):
                    report(spec, f"macOS 禁止链接另一平台 product {module}")
            for entry in target.get("sources", []):
                value = {"path": entry} if isinstance(entry, str) else entry
                folder = (spec.parent / value["path"]).resolve()
                if not folder.exists() and not value.get("optional", False):
                    report(spec, f"{name} source 不存在：{value['path']}")
                if value.get("buildPhase") == "resources" or value.get("type") == "folder":
                    continue
                # XcodeGen 的 excludes 相对于 source 条目目录，而不是该目录的父目录。
                files = (sources(folder, excludes=value.get("excludes", []), includes=value.get("includes", []))
                         if folder.is_dir() else sources(folder.parent, [folder.name], value.get("excludes", []), value.get("includes", [])))
                for file in files:
                    if not file.is_relative_to(spec.parent):
                        report(spec, f"{name} 不得直接编译本端以外的源码：{file.relative_to(root) if file.is_relative_to(root) else file}")
                    if file in app_files or file in compiled_by_package:
                        report(file, "源码重复编译：同时属于多个 source 或 App/SPM target")
                    app_files.add(file)
                    for module in imports(file):
                        owner = target_modules.get(module)
                        if platform == "ios" and (module in {"AppKit", "DesignKitMac", "MacUI"} or owner == "macos"):
                            report(file, f"iOS 禁止 import {module}")
                        if platform == "macos" and (module in {"UIKit", "DesignKitIOS", "IOSUI"} or owner == "ios"):
                            report(file, f"macOS 禁止 import {module}")
        for directory in ("App", "Features", "BusinessUI"):
            for file in (spec.parent / directory).rglob("*.swift"):
                if file.resolve() not in app_files:
                    report(file, "本端 UI 源码未编译：加入 App sources")
        for file in (spec.parent / "Platform").rglob("*.swift"):
            owners = compiled_by_package.get(file.resolve(), [])
            if file.resolve() not in app_files and not owners:
                report(file, "平台源码未编译：加入本端 App sources 或 Package target")
            for manifest, target, kind in owners:
                if kind == "test":
                    report(file, "平台源码只能由生产 target 编译")
                if target not in linked_targets.get(manifest, set()):
                    report(file, "平台 target 未编译进 App：project.yml 必须链接对应 product")

    locked = {}
    locks = set(root.glob("packages/*/Package.resolved")) | {root / platform / "Package.resolved" for platform in projects}
    locks |= set(root.glob("**/*.xcworkspace/xcshareddata/swiftpm/Package.resolved"))
    for path in sorted(locks):
        if not path.is_file():
            continue
        content = json.loads(path.read_text())
        for pin in content.get("pins", content.get("object", {}).get("pins", [])):
            url = pin.get("location", pin.get("repositoryURL", ""))
            key = location(url)
            state = pin["state"]
            if key in requirements:
                requirement = requirements[key][0]
                if requirement[0] == "exact" and state.get("version") != requirement[1]:
                    report(path, "锁文件版本与 exact 声明不一致")
                if requirement[0] == "range" and (
                    not state.get("version")
                    or not version_key(requirement[1]) <= version_key(state["version"]) < version_key(requirement[2])
                ):
                    report(path, "锁文件版本不在声明范围内")
            if key in locked and locked[key] != state:
                report(path, "锁文件同一依赖的版本/revision 不一致")
            locked[key] = state
    return errors


def main():
    """输出明确的检查结果；依赖解析与真实编译/交互仍需另行执行。"""
    try:
        errors = check(ROOT)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"架构检查未完成：{error}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("四层架构检查通过（结构与导入边界；不代替编译、语义审查或设备验收）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
