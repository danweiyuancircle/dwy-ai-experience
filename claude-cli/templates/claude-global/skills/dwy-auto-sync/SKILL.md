---
name: dwy-auto-sync
description: "create-dwy 发版后自动更新本地 CLI 并同步 Claude Code 配置。触发条件：执行了 npm publish create-dwy、pnpm publish:cli、或用户要求同步 dwy 配置时。"
---

# DWY 发版后自动同步

当 `create-dwy` 发布新版本后，必须执行以下步骤确保本地 Claude Code 配置与最新版本同步。

## 触发时机

以下任一情况发生时，执行同步流程：

1. 执行了 `npm publish`（在 claude-cli 目录下）
2. 执行了 `pnpm publish:cli`
3. 用户要求"同步 dwy"或"更新配置"

## 同步流程

发版成功后，按顺序执行：

```bash
# 1. 更新全局 CLI 到最新版
npm i -g create-dwy@latest

# 2. 验证版本
dwy --version

# 3. 同步 Claude Code 配置（skills/rules/hooks/commands/settings）
dwy sync claude

# 4. 验证同步结果
ls ~/.claude/skills/
```

## 同步了什么

`dwy sync claude` 会将以下内容从 CLI 模板同步到 `~/.claude/`：

| 目录 | 内容 | 同步方式 |
|------|------|---------|
| `~/.claude/skills/` | AI 速查文档 (dwy-frontend-eui, dwy-frontend-core, dwy-backend-base) | 覆盖同名，保留已有 |
| `~/.claude/rules/` | 编码规范 (python-code-style, vue-code-style, 安全规则等) | 覆盖同名，保留已有 |
| `~/.claude/hooks/` | 自动化脚本 (pre-git-commit 检查) | 覆盖同名，保留已有 |
| `~/.claude/commands/` | 自定义命令 | 覆盖同名，保留已有 |
| `~/.claude/settings.json` | Claude Code 设置 | 浅合并（新 key 加入，同名覆盖，已有独有 key 保留） |

## 注意事项

- npm 注册表有传播延迟（~1 分钟），如果 `npm i -g create-dwy@latest` 安装的不是刚发布的版本，等待后重试
- `dwy sync claude` 从 Gitee 仓库拉取模板，确保代码已 push 到 Gitee 后再执行
- 同步不会删除用户手动添加的 skills/rules，只覆盖同名文件
