---
source_url: https://code.claude.com/docs/zh-CN/skills, https://code.claude.com/docs/zh-CN/commands
fetched_at: "2026-05-19"
category: A
fetched_via: WebFetch
summary: 自定义 slash command 已合并到 skills。本文件覆盖 .claude/commands/*.md 兼容写法 + 内置 commands 速查
---

# Slash Commands（自定义 + 内置）

## 0. 重要前提

> **自定义命令已合并到 skills 中。** `.claude/commands/deploy.md` 中的文件和 `.claude/skills/deploy/SKILL.md` 中的 skill 都会创建 `/deploy` 并以相同的方式工作。你现有的 `.claude/commands/` 文件继续工作。Skills 添加了可选功能：支持文件的目录、控制你或 Claude 是否调用它们的 frontmatter，以及 Claude 在相关时自动加载它们的能力。

（来源：https://code.claude.com/docs/zh-CN/skills，缓存于 2026-05-19）

**结论**：
- **新写一律走 SKILL.md 形态**，看 [references/skills.md](skills.md)
- 已有 `.claude/commands/*.md` 兼容运行，但**没有** `references/` / `scripts/` 等扩展能力
- 内置 commands 由 CLI 硬编码，**不能**自定义同名

## 1. 自定义 command 文件位置

| 位置 | 路径 | 范围 |
|------|------|------|
| 项目级 | `.claude/commands/<name>.md` | 仅本项目 |
| 用户级 | `~/.claude/commands/<name>.md` | 本机所有项目 |

文件名 = 命令名。`<name>.md` → `/<name>`。

**重名时 skill 优先于 command**（同 scope）。

## 2. 文件结构

跟 SKILL.md 完全一样：YAML frontmatter + markdown body。**frontmatter 字段集与 skill 完全相同**（见 [references/skills.md 第 4 节](skills.md#4-frontmatter-完整字段表)）。

简单示例：

```markdown
---
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---

# Commit

Stage all changes and create a commit. $ARGUMENTS becomes the commit message.

1. Run `git status` to see changes
2. Run `git diff --staged`
3. Commit with message: $ARGUMENTS
```

调用：`/commit fix: 修正登录跳转`

## 3. 从 .claude/commands/ 迁移到 SKILL.md（推荐）

迁移步骤：

```bash
# 原：.claude/commands/deploy.md
# 改：.claude/skills/deploy/SKILL.md

mkdir -p .claude/skills/deploy
mv .claude/commands/deploy.md .claude/skills/deploy/SKILL.md
```

内容不需改。迁移后获得能力：
- 可以加 `references/`、`scripts/`、`examples/` 子目录
- 可以用 `${CLAUDE_SKILL_DIR}` 引用资源
- 可以用 `context: fork` 切到 subagent 跑

## 4. 命名规则

| 规则 | 说明 |
|------|------|
| **kebab-case** | `my-command.md`，不用 `_` 不用大写 |
| **不冲突内置** | `/init / /compact / /clear / /memory / /help / /context / /skills / /agents / /mcp / ...` 不要重名 |
| **最多 64 字符** | 跟 skill name 字段一致 |

## 5. 调用语义

- 命令**仅在消息开头**识别：`/<name>` 加在消息中间不会被识别
- 命令名后的文本作为参数传给 `$ARGUMENTS` / `$N`：`/fix-issue 123` → `$ARGUMENTS=123`、`$0=123`
- 索引参数用 shell 风格引号：`/cmd "hello world" second` → `$0=hello world`、`$1=second`

## 6. 内置 commands 速查（≠ 自定义）

按工作流分类列举常用项：

### 项目初始化
- `/init` — 生成初始 CLAUDE.md。`CLAUDE_CODE_NEW_INIT=1` 启用交互式多阶段流程
- `/memory` — 查看 / 编辑 CLAUDE.md、CLAUDE.local.md、rules 文件，切换 auto memory

### 配置
- `/agents` — 管理 subagent 配置（推荐用 UI 而非手写文件）
- `/mcp` — 管理 MCP 服务器连接和 OAuth
- `/permissions` — 管理 allow/ask/deny 规则
- `/hooks` — 查看 hooks 配置（只读）
- `/skills` — 列出可用 skills，按 token 数排序，调整可见性
- `/plugin` — 管理 plugins

### 会话控制
- `/clear` — 新开对话，旧的保留在 `/resume` 列表
- `/compact [instructions]` — 总结当前对话释放 context
- `/context` — 可视化 context 使用，显示优化建议
- `/resume [session]` — 恢复某次对话
- `/branch [name]` — 在当前位置分叉对话
- `/rewind` — 回滚到 checkpoint

### 模型 / 推理
- `/model [model]` — 切模型
- `/effort [level]` — 调努力级别（low/medium/high/xhigh/max）
- `/plan [description]` — 进入 plan mode
- `/fast [on|off]` — 切换 fast mode

### 工作流（多为 bundled skill）
- `/debug` — **bundled skill**。开调试日志 + 分析问题
- `/simplify [focus]` — **bundled skill**。检视近期改动，跑 3 个 reviewer agent，应用修复
- `/batch <instr>` — **bundled skill**。大规模改动分解到 5-30 个独立单元，每个 worktree 并行
- `/loop [interval] [prompt]` — **bundled skill**。按间隔重复跑 prompt
- `/btw <q>` — 不进对话历史的旁问
- `/review [PR]` — 本地 review PR
- `/security-review` — 当前分支安全审计
- `/diff` — 交互式 diff 查看器

### 诊断
- `/doctor` — 诊断安装与设置
- `/usage` — 会话花费、计划用量、活动统计
- `/feedback [report]` — 反馈 bug

### 其他
- `/help` — 帮助
- `/exit` 或 `/quit` — 退出 CLI
- `/config` — 设置界面
- `/theme` — 主题切换
- `/copy [N]` — 复制最后 / 第 N 个响应到剪贴板
- `/export [filename]` — 导出对话为纯文本

完整清单（含平台限定项如 `/desktop` / `/upgrade`）见 https://code.claude.com/docs/zh-CN/commands

## 7. 区分自定义 command 与 bundled skill

内置 commands 表里标 **[Skill]** 的（如 `/simplify`、`/batch`、`/debug`、`/loop`、`/claude-api`）是 **bundled skill**：本质是基于提示的 skill，跟你自己写的 skill 调用机制相同；其他无标签的是硬编码 built-in command。区别：

| 类型 | 实现 | 可否自定义同名 |
|------|------|---------------|
| 内置 built-in command（无 [Skill]）| CLI 硬编码 | ❌ 不能 |
| Bundled skill（有 [Skill]）| Anthropic 提供的 SKILL.md，与你写的一样 | ❌ 用户级覆盖能改但不建议 |
| 自定义 skill / command | 你写的 SKILL.md 或 .claude/commands/*.md | ✅ |

## 8. MCP prompts 作为命令

MCP 服务器可以暴露 prompts 作为命令，格式 `/mcp__<server>__<prompt>`，从已连接服务器动态发现。详见 https://code.claude.com/docs/zh-CN/mcp

## 9. 常见踩坑

- **命名冲突**：自定义 `/init` 会被忽略（内置 `/init` 占用）。先看 `/help` 列表
- **文件不在 `.claude/commands/` 直接根**：放子目录会变成 namespace（如 `.claude/commands/git/foo.md` → 子命令路径行为按 skill 规则）
- **混淆字段集**：`.claude/commands/*.md` 字段集 = SKILL.md 字段集，**不**含 subagent 的 `tools`（注意不是 `allowed-tools`）`permissionMode`、`mcpServers` 等字段
- **没加 `disable-model-invocation`**：高副作用命令（commit / deploy / send-message）若不加此字段，Claude 可能自动调用，造成意外
- **在 commands/ 里用 supporting files 不生效**：要 supporting files 必须迁移到 skills/

## 10. 引用本文件

回答时引用任何条款都附 `（来源：<上述 source_url 之一>，缓存于 2026-05-19）`。

字段详表统一指向 references/skills.md（避免重复维护）。
