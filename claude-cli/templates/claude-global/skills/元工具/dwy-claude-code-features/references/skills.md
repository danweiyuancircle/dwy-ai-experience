---
source_url: https://code.claude.com/docs/zh-CN/skills
fetched_at: "2026-05-19"
category: C
fetched_via: WebFetch
summary: Claude Code Skills（含已合并的 .claude/commands/）官方规范：SKILL.md 文件结构、frontmatter 全字段表、progressive disclosure、字符串替换、调用控制
---

# Skills（含自定义 slash command）

> **重要**：自定义 slash command 已合并到 skills。`.claude/commands/deploy.md` 与 `<dir>/SKILL.md` 等价。新写一律走 SKILL.md 形态。

## 1. 官方定义

> Skills 扩展了 Claude 能做的事情。创建一个 SKILL.md 文件，其中包含说明，Claude 会将其添加到其工具包中。Claude 在相关时使用 skills，或者你可以使用 `/skill-name` 直接调用一个。

（来源：https://code.claude.com/docs/zh-CN/skills，缓存于 2026-05-19）

## 2. 文件位置与共享范围

| 位置 | 路径 | 适用范围 | 优先级 |
|------|------|---------|--------|
| 企业（managed） | 见 managed settings | 组织全员 | 1 最高 |
| 个人 | `~/.claude/skills/<skill-name>/SKILL.md` | 本机所有项目 | 2 |
| 项目 | `.claude/skills/<skill-name>/SKILL.md` | 仅本项目 | 3 |
| 插件 | `<plugin>/skills/<skill-name>/SKILL.md` | 启用插件的位置 | 4，使用 `plugin-name:skill-name` 命名空间不冲突 |

- 项目级 skills 从启动目录到仓库根的每个父目录的 `.claude/skills/` 都会加载
- 编辑/新增/删除 skill 文件在当前会话内**即时生效**（无需重启），新建顶层 `skills/` 目录需重启
- `--add-dir` 加入的目录的 `.claude/skills/` 也会自动加载（其他 `.claude/` 配置不会）

## 3. 目录布局

```
my-skill/
├── SKILL.md          # 主文档（必需）
├── template.md       # Claude 填写的模板
├── examples/
│   └── sample.md     # 预期输出示例
├── references/
│   └── api.md        # 详细 API 文档（按需加载）
└── scripts/
    └── validate.sh   # Claude 可执行的脚本（不进 context）
```

只有 `SKILL.md` 必需。其他文件**按需**加载，在 SKILL.md 里用 `[reference.md](reference.md)` 等链接引用，Claude 据此判断何时读哪个。

## 4. Frontmatter 完整字段表

```yaml
---
name: my-skill
description: What this skill does
disable-model-invocation: true
allowed-tools: Read Grep
---
```

**全部字段都是可选的，仅 `description` 是推荐。**

| 字段 | 必需 | 含义 |
|------|------|------|
| `name` | 否 | 显示名。省略则用目录名。**仅小写字母、数字、连字符，最多 64 字符** |
| `description` | **推荐** | skill 干什么 + 何时用。Claude 据此决定何时调用。省略则取 markdown 正文第一段。`description + when_to_use` 在 skill 列表中被截断到 **1536 字符**上限 |
| `when_to_use` | 否 | 额外触发上下文（短语 / 示例请求）。追加到 description 后，共享 1536 字符上限 |
| `argument-hint` | 否 | 自动补全提示，如 `[issue-number]` / `[filename] [format]` |
| `arguments` | 否 | 命名位置参数（用于 `$name` 替换）。空格分隔字符串 或 YAML 列表 |
| `disable-model-invocation` | 否 | `true` 阻止 Claude 自动调用，仅用户 `/name` 触发。也阻止被预加载进 subagent。**默认 false** |
| `user-invocable` | 否 | `false` 从 `/` 菜单隐藏，仅 Claude 自动调用。默认 true |
| `allowed-tools` | 否 | skill 活跃时无需权限提示可用的工具。空格分隔字符串 或 YAML 列表。**不限制可用范围**，只是免提示 |
| `model` | 否 | skill 活跃时用的模型。`sonnet/opus/haiku` 别名 或 完整 ID（如 `claude-opus-4-7`）或 `inherit`。仅当前轮有效 |
| `effort` | 否 | 努力级别。`low/medium/high/xhigh/max`。覆盖会话默认 |
| `context` | 否 | `fork` 表示在分叉的 subagent 上下文中运行 |
| `agent` | 否 | `context: fork` 时用哪个 subagent 类型（`Explore/Plan/general-purpose` 或自定义） |
| `hooks` | 否 | 限定于此 skill 生命周期的 hooks。配置格式见 hooks 文档 |
| `paths` | 否 | glob 模式，限制何时激活 skill。逗号分隔或 YAML 列表。匹配的文件被处理时才自动加载 |
| `shell` | 否 | `bash`（默认）或 `powershell`。控制 `` !`cmd` `` 内联和 ` ```! ` 块用哪个 shell |

## 5. 字符串替换（仅 SKILL.md 正文）

| 变量 | 作用 |
|------|------|
| `$ARGUMENTS` | 全部参数原串。skill 不含此占位符时，Claude Code 把 `ARGUMENTS: <value>` 追加到末尾 |
| `$ARGUMENTS[N]` | 按 0 索引取第 N 个参数（shell 风格引号支持） |
| `$N` | `$ARGUMENTS[N]` 简写 |
| `$name` | `arguments` 字段声明的命名参数 |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_EFFORT}` | 当前 effort 级别 |
| `${CLAUDE_SKILL_DIR}` | skill 自身所在目录。引用 scripts/ 或 references/ 时**必用**，避免硬编码路径 |

