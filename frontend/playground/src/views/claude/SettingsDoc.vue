<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const CB = '```'

const content = `# Claude Code Settings

## 概述

\`settings.json\` 是 Claude Code 的全局配置文件，位于 \`~/.claude/settings.json\`。当前配置主要定义了 **Hooks**（钩子），用于在 Claude 执行特定工具前后自动运行自定义脚本。

## 完整配置

${CB}json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/pre-git-commit-sensitive-check.sh"
          }
        ]
      }
    ]
  }
}
${CB}

## 字段说明

### hooks

钩子配置的顶层对象，按触发时机分类。

### hooks.PreToolUse

**工具调用前**触发的钩子数组。每个条目包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| \`matcher\` | string | 匹配的工具名称。\`"Bash"\` 表示拦截所有 Bash 工具调用 |
| \`hooks\` | array | 匹配后要执行的钩子列表 |

### hooks[].hooks[]

具体的钩子定义：

| 字段 | 类型 | 说明 |
|------|------|------|
| \`type\` | string | 钩子类型，目前支持 \`"command"\`（执行 shell 命令） |
| \`command\` | string | 要执行的命令。脚本可通过 \`$TOOL_INPUT\` 环境变量获取工具输入内容 |

### 钩子退出码

| 退出码 | 行为 |
|--------|------|
| 0 | 通过，继续执行工具调用 |
| 1 | 拒绝，阻止工具调用 |
| 2 | 暂停，等待用户人工审批后决定 |

## 当前配置的钩子

### pre-git-commit-sensitive-check.sh

- **触发时机**: 每次 Claude 调用 Bash 工具时
- **实际拦截**: 仅当命令包含 \`git commit\` 时才执行检查
- **功能**: 扫描 git 暂存区中是否包含密码、API Key、私钥等敏感数据
- **详细文档**: [查看 Hook 文档](#/claude/hooks/pre-git-commit-sensitive-check)

## 其他可用的 Hook 时机

| Hook 类型 | 触发时机 |
|-----------|---------|
| \`PreToolUse\` | 工具调用前 |
| \`PostToolUse\` | 工具调用后 |
| \`Notification\` | 通知事件时 |
| \`Stop\` | 对话结束时 |

## 安装方式

通过 \`create-dwy\` CLI 工具自动同步：

${CB}bash
npx create-dwy claude-sync
${CB}

该命令会将模板中的 settings.json、hooks、skills、rules 同步到 \`~/.claude/\` 目录。`
</script>

<template>
  <DocPage :content="content" title="Settings 配置" />
</template>
