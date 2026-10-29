# 版本号多文件同步

版本号定好后，**同一工程中代表该版本的来源文件必须一致**；不同工程的独立版本不要求相同。先核对项目实际版本来源，不假设所有技术栈都存在表中全部文件。

## 各技术栈版本来源清单

| 技术栈 | 版本来源文件 | 字段 |
|------|------|------|
| Python | `pyproject.toml` + 包 `__init__.py` | `version` / `__version__` |
| Node/Vue | `package.json` | `version` |
| Android | `build.gradle(.kts)` | `versionName`（语义号）+ `versionCode`（整数，每次发布递增） |
| iOS | `Info.plist` 或 `project.pbxproj` | `CFBundleShortVersionString`（语义号）+ `CFBundleVersion`（build 号，见 `ios.md`） |
| 鸿蒙 | `oh-package.json5` | `version` |

## 规则

- **Python**：项目同时维护 `pyproject.toml` 的 `version` 与包 `__init__.py` 的 `__version__` 时，两处必须一致。
- **Android**：`versionName` 用语义版本号；新上传构建的 `versionCode` 遵循渠道及项目的递增要求。
- **iOS**：`CFBundleShortVersionString` 用语义版本号；`CFBundleVersion`（build 号）规则见 `ios.md`。
- 改完后用 grep 全仓库扫一遍旧版本号，确认无遗漏：

```bash
grep -rn "<旧版本号>" --include=pyproject.toml --include=package.json --include="*.gradle*" --include="*.plist" --include="oh-package.json5" .
```

## 禁止

- 禁止漏改项目实际维护的版本来源（如已有的 `__init__.py` 版本）
- 禁止用会自动 commit 的版本命令（`npm version` / `bumpversion` 等），直接编辑文件，保持提交边界可控
- 重新上传构建时遵循对应应用商店的构建号要求；直接重部署已记录的相同产物可复用原构建号。
