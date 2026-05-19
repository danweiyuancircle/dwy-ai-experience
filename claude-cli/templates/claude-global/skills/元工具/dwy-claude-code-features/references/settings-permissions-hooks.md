---
source_url: https://code.claude.com/docs/zh-CN/settings, https://code.claude.com/docs/zh-CN/permissions, https://code.claude.com/docs/zh-CN/hooks
fetched_at: "2026-05-19"
category: E
fetched_via: WebFetch
summary: settings.json、permissions 规则、hooks 配置的横向参考（不是主要查询入口，被 A-D 引用时来这查具体字段）
---

# Settings / Permissions / Hooks 横向参考

这是 A-D 文件引用到 `settings.json` 配置、permissions 规则、hooks 事件时的字段速查。**不是主要查询入口**。

## 1. settings.json 位置与优先级

| 层级 | 位置 | 范围 | 优先级 |
|------|------|------|--------|
| Managed | macOS `/Library/Application Support/ClaudeCode/managed-settings.json`、Linux `/etc/claude-code/managed-settings.json`、Windows `C:\ProgramData\ClaudeCode\managed-settings.json` | 组织全员 | 1 最高 |
| Local | `.claude/settings.local.json` | 本机此项目（应进 .gitignore） | 2 |
| Project | `.claude/settings.json` | 团队共享 | 3 |
| User | `~/.claude/settings.json` | 仅你 | 4 |
| CLI flag | `--xxx` | 单次会话 | 介于 User 与 Local |

**permissions 数组跨层级合并**（不覆盖）。其他字段后者覆盖前者。

## 2. 核心字段速查

### permissions
```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Read(./src/**)"],
    "deny": ["Bash(curl *)", "Read(.env*)"],
    "ask": ["Bash(git push *)"],
    "additionalDirectories": ["../docs/"],
    "defaultMode": "default"
  }
}
```
- 规则语法：`Tool(pattern)`，glob 风格
- 优先级：**deny > ask > allow**（首个匹配即止）
- `defaultMode`: `default / acceptEdits / plan / auto / dontAsk / bypassPermissions`

### env / claudeMd / agent
```json
{
  "env": { "NODE_ENV": "development" },
  "claudeMd": "Always run lint before committing.",
  "agent": "code-reviewer"
}
```
- `claudeMd` **仅 managed 层有效**
- `agent` 设默认 subagent，整个 session 用该 subagent 系统提示

### auto memory
```json
{
  "autoMemoryEnabled": false,
  "autoMemoryDirectory": "~/my-mem"
}
```
- `autoMemoryDirectory` **仅 policy/user/CLI** 接受（防项目级劫持）

### skillOverrides
```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```
4 种状态：`on / name-only / user-invocable-only / off`。`/skills` 菜单可视化配置。

### claudeMdExcludes
```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```
跨层级合并，managed 层 CLAUDE.md 不能被排除。

