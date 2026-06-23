# 版本号多文件同步

版本号定好后，**同一次发布的所有版本来源文件必须改到完全一致**。一个技术栈往往有多处版本声明，漏改一处就会导致包内版本不一致、构建产物版本错乱。

## 各技术栈版本来源清单

| 技术栈 | 版本来源文件 | 字段 |
|------|------|------|
| Python | `pyproject.toml` + 包 `__init__.py` | `version` / `__version__` |
| Node/Vue | `package.json` | `version` |
| Android | `build.gradle(.kts)` | `versionName`（语义号）+ `versionCode`（整数，每次发布递增） |
| iOS | `Info.plist` 或 `project.pbxproj` | `CFBundleShortVersionString`（语义号）+ `CFBundleVersion`（build 号，见 `sdk-ios.md`） |
| 鸿蒙 | `oh-package.json5` | `version` |

## 规则

- **Python**：`pyproject.toml` 的 `version` 与包 `__init__.py` 的 `__version__` 两处必须一致。
- **Android**：`versionName` 用语义版本号；`versionCode` 是单调递增整数，与语义号无关，每次发布 +1。
- **iOS**：`CFBundleShortVersionString` 用语义版本号；`CFBundleVersion`（build 号）用时间戳，规则见 `sdk-ios.md`。
- 改完后用 grep 全仓库扫一遍旧版本号，确认无遗漏：

```bash
grep -rn "<旧版本号>" --include=pyproject.toml --include=package.json --include="*.gradle*" --include="*.plist" --include="oh-package.json5" .
```

## 禁止

- 禁止只改一处版本来源就发布（如只改 `pyproject.toml` 漏改 `__init__.py`）
- 禁止用会自动 commit 的版本命令（`npm version` / `bumpversion` 等），直接编辑文件，保持提交边界可控
- 禁止 `versionCode` / `CFBundleVersion` 不递增就重发（应用商店会拒）
