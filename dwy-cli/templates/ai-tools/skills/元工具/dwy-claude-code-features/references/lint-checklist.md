---
source_url: synthesized from https://code.claude.com/docs/zh-CN/skills, /zh-CN/sub-agents, /zh-CN/memory
fetched_at: "2026-05-19"
category: lint-semantic
summary: 语义类（机器难判定）人工对照检查清单。配合 scripts/lint.py 的格式硬检查使用
---

# 语义检查清单

`scripts/lint.py` 处理格式硬规则（YAML 解析、字段集、文件名）。本清单处理"格式合法但写得不好"的语义问题，需要 Claude 人工对照判断。

使用方式：用户让你检查某个 `.claude/commands/*.md`、`.claude/agents/*.md`、`SKILL.md` 或 `CLAUDE.md` 时，**先跑 lint.py**，再按本清单逐项核对，最后用 dwy-shared 风格表格输出：`检测项 | 严重度 | 修复建议`。

---

## 通用（四类都查）

- [ ] **description 是否包含具体触发关键词**：列举用户口头会说的短语（中英都行），如「检查 X / 创建 Y / 怎么写 Z」
- [ ] **description 长度合理**：> 30 字（避免太空泛）且 < 1536 字符（skill 列表硬上限）
- [ ] **不暴露内部实现细节**：员工邮箱、内网域名 / IP、未发布的内部 API 名称、SQL 表名、Redis key 等
- [ ] **不硬编码用户路径**：`/Users/chances/...`、`/home/<name>/...` 这类绝对路径不应出现在示例
- [ ] **代码示例可运行**：贴出的 yaml/bash/python 片段语法正确，没有断尾或占位 `xxx`
- [ ] **不暴露密钥**：API Key / Token / 密码原文一律禁止出现，哪怕是示例也要用 `<your-token-here>` 占位

---

## A. Slash Command（`.claude/commands/*.md` 或 SKILL.md 形态）

> 自定义 command **已合并到 skills**。新写一律走 SKILL.md 形态走下面 C 类。`.claude/commands/*.md` 兼容运行，可继续用以下清单检查：

- [ ] **`allowed-tools` 最小化**：不写星号通配，按需列具体工具，如 `Bash(git add *) Bash(git commit *) Read Edit`
- [ ] **`argument-hint` 给出有意义占位符**：写 `[issue-number]`、`[filename] [format]` 这类，不写 `[arg]`
- [ ] **命令名 kebab-case** 且不与内置命令冲突（参考 `code.claude.com/docs/zh-CN/commands` 内置命令清单：`/help / /compact / /clear / /init / ...`）
- [ ] **副作用命令明确加 `disable-model-invocation: true`**：`/deploy`、`/commit`、`/send-slack` 等不应让 Claude 自动跑

---

## B. CLAUDE.md / `.claude/rules/*.md`

- [ ] **大小 < 200 行**：超过建议拆 `.claude/rules/`（官方明确建议）
- [ ] **结构化表达至少一种**：「检查清单」/「Do / Don't 表」/「严重程度分级表」/「字段表」，避免大段散文
- [ ] **指令具体可验证**：写「使用 2 空格缩进」而不是「请格式化好代码」；写「commit 前跑 `npm test`」而不是「测一下」
- [ ] **没有冲突指令**：同一规则不要在多个文件里给不同答案
- [ ] **`@path` import 路径真实存在**：lint.py 会查路径，但还要检查 import 的内容是否真有用，没用就别 import（占 token）
- [ ] **`.claude/rules/*.md` 用 `paths` frontmatter 缩限作用域**：通用规则不写 `paths`，专题规则（如 `api-design.md`）必须写 `paths: ["src/api/**/*.ts"]` 避免无关 session 加载
- [ ] **不重复内置约束**：官方默认的 plan mode、文件读写约束不要在 CLAUDE.md 重复声明

---

## C. Skill（`<dir>/SKILL.md`）