## 6. 动态上下文注入

```markdown
## Current changes
!`git diff HEAD`
```

`` !`cmd` `` 在 skill 内容发给 Claude **之前**执行，输出替换占位符。多行命令用：

```!
node --version
npm --version
```

- 仅扫描一次原文件，命令输出**不会**再被扫描为占位符
- `disableSkillShellExecution: true` 可在 settings 禁用此行为（替换为 `[shell command execution disabled by policy]`）

## 7. progressive disclosure（三层加载）

| 层 | 何时加载 | 大小约束 |
|----|---------|---------|
| 元数据（name + description） | **始终**在 context（默认所有 session） | ~100 词级别 |
| SKILL.md 正文 | 被调用时加载，常驻整个 session | **建议 < 500 行**（官方 Tip） |
| 资源文件 | 按需读取 / 执行 | 无限大（scripts 执行不加载） |

**关键设计原则**：主 SKILL.md 写"导航 + 路由 + 核心心智模型"，详细字段 / API / 示例放 `references/`，可执行任务放 `scripts/`。

## 8. 调用控制（默认 vs 限制）

| frontmatter | 你可调用 | Claude 可调用 | 何时加载到 context |
|-------------|---------|--------------|------------------|
| （默认）| ✅ | ✅ | description 始终在；调用时加载正文 |
| `disable-model-invocation: true` | ✅ | ❌ | description **不进** context；用户调用时加载 |
| `user-invocable: false` | ❌ | ✅ | description 始终在；调用时加载 |

## 9. 与 subagent 配合：两个方向

| 方法 | 系统提示 | 任务 | 同时加载 |
|------|---------|------|---------|
| Skill 带 `context: fork` | 来自 agent 类型 | SKILL.md 内容 | CLAUDE.md（Explore/Plan 不加载）|
| Subagent 带 `skills` 字段 | subagent 的 markdown 正文 | Claude 委派消息 | 预加载的 skills + CLAUDE.md |

## 10. 最小骨架（复制即用）

### 普通信息类 skill

```yaml
---
description: 一句话功能 + 何时用。涉及以下任何主题必须使用此 skill：用户问 X / 在编辑 Y 时
---

# 标题

## 触发场景
1. ...

## 工作流程
1. ...
```

### 副作用任务类 skill（如 deploy / commit）

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(git push *) Bash(npm run build)
---

部署 $ARGUMENTS 到生产：

1. 跑测试套件
2. 构建
3. 推送
4. 验证
```

### 隔离任务类 skill（用 fork 让 subagent 跑）

```yaml
---
name: deep-research
description: Research a topic thoroughly. Use when user asks for codebase-wide investigation
context: fork
agent: Explore
---

彻底调研 $ARGUMENTS：

1. 用 Glob/Grep 找相关文件
2. 读取并分析代码
3. 给出带文件引用的总结
```

## 11. `.claude/commands/*.md` 兼容写法

官方原话："`.claude/commands/` 中的文件仍然有效，并支持相同的 frontmatter。建议使用 Skills，因为它们支持额外的功能。"

如果你有遗留的 `.claude/commands/deploy.md`：
- 它跟 `.claude/skills/deploy/SKILL.md` 等价，都创建 `/deploy`
- frontmatter 字段集与上面表完全相同
- 但**没有** supporting files（references/ scripts/）能力
- 建议迁移：把 `.claude/commands/deploy.md` 改成 `.claude/skills/deploy/SKILL.md`，内容不变

## 12. 常见踩坑

- **description 过短**：`description: Deploy app` 这种太空泛，Claude 不会自动调用。补具体触发短语
- **硬编码 skill 路径**：脚本里写 `~/.claude/skills/deploy/scripts/run.sh` 会在项目级 / 插件级安装时失效。**改用 `${CLAUDE_SKILL_DIR}/scripts/run.sh`**
- **`allowed-tools` 写星号通配** `*`：权限过宽是安全隐患，应列具体工具如 `Bash(git add *) Bash(git commit *) Read Edit`
- **`context: fork` 用在纯指南 skill**：fork 把 SKILL.md 当 prompt 给 subagent，纯"使用这些 API 约定"这类没任务的内容会让 subagent 无所事事直接返回。
- **`name` 不合规**：必须 kebab-case，不能用 `_` 或大写。文件名也建议跟 `name` 一致便于查找

## 13. 故障排查

| 现象 | 处理 |
|------|------|
| Claude 不触发 | 检查 description 关键词；运行 `What skills are available?` 看是否列出；直接 `/skill-name` 测试 |
| Claude 过度触发 | description 收紧具体场景；或加 `disable-model-invocation: true` |
| description 被截断 | 官方 1536 字符上限。把关键词放前面；用 `/doctor` 看预算是否溢出；或在 settings 提 `skillListingBudgetFraction` |
| 调用了 skill 但行为没变 | SKILL.md 内容已进 context，但 Claude 选了其他路径。加强 description + 正文指令，或用 hooks 强制 |

## 14. 引用本文件

回答时引用任何条款都附 `（来源：https://code.claude.com/docs/zh-CN/skills，缓存于 2026-05-19）`。

跨主题查询：
- 字段对比 → references/comparison-matrix.md
- 写法 lint → scripts/lint.py + references/lint-checklist.md
- 跟 subagent 关系 → references/subagents.md