### hooks
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/scripts/check.sh" }
        ]
      }
    ]
  }
}
```

### Managed-only 字段（仅 managed-settings.json 生效）

- `allowManagedPermissionRulesOnly`
- `allowManagedHooksOnly`
- `allowManagedMcpServersOnly`
- `allowedMcpServers / deniedMcpServers`
- `claudeMd`
- `forceLoginMethod / forceLoginOrgUUID`

## 3. Hook 事件全清单

### 会话生命周期
- `SessionStart` — 会话开始或恢复
- `Setup` — `--init-only / --init / --maintenance` 时
- `SessionEnd` — 会话终止

### 每轮事件
- `UserPromptSubmit` — 用户提交 prompt
- `UserPromptExpansion` — slash command 展开时
- `Stop` — Claude 完成响应
- `StopFailure` — 因 API 错误结束

### 工具执行（Agentic Loop）
- `PreToolUse` — 工具调用前
- `PermissionRequest` — 权限对话框出现时
- `PermissionDenied` — 工具被 auto-mode 分类器拒绝
- `PostToolUse` — 工具成功后
- `PostToolUseFailure` — 工具失败后
- `PostToolBatch` — 并行工具批次结束后

### Agent / Task
- `SubagentStart` — subagent 启动
- `SubagentStop` — subagent 完成
- `TaskCreated` — TaskCreate 创建任务
- `TaskCompleted` — 任务标 completed
- `TeammateIdle` — agent team 队友即将 idle

### 环境 / 上下文
- `InstructionsLoaded` — CLAUDE.md 或 `.claude/rules/*.md` 加载时（debug 友好）
- `ConfigChange` — 配置文件变化
- `CwdChanged` — 工作目录变化
- `FileChanged` — watched 文件变化
- `Notification` — Claude Code 发通知

### 压缩 / Worktree
- `PreCompact / PostCompact` — context 压缩前后
- `WorktreeCreate / WorktreeRemove` — `--worktree` 创建/移除

### MCP
- `Elicitation` — MCP 服务器请求用户输入
- `ElicitationResult` — 用户响应后

## 4. Hook Types

```json
{
  "type": "command",   // shell 命令，stdin/stdout
  "type": "http",      // HTTP POST endpoint
  "type": "mcp_tool",  // 调 MCP server 工具
  "type": "prompt",    // 发 prompt 给 Claude
  "type": "agent"      // spawn subagent（实验性）
}
```

## 5. Matcher 语法

| 模式 | 解析 | 示例 |
|------|------|------|
| `"*"` / `""` / 省略 | 匹配全部 | 每次都触发 |
| 仅字母数字下划线和 `\|` | 精确串或 `\|` 分隔列表 | `Bash`、`Edit\|Write` |
| 其他字符 | JavaScript 正则 | `^Notebook`、`mcp__memory__.*` |

### 按事件类型的 matcher

| 事件 | 匹配 | 示例 |
|------|------|------|
| 工具事件 (PreToolUse 等) | 工具名 | `Bash`、`Edit\|Write` |
| `SessionStart` | 启动方式 | `startup / resume / clear / compact` |
| `SessionEnd` | 结束原因 | `clear / resume / logout / other` |
| `Notification` | 通知类型 | `permission_prompt / idle_prompt` |
| `SubagentStart/Stop` | agent 类型名 | `general-purpose / Explore / 自定义` |
| `PreCompact/PostCompact` | 触发 | `manual / auto` |
| `FileChanged` | 文件名 | `.envrc\|.env` |

## 6. Command hook 字段

```json
{
  "type": "command",
  "command": "/path/to/script.sh",
  "args": [],
  "shell": "bash",
  "async": false,
  "asyncRewake": false,
  "if": "Bash(git *)",
  "timeout": 600,
  "statusMessage": "Checking...",
  "once": false
}
```

**exec form**（`args` 存在）：直接 spawn，无 shell，变量当字符串
**shell form**（无 `args`）：shell 调用，支持 `|`、`&&`、glob

### 路径占位符

```
${CLAUDE_PROJECT_DIR}    # 项目根
${CLAUDE_PLUGIN_ROOT}    # 插件安装目录
${CLAUDE_PLUGIN_DATA}    # 插件持久数据目录
```

## 7. 退出码语义

| 退出码 | 含义 |
|--------|------|
| 0 | 成功；JSON 输出被处理 |
| 2 | **阻塞性错误**；stderr 给 Claude，操作被拒 |
| 其他 | 非阻塞错误；stderr 显示，继续执行 |

### Exit 0 的 JSON 输出结构

```json
{
  "continue": true,
  "stopReason": "Build failed",
  "decision": "block",
  "reason": "Why blocked",
  "suppressOutput": false,
  "systemMessage": "Warning text",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "...",
    "additionalContext": "Context for Claude"
  }
}
```

## 8. 最小可工作示例（阻止 rm -rf）

`.claude/settings.json`：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/block-rm.sh`：
```bash
#!/bin/bash
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)
if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive rm -rf blocked"
    }
  }'
else
  exit 0
fi
```

## 9. Skill / Subagent frontmatter 中的 hooks

跟 settings.json 同结构，写在 frontmatter：

```yaml
---
name: my-skill
description: Skill with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
          once: true
---
```

**配置层级合并顺序**（从低到高优先）：
1. Claude Code 默认
2. Plugin `hooks/hooks.json`
3. User `~/.claude/settings.json`
4. Project `.claude/settings.json`
5. Project `.claude/settings.local.json`
6. Managed policy settings（user/project 不能禁用）
7. Skill / Agent frontmatter hooks（session-scoped）

## 10. 禁用所有 hooks

```json
{
  "disableAllHooks": true
}
```
Managed hooks 不能在 user/project 层禁用。

## 11. 引用本文件

回答时附 `（来源：<对应 source_url>，缓存于 2026-05-19）`，多源时列举各自 URL。

跨主题：
- subagent 自带 hooks → references/subagents.md 第 9 节
- skill 自带 hooks → references/skills.md（hooks 字段）
- CLAUDE.md 大小限制等 → references/memory-rules.md
