---
source_url: https://code.claude.com/docs/zh-CN/sub-agents
fetched_at: "2026-05-19"
category: D
fetched_via: WebFetch
summary: Claude Code subagents 官方规范：文件位置与优先级、frontmatter 全字段表（含必填 name + description）、内置 subagents、调用方式、fork 模式
---

# Subagents

## 1. 官方定义

> Subagents 是处理特定类型任务的专门 AI 助手。当一个辅助任务会用搜索结果、日志或文件内容充斥你的主对话，而你不会再次引用这些内容时，请使用一个 subagent：该 subagent 在自己的上下文中完成这项工作，仅返回摘要。

每个 subagent 在自己的 **独立 context window** 中运行，有自定义系统提示、特定工具访问权限、独立权限。

（来源：https://code.claude.com/docs/zh-CN/sub-agents，缓存于 2026-05-19）

## 2. 内置 subagents

| 名称 | Model | 工具 | 用途 |
|------|-------|------|------|
| **Explore** | Haiku | 只读（Read/Glob/Grep/...）| 代码库搜索 / 文件发现 / 探索。**跳过 CLAUDE.md 和 git status** |
| **Plan** | 继承主对话 | 只读 | plan mode 期间的代码库研究。**跳过 CLAUDE.md 和 git status** |
| **general-purpose** | 继承主对话 | 全部工具 | 多步骤复杂任务（探索 + 修改）|
| statusline-setup | Sonnet | -- | `/statusline` 配置时自动用 |
| claude-code-guide | Haiku | -- | 用户问 Claude Code 功能时自动用 |

**关键事实**：内置 subagents（除 Explore/Plan 外）都加载 CLAUDE.md 和 git status；自定义 subagents 也加载。**Subagent 不能再生成 subagent**（防无限嵌套）。

## 3. 文件位置与优先级

| 位置 | 范围 | 优先级 |
|------|------|--------|
| 托管设置 (managed) | 组织全员 | 1 最高 |
| `--agents` CLI 标志（JSON 内联）| 当前会话 | 2 |
| `.claude/agents/<name>.md` | 当前项目 | 3 |
| `~/.claude/agents/<name>.md` | 所有项目 | 4 |
| Plugin `agents/` 目录 | 启用插件处 | 5 最低 |

- 重名时**高优先级覆盖低优先级**
- 项目 subagents 通过**向上遍历**当前目录发现；**`--add-dir` 加入的目录不会扫描 subagents**
- `.claude/agents/` 和 `~/.claude/agents/` 都**递归扫描**，可用子文件夹组织（如 `agents/review/security.md`），子目录不影响 subagent 身份（只看 `name` 字段）
- 同一 scope 内**两个文件声明同一 name 会被静默丢一个，无警告**
- Plugin 的子文件夹会成为命名空间的一部分：`my-plugin:review:security`

### 直接添加文件需重启会话

> Subagents 在会话启动时加载。如果你直接在磁盘上添加或编辑 subagent 文件，请重启你的会话以加载它。通过 `/agents` 界面创建的 Subagents **无需重启即可立即生效**。

## 4. Frontmatter 完整字段表

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

**仅 `name` 和 `description` 必需。** 正文是 system prompt。