- [ ] **description 够 pushy**（dwy-shared 范式）：用「涉及以下任何主题 / 必须使用此 skill」「触发条件：」之类硬性引导句式
- [ ] **description 列出具体触发短语**：用户口头说什么 / 在编辑什么文件时触发，分号 / 顿号分隔
- [ ] **合理使用 progressive disclosure**：
  - SKILL.md 主文档 < 500 行（官方 Tip）
  - 大块参考资料拆到 `references/`（详读时再加载）
  - 可执行任务拆到 `scripts/`（不进 context，按需 `Bash` 调用）
- [ ] **`references/` 内大文档（> 300 行）有 TOC**
- [ ] **`scripts/` 内脚本可执行**：shebang 行正确（`#!/usr/bin/env python3` 或 `#!/bin/bash`），文件 chmod +x
- [ ] **副作用类 skill 加 `disable-model-invocation: true`**：`/commit / /deploy / /send-*` 这类
- [ ] **背景知识类 skill 加 `user-invocable: false`**：不可作为命令的纯参考内容
- [ ] **用 `${CLAUDE_SKILL_DIR}` 引用 skill 内文件**：不要硬编码 `~/.claude/skills/<name>/...`，否则插件 / 项目级安装会失效
- [ ] **`allowed-tools` 收得紧**：跟 A 类相同要求，不写星号通配
- [ ] **`context: fork` 时必须有可执行任务**：fork 把 SKILL.md 作为 subagent prompt，纯指南类 skill 用 fork 等于浪费

---

## D. Subagent（`.claude/agents/*.md`）

- [ ] **`name` 是 kebab-case** 且唯一（同 scope 内重名会被静默丢一个，无警告）
- [ ] **description 说清输入 / 输出契约**：「输入：xxx；输出：yyy」，让主 agent 知道什么时候委派
- [ ] **description 含 "use proactively" 或类似主动委派暗示**（如果希望 Claude 自动调用）
- [ ] **`tools` 给最小集**：不写 `tools` 字段会继承所有工具，包括 MCP。read-only agent 应明确 `tools: Read, Glob, Grep, Bash`
- [ ] **`permissionMode` 合理**：read-only 用 `plan`，安全侧用 `default`，自动化用 `acceptEdits`，慎用 `bypassPermissions`
- [ ] **body 是 self-contained 的 system prompt**：subagent 看不到主对话，body 要把任务上下文 / 角色 / 输出格式说全
- [ ] **`memory` 字段是否需要**：跨会话沉淀知识用 `memory: project`（默认推荐），临时任务别开 memory（每次写文件污染仓库）
- [ ] **`mcpServers` 内联还是引用**：仅 subagent 用的 MCP 用 inline 定义；主对话也要的引用名字
- [ ] **`hooks` 写明 matcher**：`PreToolUse` 必须指定 `matcher`（`Bash`、`Edit|Write` 等），不写 = 匹配所有
- [ ] **`isolation: worktree` 仅在需要文件隔离时用**：纯调研类 agent 不需要

---

## 输出格式（推荐）

发现违规时按 dwy-shared 风格输出：

| 检测项 | 严重度 | 修复建议 |
|--------|--------|---------|
| description 缺触发关键词 | 高 | 在 description 末尾追加「涉及以下任何主题必须使用此 skill：用户问 X / 编辑 Y / 检查 Z」 |
| SKILL.md 762 行 | 中 | 把第 5/6 节移到 `references/advanced.md`，主文档保留导航段 |
| body 出现 `/Users/chances/projects/...` | 高 | 替换为 `<your-project-path>` 占位 |
| 命令名 `my_command` | 低 | 改 kebab-case：`my-command` |

合规时静默放行，不要为了凑数报。

## 严重度分级（沿用 dwy-shared 约定）

- **致命 → STOP**：泄露密钥 / 编造官方字段名 / 跳过 lint.py 直接通过
- **高**：触发关键词缺失 / 字段集错误 / hooks 无 matcher
- **中**：体积超限未拆分 / 工具白名单过宽 / 缓存过期未刷新
- **低**：命名风格（kebab-case）/ 注释完整度

引用判定依据时附 `（来源：<source_url>，缓存于 2026-05-19）`。
