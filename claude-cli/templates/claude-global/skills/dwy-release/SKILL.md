---
name: dwy-release
description: "标准化发版流程：bump version → changelog → build → publish → git tag。触发条件：用户说'发版'、'发布'、'release'、'bump version' 时。"
---

# DWY 标准化发版流程

## 触发条件

用户要求发布以下任一包时：
- `@danweiyuan/eui`
- `@danweiyuan/core`
- `danweiyuan-base`（PyPI）
- `create-dwy`

## 发版前确认

先询问用户：

1. **发哪个包？** eui / core / backend / cli（可多选）
2. **版本号？** patch / minor / major，或指定具体版本号

## 发版流程

### 1. Bump Version

根据用户选择的包修改对应 `package.json`（或 `pyproject.toml`）中的 version 字段。

| 包 | 版本文件 |
|---|---------|
| eui | `frontend/eui/package.json` |
| core | `frontend/core/package.json` |
| backend | `backend/pyproject.toml` |
| cli | `claude-cli/package.json` |

```bash
# 读取当前版本
node -e "console.log(require('./frontend/eui/package.json').version)"

# 计算新版本（示例：1.2.0 → patch=1.2.1, minor=1.3.0, major=2.0.0）
```

直接编辑文件中的 version 字段，不使用 npm version（避免自动 commit）。

### 2. Generate CHANGELOG

```bash
# 生成 changelog（基于上次 tag 到当前的 conventional commits）
pnpm changelog
```

检查生成的 CHANGELOG.md 内容，确认无误后继续。

### 3. Build

根据包执行对应构建：

```bash
# eui
pnpm build:eui

# core
pnpm build:core

# backend（无构建步骤，publish 时自动 build）

# cli（无构建步骤）
```

构建必须成功才能继续。

### 4. Commit + Tag

```bash
# 暂存变更的文件（version + changelog）
git add <changed-files>

# 提交（遵循 git-commit-convention）
git commit -m "chore(<scope>): release v<version>"

# 打 tag
git tag v<version>
# 如果是包级 tag：git tag <package>@<version>

# 推送
git push origin master --tags
```

Tag 命名规则：
- 单包发布：`@danweiyuan/eui@1.3.0`、`@danweiyuan/core@1.1.0`、`danweiyuan-base@0.3.0`、`create-dwy@0.6.0`
- 多包同时发布：每个包各打一个 tag

### 5. Publish

```bash
# eui
pnpm publish:eui

# core
pnpm publish:core

# backend
pnpm publish:backend

# cli
pnpm publish:cli
```

### 6. 发版后验证

```bash
# npm 包验证
npm view @danweiyuan/eui version
npm view @danweiyuan/core version
npm view create-dwy version

# PyPI 包验证
pip index versions danweiyuan-base 2>/dev/null || echo "检查 https://pypi.org/project/danweiyuan-base/"
```

### 7. 发版后同步（仅 CLI 发版时）

如果发布了 `create-dwy`，触发 `dwy-auto-sync` 流程。
注意：如果只是修改了 skills/rules 等配置内容，不需要发 CLI 新版，推送到 Gitee 即可。

## 多包同时发版

如果同时发布多个包，按依赖顺序执行：
1. `@danweiyuan/core`（被 eui 依赖）
2. `@danweiyuan/eui`
3. `danweiyuan-base`（独立）
4. `create-dwy`（独立）

每个包独立走完 bump → build → publish 流程后，统一 commit + tag + push。

## 禁止事项

- **禁止**跳过 build 直接 publish
- **禁止**忘记打 tag
- **禁止**publish 失败后不回滚 version 变更
- **禁止**在 CHANGELOG 未生成时发版