| 字段 | 必需 | 含义 |
|------|------|------|
| `name` | **Yes** | 唯一标识，小写字母 + 连字符。**hooks 收到此值作 `agent_type`**。文件名不必与 name 一致 |
| `description` | **Yes** | Claude 何时该委派此 subagent |
| `tools` | No | 工具白名单。**逗号分隔**字符串或 YAML 列表。**省略则继承所有**（含 MCP） |
| `disallowedTools` | No | 黑名单，从继承或 tools 列表中移除。两者都设时 disallowedTools 先应用 |
| `model` | No | `sonnet/opus/haiku`、完整 ID（`claude-opus-4-7`）或 `inherit`。**默认 `inherit`** |
| `permissionMode` | No | `default/acceptEdits/auto/dontAsk/bypassPermissions/plan`。plugin subagent 忽略此字段 |
| `maxTurns` | No | 代理轮次上限 |
| `skills` | No | **预加载**到 subagent context 的 skills 列表。注入完整内容，不是仅 description。subagent 仍可通过 Skill 工具调用未列出的 skill |
| `mcpServers` | No | 限定到此 subagent 的 MCP 服务器。每项是字符串引用（`"slack"`）或内联定义（含完整 MCP 配置）。plugin subagent 忽略此字段 |
| `hooks` | No | 生命周期 hooks（PreToolUse/PostToolUse/Stop）。plugin subagent 忽略此字段 |
| `memory` | No | `user/project/local`，启用跨会话学习 |
| `background` | No | `true` 始终后台运行。默认 false |
| `effort` | No | `low/medium/high/xhigh/max`。覆盖会话级 |
| `isolation` | No | `worktree` = 在临时 git worktree 运行（隔离副本）。无更改时自动清理 worktree |
| `color` | No | `red/blue/green/yellow/purple/orange/pink/cyan`。任务列表显示色 |
| `initialPrompt` | No | 作为主会话 agent 运行时（`--agent` 或 `agent` setting），自动作为第一条用户消息提交。前置于用户提示 |

## 5. tools / disallowedTools 语法

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

```yaml
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

特殊：`Agent(<sub-name>, <sub-name>)` 限制能 spawn 的 subagent 类型（仅 `claude --agent` 主线程模式有意义）：

```yaml
tools: Agent(worker, researcher), Read, Bash
```

- 不写 `Agent` → 不能 spawn 任何 subagent
- 写 `Agent` 无括号 → 可 spawn 任意

## 6. permissionMode 6 种取值

| 模式 | 行为 |
|------|------|
| `default` | 标准权限检查，带提示 |
| `acceptEdits` | 自动接受文件编辑和工作目录内常见 fs 命令 |
| `auto` | 后台分类器审查命令和受保护目录写入 |
| `dontAsk` | 自动拒绝权限提示（显式允许的工具仍工作）|
| `bypassPermissions` | **跳过所有权限提示**（极危险，根目录 `rm -rf /` 仍拦截）|
| `plan` | Plan mode（只读探索）|

**父子继承规则**：父 `bypassPermissions` 或 `acceptEdits` 时**优先于子**，子 frontmatter 无效。父 `auto` 时子的 `permissionMode` 被忽略，分类器用父规则评估。

## 7. memory 字段（持久知识库）

```yaml
---
name: code-reviewer
description: Reviews code for quality
memory: project
---

You are a code reviewer. As you review code, update your agent memory with patterns,
conventions, and recurring issues you discover.
```

| 范围 | 位置 | 用于 |
|------|------|------|
| `user` | `~/.claude/agent-memory/<name>/` | 跨项目复用的领域知识 |
| `project` | `.claude/agent-memory/<name>/` | 项目特定，可 git 共享。**推荐默认** |
| `local` | `.claude/agent-memory-local/<name>/` | 项目特定，不进 git |

启用 memory 后：
- 系统提示自动加 memory 读写说明
- 系统提示包含 `MEMORY.md` **前 200 行或 25KB**（先到者优先）
- **Read/Write/Edit 工具自动启用**

## 8. mcpServers 字段

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  # 内联定义：仅此 subagent 用
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # 字符串引用：复用已配置的服务器
  - github
---
```

- 内联定义在 subagent 启动时连接、完成时断开
- 字符串引用共享父会话连接
- 内联定义 schema 同 `.mcp.json`（stdio/http/sse/ws）
- 想让 MCP 只对 subagent 可见、**不消耗主对话 context**，用内联方式

