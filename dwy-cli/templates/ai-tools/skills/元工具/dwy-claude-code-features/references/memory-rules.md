---
source_url: https://code.claude.com/docs/zh-CN/memory
fetched_at: "2026-05-19"
category: B
fetched_via: WebFetch
summary: CLAUDE.md / .claude/rules/ / auto memory 官方规范：加载位置与优先级、@path import、paths frontmatter、auto memory 机制
---

# CLAUDE.md / Rules / Auto Memory

## 1. 两套记忆系统

| | CLAUDE.md 文件 | Auto memory |
|---|---------------|-------------|
| **谁写** | 你 | Claude 自己 |
| **内容** | 指令和规则 | 学习模式和发现 |
| **范围** | 项目 / 用户 / 组织 | 每个 git 仓库 |
| **加载** | 每个会话（**完整**加载） | 每个会话加载 MEMORY.md 前 200 行或 25KB |
| **用于** | 编码标准、工作流、项目架构 | 构建命令、调试见解、Claude 发现的偏好 |

（来源：https://code.claude.com/docs/zh-CN/memory，缓存于 2026-05-19）

## 2. CLAUDE.md 文件位置与加载顺序

按加载顺序从广到窄（**所有发现的文件全部拼接进 context**，不互相覆盖）：

| 范围 | 位置 | 共享 |
|------|------|------|
| **托管策略** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux/WSL: `/etc/claude-code/CLAUDE.md`<br>Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | 组织全员，**不能被排除** |
| **用户指令** | `~/.claude/CLAUDE.md` | 仅你，所有项目 |
| **项目指令** | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队（git 管理） |
| **本地指令** | `./CLAUDE.local.md` | 仅你，当前项目（应进 `.gitignore`） |

加载机制：
- 从工作目录**向上遍历**到根，每层有 `CLAUDE.md` 和 `CLAUDE.local.md` 都加载
- 文件系统根 → 工作目录方向拼接，**距工作目录越近排越后**
- 同一目录内 `CLAUDE.local.md` 在 `CLAUDE.md` **之后**追加
- 子目录的 `CLAUDE.md` **不在启动加载**，Claude 读取该子目录文件时再加载

## 3. `.claude/rules/*.md` 的角色

```text
your-project/
├── .claude/
│   ├── CLAUDE.md           # 主项目指令
│   └── rules/
│       ├── code-style.md   # 全局生效（无 paths）
│       ├── api-design.md   # 仅 src/api/** 触发
│       └── testing.md
```

跟 CLAUDE.md 的区别：
- **递归发现**所有 `.md`，可建子目录如 `frontend/`、`backend/`
- 支持 `paths` frontmatter **按文件路径范围加载**，省 token
- 没 `paths` 字段 = 启动时全量加载，优先级与 `.claude/CLAUDE.md` 相同
- 有 `paths` 字段 = **Claude 读取匹配文件时才加载**，不是每次工具调用

### paths 字段语法

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---

