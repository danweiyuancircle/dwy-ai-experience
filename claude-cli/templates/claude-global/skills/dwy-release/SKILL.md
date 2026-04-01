---
name: dwy-release
description: "标准化发版流程：bump version → changelog → build → publish → git tag。触发条件：用户说'发版'、'发布'、'release'、'bump version' 时。"
---

# 标准化发版流程

通用的发版流程框架，项目特定的包名、路径、命令由 CLAUDE.md 的 `## Release` 段落定义。

## 触发条件

用户要求发布包时（"发版"、"发布"、"release"、"bump version"）。

## 第 0 步：检查项目 Release 配置

**在执行任何操作前**，检查当前项目的 CLAUDE.md 是否包含 `## Release` 段落：

- **有** → 读取其中的包列表、版本文件路径、构建命令、发布命令、依赖顺序等配置，按配置执行
- **没有** → **停止发版流程**，提醒用户：

> 「当前项目 CLAUDE.md 未定义 `## Release` 段落，无法执行发版流程。需要我帮你加吗？」

参考格式（提供给用户）：

```markdown
## Release

### 包列表

| 包名 | scope | 版本文件 | 构建命令 | 发布命令 | 验证命令 |
|------|-------|---------|---------|---------|---------|
| @scope/pkg-a | pkg-a | packages/a/package.json | pnpm build:a | pnpm publish:a | npm view @scope/pkg-a version |

### 依赖顺序

多包发版时按此顺序执行：pkg-a → pkg-b → pkg-c

### Tag 命名

- 单包：`@scope/pkg-a@1.0.0`
- 仅一个包时可简化为：`v1.0.0`

### CHANGELOG

- 命令：`pnpm changelog`
- 工具：changelogen
```

## 发版前确认

询问用户：

1. **发哪个包？**（从 Release 配置的包列表中选，可多选）
2. **版本号？** patch / minor / major，或指定具体版本号

## 发版流程

### 1. Bump Version

根据 Release 配置中的版本文件路径，直接编辑 version 字段。

```bash
# 读取当前版本（根据配置的版本文件）
# 计算新版本：patch=x.y.z+1, minor=x.y+1.0, major=x+1.0.0
```

不使用 `npm version`（避免自动 commit）。Python 项目编辑 `pyproject.toml` 中的 `version` 字段。

### 2. Generate CHANGELOG

执行 Release 配置中定义的 changelog 命令。检查生成内容，确认无误后继续。

### 3. Build

执行 Release 配置中对应包的构建命令。**构建必须成功才能继续。**

### 4. Commit + Tag

```bash
# 暂存变更（version + changelog）
git add <changed-files>

# 提交（遵循 git-commit-convention）
git commit -m "chore(<scope>): release v<version>"

# 打 tag（按 Release 配置的命名规则）
git tag <tag-name>

# 推送
git push origin <branch> --tags
```

### 5. Publish

执行 Release 配置中对应包的发布命令。

### 6. 发版后验证

执行 Release 配置中对应包的验证命令，确认新版本已发布。

## 多包同时发版

按 Release 配置中定义的依赖顺序，每个包独立走完 bump → build → publish，最后统一 commit + tag + push。

## 禁止事项

- **禁止**跳过 build 直接 publish
- **禁止**忘记打 tag
- **禁止**publish 失败后不回滚 version 变更
- **禁止**在 CHANGELOG 未生成时发版
- **禁止**在无 Release 配置的情况下猜测发版命令
