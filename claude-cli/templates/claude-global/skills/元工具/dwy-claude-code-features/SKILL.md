---
name: dwy-claude-code-features
description: Claude Code 四大用户级扩展（slash command / CLAUDE.md & rules / skills / subagent）官方文档查询 + 写法 lint 工具。涉及以下任何主题，**必须**使用此 skill（即使用户没说 'dwy-claude-code-features'）：用户问 'slash command 怎么写' / '.claude/commands 字段' / 'CLAUDE.md 加载机制' / 'CLAUDE.md 放哪' / '.claude/rules 怎么用' / 'paths frontmatter' / 'SKILL.md frontmatter' / 'allowed-tools / argument-hint / disable-model-invocation' / 'progressive disclosure' / 'context: fork' / '怎么写 subagent' / '.claude/agents 字段' / 'permissionMode / mcpServers / isolation' / 'hooks 事件清单' / 'Claude Code 特性 / 扩展 / 自定义'；用户要求横向对比 command / rules / skills / agent / subagent 的差异；用户让你检查现有 .claude/commands/*.md / .claude/agents/*.md / SKILL.md / CLAUDE.md 写法是否合规；用户要写新的 command/skill/agent 并粘贴 frontmatter 求确认；用户说 '帮我写一个 slash command' / '加个 subagent' / '生成 SKILL.md' / '/<name> 怎么用'。权威来源：code.claude.com 官方中文文档，所有引用 URL 全程留痕。
authoritative_source: https://code.claude.com/docs/zh-CN
fetched_at: "2026-05-19"
---

# dwy-claude-code-features

Claude Code 四大用户级扩展（**slash command / CLAUDE.md & rules / skills / subagent**）的官方文档查询 + 写法 lint 工具。

权威来源限定 `code.claude.com/docs/zh-CN/*`。引用任何官方条款都附 `（来源：<url>，缓存于 2026-05-19）`。

## 何时触发

下列任何场景**必须**用此 skill，不要凭记忆作答：

- 用户问任一特性的字段、文件位置、加载机制、调用方式
- 用户要求横向对比四类的差异
- 用户让你**检查** `.claude/commands/*.md` / `.claude/agents/*.md` / `SKILL.md` / `CLAUDE.md` 写法
- 用户要**新写**一个 command/skill/agent，先拿模板再下笔
- 用户粘贴一段 frontmatter 让你判断是否合规

## 四类速查（一级路由）

| 特性 | 文件位置 | 关键字段 | 详读 |
|------|---------|---------|------|
| Slash Command | `.claude/commands/<name>.md`（已合并到 skills，**新写走 SKILL.md**） | 同 SKILL.md | [references/slash-commands.md](references/slash-commands.md) |
| CLAUDE.md / Rules | `CLAUDE.md` / `./.claude/CLAUDE.md` / `.claude/rules/*.md` | 无 frontmatter；rules 可有 `paths` | [references/memory-rules.md](references/memory-rules.md) |
| Skill | `<dir>/SKILL.md` + 同目录资源 | `name / description / allowed-tools / model / context / paths` 等 | [references/skills.md](references/skills.md) |
| Subagent | `.claude/agents/<name>.md` | **`name + description` 必填**；`tools / permissionMode / mcpServers / hooks` 等 | [references/subagents.md](references/subagents.md) |

横向对比矩阵：[references/comparison-matrix.md](references/comparison-matrix.md)

## 工作流程（问题驱动）

### 场景 A：用户问"某个字段 / 文件位置 / 使用场景"

1. 在四类速查里定位是哪一类
2. 读对应的 references/*.md
3. 回答时**必须**附原文 URL：`（来源：<frontmatter 里的 source_url>，缓存于 2026-05-19）`
4. **禁止编造字段名**——若 references 里没有该字段，明说"官方文档未提及"

### 场景 B：用户要横向对比

直接读 [references/comparison-matrix.md](references/comparison-matrix.md)，按用户关心的维度（文件位置 / frontmatter / 触发方式 / 工具白名单 / 共享范围）输出对应行。

### 场景 C：用户让你"检查写法是否合规"

按以下顺序：

1. **跑 lint.py**（格式硬检查，秒级返回）：

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/lint.py --target <文件路径> [--type slash-command|skill|subagent|claude-md]
   ```

   不传 `--type` 时按路径自动推断。

2. **对照 [references/lint-checklist.md](references/lint-checklist.md)** 做语义检查（description 触发关键词、progressive disclosure、暴露内部细节等机器难判定的项）

3. **用 dwy-shared 风格表格**输出违规：

   | 检测项 | 严重度 | 修复建议 |
   |--------|--------|---------|
   | description 缺触发关键词 | 高 | 追加「涉及以下任何主题必须使用此 skill：用户问 X / 编辑 Y」 |
   | SKILL.md 762 行 | 中 | 把第 5/6 节移到 `references/advanced.md` |

   合规则静默放行，不要凑数报。

### 场景 D：用户要"新写一个 command / skill / agent"

1. 先确认目标类型（场景 A 路由表）
2. 从对应 references 的"最小骨架（复制即用）"段落取模板
3. 用 lint.py（场景 C）校验产物

## URL 留痕（强约束）

- 每个 [references/](references/) 下的 .md 文件 frontmatter 都有 `source_url` + `fetched_at`
- 所有缓存文档的 URL 汇总在 [references/url-manifest.json](references/url-manifest.json)
- 回答时引用任何官方条款都附 `（来源：<url>，缓存于 <date>）`
- 如果用户说"刷新文档"或缓存超 90 天：

  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/refresh_docs.py
  ```

  脚本会列出哪些文件需要刷新 + 主源 URL。然后用 WebFetch 抓最新内容更新对应 reference，最后用 `--update-date` 更新 `fetched_at`。

## 强约束（检测清单）

| 检查项 | 违规模式 | 严重度 |
|--------|---------|--------|
| 引用官方字段 / 规则未附 URL | 回答提到 `allowed-tools / permissionMode` 等却不引用源 | 高 |
| 编造字段名 | 输出的 frontmatter 字段未在 references/*.md 出现 | **致命 → STOP** |
| 跳过 lint.py 直接说"没问题" | 用户要求检查写法但未跑脚本 | 高 |
| 用过期缓存当最新（> 180 天）| 直接答而不提示用户刷新 | 中 |
| 把 skill 字段当 subagent 字段（或反过来）| 比如说 subagent 用 `allowed-tools`（错，应是 `tools`） | 高 |

## 与其他 skill 的协作边界

- 写 / 改 dwy-shared 仓库内 skill 的**归档 / 搬迁** → 走 `dwy-shared` skill，本 skill 不管入库
- 创建 / 评估 / 测试 / 优化新 skill 的**内容** → 走 `skill-creator`，本 skill 只覆盖"格式是否合规"和"官方字段语义"
- 用户问 `claude-code` 命令行参数（不是配置文件）→ 引导到 [references/settings-permissions-hooks.md](references/settings-permissions-hooks.md) 或 `code.claude.com/docs/zh-CN/cli-reference`

## 资源目录

```
dwy-claude-code-features/
├── SKILL.md                          # 本文件
├── references/
│   ├── slash-commands.md             # A
│   ├── memory-rules.md               # B
│   ├── skills.md                     # C
│   ├── subagents.md                  # D
│   ├── settings-permissions-hooks.md # E（横向）
│   ├── comparison-matrix.md          # 四类对比表
│   ├── lint-checklist.md             # 语义检查清单
│   └── url-manifest.json             # 所有 URL + fetched_at
└── scripts/
    ├── lint.py                       # 格式硬检查
    └── refresh_docs.py               # 文档刷新提示
```

## 工具脚本速查

| 脚本 | 用途 | 关键参数 |
|------|------|---------|
| `${CLAUDE_SKILL_DIR}/scripts/lint.py` | 格式硬检查 | `--target <file> [--type slash-command\|skill\|subagent\|claude-md] [--format json\|table]` |
| `${CLAUDE_SKILL_DIR}/scripts/refresh_docs.py` | 文档刷新提示 | `[--only A\|B\|C\|D\|E] [--warn-days 90] [--check-only]` |

只用 Python 标准库，无外部依赖。

## 风格

- 所有回答**中文**
- 引用官方条款附 URL（来源链 + 缓存日期）
- 不编造字段名 / 默认值 / 路径
- 检查产出用 dwy-shared 风格 3 列表：`检测项 | 严重度 | 修复建议`
- 合规则静默放行
