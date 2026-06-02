---
name: dwy-publish
description: "发布版本：测试 → bump → changelog → build → publish → tag。触发条件：用户说'发版'、'发布'、'release'、'bump version' 时。"
---

# 发布版本流程

通用的发版流程框架，项目特定的包名、路径、命令由 CLAUDE.md 的 `## Release` 段落定义。

## 触发条件

用户要求发布包时（"发版"、"发布"、"release"、"bump version"）。

## 第 0 步：检查项目 Release 配置

**在执行任何操作前**，检查当前项目的 CLAUDE.md 是否包含 `## Release` 段落：

- **有** → 读取其中的包列表、版本文件路径、测试命令、构建命令、发布命令、依赖顺序等配置，按配置执行
- **没有** → **停止发版流程**，提醒用户：

> 「当前项目 CLAUDE.md 未定义 `## Release` 段落，无法执行发版流程。需要我帮你加吗？」

参考格式（提供给用户）：

```markdown
## Release

### 包列表

| 包名 | scope | 版本文件 | 测试命令 | 构建命令 | 发布命令 | 验证命令 |
|------|-------|---------|---------|---------|---------|---------|
| @scope/pkg-a | pkg-a | packages/a/package.json | cd packages/a && pnpm vitest run | pnpm build:a | pnpm publish:a | npm view @scope/pkg-a version |

### 依赖顺序

多包发版时按此顺序执行：pkg-a → pkg-b → pkg-c

### Tag 命名

- 单包：`@scope/pkg-a@1.0.0`
- 仅一个包时可简化为：`v1.0.0`

### CHANGELOG

- 命令：`pnpm changelog`（可选，无则手写）
- 工具：changelogen
```

## 发版前置检查（按项目类型）

正式发版前，先按项目类型过对应的前置 skill：

- **SDK 类项目（对外发布的库 / SDK，不限 PyPI / npm / 私有源）** → 先用 `dwy-sdk-spec` 做发布安全检查（接口注释脱敏、商业版源码保护、发布产物审计），通过后再发版。
- **含 C 扩展 / Cython / .so、需跨平台 wheel** → 用 `dwy-cibuildwheel` 配 GitHub Actions + cibuildwheel 打跨平台 wheel 发 PyPI（此时下方第 4、6 步的 build / publish 由 CI workflow 承担）。
- **版本号该升哪一位拿不准** → 用 `dwy-semver` 决策（见下方第 2 步）。

## 发版前确认

询问用户：

1. **发哪个包？**（从 Release 配置的包列表中选，可多选）
2. **版本号？** patch / minor / major，或指定具体版本号

## 发版流程

### 1. 运行测试

执行 Release 配置中对应包的测试命令。**测试必须全部通过才能继续。**

**有失败 → 停止发版，修复后重新开始。**

### 2. Bump Version

**版本级别（major/minor/patch）该怎么定** —— 不确定时用 `dwy-semver` skill 决策，它给出该升哪一位 + 具体新版本号（含 0.x 阶段、预发布、归零规则）。

根据 Release 配置中的版本文件路径，直接编辑 version 字段。新版本号用 `dwy-semver` 的 `scripts/bump.py` 算，避免手算归零出错：

```bash
python3 <dwy-semver>/scripts/bump.py <当前版本> <major|minor|patch>
# 如 1.2.3 minor -> 1.3.0
```

不使用 `npm version`（避免自动 commit）。Python 项目编辑 `pyproject.toml` 中的 `version` 字段。

### 3. 编写 CHANGELOG

**如果项目有 changelog 自动生成工具**（如 changelogen），执行配置的命令。

**如果没有**，手动编写 CHANGELOG 条目：

1. 查看上个版本 tag 以来的 git log：`git log <last-tag>..HEAD --oneline`
2. 按变更类型分组（feat / fix / refactor / chore）
3. 写入项目的 CHANGELOG.md，格式：

```markdown
## x.y.z

### Minor Changes / Patch Changes

- 变更描述 1
- 变更描述 2
```

**CHANGELOG 未写不发版。**

### 4. Build

执行 Release 配置中对应包的构建命令。**构建必须成功才能继续。**

### 5. Commit + Tag

```bash
# 暂存变更（version + changelog）
git add <changed-files>

# 提交（遵循 dwy-git-commit）
git commit -m "chore(<scope>): release v<version>"

# 打 tag（按 Release 配置的命名规则）
git tag <tag-name>

# 推送
git push origin <branch> --tags
```

### 6. Publish

执行 Release 配置中对应包的发布命令。

### 7. 发版后验证

执行 Release 配置中对应包的验证命令，确认新版本已发布。

## 多包同时发版

按 Release 配置中定义的依赖顺序，每个包独立走完 测试 → bump → changelog → build → publish，最后统一 commit + tag + push。

## 禁止事项

- **禁止**跳过测试直接发版
- **禁止**跳过 build 直接 publish
- **禁止**忘记打 tag
- **禁止**publish 失败后不回滚 version 变更
- **禁止**在 CHANGELOG 未编写时发版
- **禁止**在无 Release 配置的情况下猜测发版命令
