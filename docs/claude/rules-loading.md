# Claude Code Rules 加载机制

来源：[官方文档 — Memory](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/)

## 一句话

`.claude/rules/*.md` 是 Claude Code 官方一等公民。文件 frontmatter 有 `paths` 字段则按文件 glob 触发，没有就启动时全量注入。

## 目录约定

| 位置 | 作用域 |
|---|---|
| `~/.claude/rules/*.md` | 用户级，所有项目生效 |
| `.claude/rules/*.md` | 项目级，团队共享（提交进版本库） |

支持递归子目录（`rules/frontend/*.md`）和 symlink。

## 两种加载模式

### 1. 无 `paths` — 启动全量注入

```markdown
---
description: 任意备注（Claude Code 不读此字段，仅供人看）
---

# 任意规则正文…
```

加载时机：**会话启动**。优先级与 `.claude/CLAUDE.md` 相同。
适用：项目通用约定、提交规范、技术栈约束。

### 2. 有 `paths` — 按文件 glob 触发

```markdown
---
paths:
  - "**/*.py"
  - "src/**/*.{ts,tsx}"
---

# 仅当 Claude 读取匹配文件时才注入
```

加载时机：**Claude 用 Read/Edit/Write 触碰匹配文件时**，不是每次 tool use。
适用：语言/模块特定规则（Python 安全、Vue 组件规范、Flutter 路由）。

## 支持的 glob 模式

| 模式 | 匹配 |
|---|---|
| `**/*.ts` | 任意目录下的 ts 文件 |
| `src/**/*` | `src/` 下所有文件 |
| `*.md` | 项目根的 md |
| `src/components/*.tsx` | 指定目录下的 tsx |
| `src/**/*.{ts,tsx}` | 多扩展名（brace expansion） |

## 优先级

加载顺序由广到窄，后加载的优先级更高：

```
managed CLAUDE.md
  → user ~/.claude/CLAUDE.md
  → user ~/.claude/rules/
  → project .claude/CLAUDE.md
  → project .claude/rules/
  → CLAUDE.local.md
```

## Rules vs CLAUDE.md vs Skills

| 机制 | 加载时机 | 用途 |
|---|---|---|
| `CLAUDE.md` | 启动全量 | 项目根级总则（构建、规范、架构） |
| `rules/*.md`（无 paths） | 启动全量 | CLAUDE.md 拆分模块化 |
| `rules/*.md`（有 paths） | 读匹配文件时 | 语言/目录特定规则 |
| `skills/<name>/SKILL.md` | 模型按 description 自行决定调用 | 任务工作流、可选流程 |

**选择原则**：每次都要遵守 → rules；偶尔触发的工作流 → skills。

## 调试

- `/memory` — 列出当前会话已加载的 CLAUDE.md + rules
- `InstructionsLoaded` hook — 记录每个规则文件加载时机和原因

## dwy 项目当前状态

`dwy-cli/templates/claude-global/rules/` 下文件通过 `dwy sync claude` 同步到 `~/.claude/rules/`，所有项目生效。

- 无 `paths`：`dwy-tdd-development.md`、`dwy-db-migration.md` 等 → 每次启动注入
- 有 `paths`：`dwy-python-backend.md` (`**/*.py`)、`dwy-vue-core.md` (Vue 相关) 等 → 读对应文件时注入

`description` 字段官方未使用，dwy 保留它作为人工注释/搜索关键字。