## 9. hooks 字段（subagent 生命周期）

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
```

支持所有 hook 事件，最常用：
| 事件 | matcher | 触发 |
|------|---------|------|
| `PreToolUse` | 工具名（`Bash`、`Edit\|Write`、`mcp__.*`）| subagent 用工具前 |
| `PostToolUse` | 工具名 | subagent 用工具后 |
| `Stop` | （无）| subagent 完成时（运行时转 `SubagentStop`）|

## 10. 启动时加载到 subagent context 的内容

非 fork subagent 启动时收到：
- **系统提示**：agent 自己的 prompt + Claude Code 附加的环境详情。**不是完整 Claude Code 系统提示**
- **任务消息**：Claude 写的委派 prompt
- **CLAUDE.md 和 memory**：所有层级（managed/user/project/local）。**Explore 和 Plan 跳过**
- **Git status**：父会话开始时的快照。Explore 和 Plan 跳过
- **预加载 skills**：`skills` 字段列的 skill 完整内容

> 主对话用完整 CLAUDE.md 上下文读取 Explore 和 Plan 结果，所以大多数规则不需要到达 subagent 本身。如果规则必须，例如"忽略 vendor/ 目录"，在你给 Claude 委派的提示中重新陈述它。

## 11. 调用方式（3 种）

### 自然语言
```text
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

### @-mention（保证用此 subagent）
```text
@"code-reviewer (agent)" look at the auth changes
```
- plugin 提供的 subagent：`@agent-my-plugin:code-reviewer`
- 子文件夹：`@agent-my-plugin:review:security`

### 整个会话作为 subagent 跑
```bash
claude --agent code-reviewer
```
subagent 的系统提示**完全替换**默认 Claude Code 系统提示（同 `--system-prompt`）。

```json
// .claude/settings.json
{
  "agent": "code-reviewer"
}
```

### CLI 内联定义（一次性）
```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer.",
    "prompt": "You are a senior code reviewer.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

## 12. 前台 vs 后台运行

| | 前台 | 后台 |
|---|------|------|
| 是否阻塞主对话 | ✅ | ❌ 并发 |
| 权限提示 | 传给你 | **自动拒绝**任何会提示的工具调用 |
| 触发方式 | 默认 | `background: true` frontmatter / Claude 主动选择 / Ctrl+B 后台化 / 用户说 "run in background" |

`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` 禁用所有后台任务。

## 13. fork 模式（实验性）

需要 v2.1.117+ 和 `CLAUDE_CODE_FORK_SUBAGENT=1`。

| | Fork | 命名 subagent |
|---|------|--------------|
| 上下文 | **完整对话历史** | 新鲜上下文 |
| 系统提示 + 工具 | 与主会话相同 | 来自定义文件 |
| 模型 | 与主会话相同 | 来自 `model` 字段 |
| 权限提示 | 你的终端 | 后台时**自动拒绝** |
| Prompt cache | 与主会话**共享** | 单独缓存 |

启用后：
- Claude 在原本用 general-purpose 的场景用 fork
- 所有 subagent 生成都进**后台**
- `/fork <directive>` 命令生成 fork（不再是 `/branch` 别名）

## 14. 最小骨架（复制即用）

### 只读 reviewer

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- ...

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

### debugger

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. ...
```

### 带 hook 的 db-reader

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries.
```

## 15. 常见踩坑

- **不写 `tools` 字段**：默认继承全部工具（含 MCP），可能让"只读 agent"意外有 Write 权限。**read-only 角色必须显式 `tools: Read, Grep, Glob, Bash`**
- **body 不 self-contained**：subagent **看不到主对话**，body 必须把任务上下文 / 角色 / 输出格式说全
- **重名静默丢**：同 scope 重名 = 一个被丢，无警告。检查 `~/.claude/agents/` 和 `.claude/agents/` 的 name 唯一性
- **`mcpServers` 写在 plugin subagent**：plugin subagent **忽略** `hooks / mcpServers / permissionMode` 字段，不报错但不生效
- **嵌套委派幻觉**：subagent **不能** spawn subagent。需嵌套用 skills 或主对话链式
- **memory 滥用**：`memory: project` 会在 `.claude/agent-memory/<name>/` 落盘并进 git，临时调研类 agent 不要开
- **`bypassPermissions` 滥用**：能写 `.git`、`.claude`、`.vscode` 等，谨慎

## 16. 引用本文件

回答时引用任何条款都附 `（来源：https://code.claude.com/docs/zh-CN/sub-agents，缓存于 2026-05-19）`。

跨主题：
- skill 与 subagent 关系 → references/skills.md 第 9 节
- hook 完整事件清单 → references/settings-permissions-hooks.md
- 字段对比 → references/comparison-matrix.md