# API 开发规则
- 所有 API 端点必须包括输入验证
```

支持 glob 与大括号扩展：

| 模式 | 匹配 |
|------|------|
| `**/*.ts` | 所有 TypeScript 文件 |
| `src/**/*` | `src/` 下所有文件 |
| `*.md` | 项目根的 markdown |
| `src/**/*.{ts,tsx}` | 大括号扩展 |

### 用户级 rules

`~/.claude/rules/*.md` 也支持，对所有项目生效。**用户级在项目级之前**加载（项目级优先级高）。

## 4. @path import 语法

CLAUDE.md 可以 import 其他文件：

```text
有关项目概述，请参阅 @README，有关此项目的可用 npm 命令，请参阅 @package.json。

# 其他指令
- git 工作流 @docs/git-instructions.md
- 个人偏好 @~/.claude/my-project-instructions.md
```

约束：
- 允许相对路径 + 绝对路径 + `~/`
- 相对路径基于**包含 import 的文件**（不是工作目录）
- 可递归 import，**最大深度 5 hop**
- 启动时完整展开进 context（与 paths 范围加载不同，import 全量进）
- **第一次遇到外部 import** 时 Claude Code 会弹批准对话框；拒绝后 import 永久禁用

## 5. AGENTS.md 兼容

Claude Code **不直接读** AGENTS.md，需要 CLAUDE.md 里 import：

```markdown CLAUDE.md
@AGENTS.md

## Claude Code

对 src/billing/ 下的更改使用 Plan Mode。
```

或建符号链接（Windows 需管理员权限或开发者模式）：

```bash
ln -s AGENTS.md CLAUDE.md
```

运行 `/init` 时如果有 `AGENTS.md`、`.cursorrules`、`.windsurfrules`，会读取并合并到生成的 CLAUDE.md。

## 6. 写好 CLAUDE.md 的官方建议

| 维度 | 推荐 |
|------|------|
| **大小** | 目标 **< 200 行**。超过用 paths-scoped rules 拆分 |
| **结构** | markdown 标题 + 项目符号分组 |
| **具体性** | "使用 2 空格缩进" > "格式化代码"；"在提交前运行 `npm test`" > "测试" |
| **一致性** | 多文件别给冲突指令；用 `claudeMdExcludes` 跳无关团队的 CLAUDE.md |
| **注释** | 块级 HTML 注释 `<!-- xxx -->` 在注入 context 前**剥离**（省 token），代码块内保留 |

## 7. 何时该用 CLAUDE.md 何时该用 skill

> 当你不断将相同的说明、检查清单或多步骤程序粘贴到聊天中时，或者当 CLAUDE.md 的一部分已经演变成程序而不是事实时，**创建一个 skill**。

判断标准：
- **事实** → CLAUDE.md（"项目用 pnpm，不要用 npm"）
- **流程 / 多步操作** → skill
- **仅特定文件类型相关** → `.claude/rules/` + `paths`
- **必须在某个时点强制执行** → hook（不是 CLAUDE.md）

## 8. 大型团队 / 管理员配置

### 部署组织 CLAUDE.md
放到上面"托管策略"位置，由 MDM / Group Policy / Ansible 分发。**个人设置不能排除**。

### managed-settings.json 内嵌
```json
{
  "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
}
```
只在 managed/policy 层有效。

### 排除特定文件（monorepo 场景）

```json
// .claude/settings.local.json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

模式是 glob，**绝对路径**匹配。可在任意 settings 层级配置，数组跨层合并。**managed 层 CLAUDE.md 不能排除**。

## 9. Auto Memory（自动记忆）

> 自动记忆让 Claude 跨会话积累知识，无需你编写任何内容。

需要 Claude Code v2.1.59+。

### 配置

```json
// 项目 settings
{
  "autoMemoryEnabled": false   // 默认 true
}

// 用户 settings (~/.claude/settings.json)
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

或环境变量 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` 关闭。

### 存储位置

`~/.claude/projects/<project>/memory/`（`<project>` 来自 git 仓库路径，**所有 worktree 共享一份**）

```text
memory/
├── MEMORY.md          # 简洁索引，启动时加载前 200 行 / 25KB
├── debugging.md       # 详细笔记，按需加载
└── api-conventions.md
```

- `MEMORY.md` 是机器可读 + 人可读的索引；超 200 行后 Claude 会主动把内容挪到主题文件
- 主题文件**不在启动时加载**，Claude 需要时读
- `autoMemoryDirectory` 必须绝对路径或 `~/` 开头；**仅 policy 和 user settings 接受**（防止恶意项目重定向）

### /memory 命令

会话内运行 `/memory` 列出当前加载的 CLAUDE.md / CLAUDE.local.md / rules 文件，可切换 auto memory 开关，可打开 auto memory 目录。

## 10. 故障排查

| 现象 | 排查 |
|------|------|
| Claude 不遵循 CLAUDE.md | 跑 `/memory` 看是否加载；指令更具体；查多文件冲突 |
| 文件太大 | 用 paths-scoped rules 拆；@import 不省 context，只是组织 |
| `/compact` 后指令丢失 | **项目根** CLAUDE.md 自动重新注入；**嵌套** CLAUDE.md 仅在 Claude 读相关文件时重新加载 |
| 必须强制的规则 | 改用 hook 替代 CLAUDE.md。CLAUDE.md 是软引导不是强制 |
| 想看具体加载了哪些 | `InstructionsLoaded` hook 可以记录加载日志 |

## 11. 关键限制

- **CLAUDE.md 不是系统提示**：作为用户消息在系统提示**之后**传递，无强制遵守保证
- **想加系统提示**：用 `--append-system-prompt` CLI 标志（每次调用都得传，适合脚本不适合交互）
- **想强制执行**：用 hooks，shell 命令在固定生命周期事件运行，**无论 Claude 决定做什么都生效**

## 12. 引用本文件

回答时引用任何条款都附 `（来源：https://code.claude.com/docs/zh-CN/memory，缓存于 2026-05-19）`。

跨主题查询：
- skill vs CLAUDE.md 选哪个 → references/comparison-matrix.md
- hook 配置详情 → references/settings-permissions-hooks.md
