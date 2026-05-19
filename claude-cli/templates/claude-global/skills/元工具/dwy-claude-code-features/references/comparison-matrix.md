---
source_url: https://code.claude.com/docs/zh-CN/skills, https://code.claude.com/docs/zh-CN/memory, https://code.claude.com/docs/zh-CN/sub-agents
fetched_at: "2026-05-19"
category: comparison
summary: Claude Code 四类用户级扩展（slash command / CLAUDE.md & rules / skills / subagents）横向对比矩阵
---

# Claude Code 四类扩展横向对比

这是查"四类有何区别"时的唯一入口。所有数据来自 code.claude.com 官方中文文档（fetched_at: 2026-05-19）。

## 总览：一句话定位

| 类型 | 一句话定位 |
|------|---------|
| **Slash Command** | 用户主动输入 `/<name>` 触发的命令，**已合并到 skills**；`.claude/commands/*.md` 仍兼容但建议迁移到 `<dir>/SKILL.md` |
| **CLAUDE.md / Rules** | 会话启动时**自动加载**到上下文的常驻规则（`CLAUDE.md` 或 `.claude/rules/*.md`） |
| **Skill** | 元数据常驻、正文按需加载的"可调用知识包"，Claude 自动判断或用户 `/<name>` 触发 |
| **Subagent** | 独立 context window 的子任务执行体，主 agent 通过 Agent 工具调用 |

## 维度对照矩阵

| 维度 | Slash Command | CLAUDE.md / Rules | Skill | Subagent |
|------|---------------|-------------------|-------|----------|
| **文件位置** | `.claude/commands/<name>.md`（项目）/ `~/.claude/commands/<name>.md`（个人） | `CLAUDE.md` 或 `./.claude/CLAUDE.md`（项目）/ `~/.claude/CLAUDE.md`（个人）/ `.claude/rules/*.md` 路径作用域 | `<skill-name>/SKILL.md` + 同目录资源（项目 `.claude/skills/`、个人 `~/.claude/skills/`、插件） | `.claude/agents/<name>.md`（项目）/ `~/.claude/agents/<name>.md`（个人） |
| **frontmatter** | 可选，跟 SKILL.md 相同字段 | **无** frontmatter；`.claude/rules/*.md` 可有 `paths` 字段 | YAML，**仅 `description` 推荐必填**（`name` 默认取目录名） | YAML，**`name` 和 `description` 必填** |
| **触发机制** | 用户输入 `/<name>` | 会话启动自动加载 | LLM 根据 description 自动调用 + 用户 `/<name>` 直接调用 | 主 agent 通过 Agent 工具按 subagent_type 调用 |
| **是否进入主 context** | 否（仅触发时） | **是**，常驻（全文加载） | description 常驻，正文触发时加载 | **否**，独立 context window |
| **大小限制 / 建议** | 跟 SKILL.md 同 | 建议 < 200 行（影响 token 与遵循率） | 主 SKILL.md 建议 < 500 行，大文档拆到 references/ | 视任务而定，body 即 system prompt |
| **指定模型 (`model`)** | ✅ 跟 SKILL.md 同 | ❌ 不适用 | ✅ `sonnet/opus/haiku/inherit` 或完整 model ID | ✅ `sonnet/opus/haiku/inherit` 或完整 model ID |
| **指定 effort** | ✅ | ❌ | ✅ `low/medium/high/xhigh/max` | ✅ `low/medium/high/xhigh/max` |
| **工具白名单字段** | `allowed-tools` | 不适用 | `allowed-tools`（空格分隔字符串或 YAML 列表） | `tools`（逗号分隔）+ `disallowedTools`（黑名单） |
| **权限模式 (`permissionMode`)** | ❌ | ❌ | ❌ | ✅ `default / acceptEdits / auto / dontAsk / bypassPermissions / plan` |
| **MCP 服务器作用域** | ❌ | ❌ | ❌ | ✅ `mcpServers` 字段（仅 subagent 独有） |
| **hooks（生命周期）** | ✅ 同 SKILL.md | ❌ | ✅ `hooks` 字段（PreToolUse 等） | ✅ `hooks` 字段（PreToolUse / PostToolUse / Stop） |
| **支持参数 (`$ARGUMENTS`)** | ✅ | ❌ | ✅ `$ARGUMENTS` / `$N` / `$name`（通过 `arguments` 字段定义） | 主 agent 传递（不通过 `$ARGUMENTS` 语法） |
| **持久 memory** | ❌ | ❌ | ❌ | ✅ `memory: user/project/local` 字段（agent 自维护知识库） |
| **隔离 (`isolation`)** | ❌ | ❌ | ❌ | ✅ `isolation: worktree`（独立 git worktree） |
| **共享 / 分发范围** | user / project / plugin / managed | user / project / local / managed | user / project / plugin / managed | user / project / plugin / managed |
| **是否能直接调用其他类型** | 跟 SKILL.md 等价，可调用工具 | 不可调用，是上下文文本 | 可调用工具，可 `context: fork` 切到 subagent 跑 | 可调用工具，可预加载 skills（`skills` 字段）；**subagent 不能再生成 subagent** |
| **写错时表现** | 命令不可见或行为偏差 | 全 session 被错误引导 | 不触发 / 误触发 / 字段被忽略 | 子任务质量崩 / agent 启动失败 |
| **官方文档主源** | https://code.claude.com/docs/zh-CN/skills（已合并） | https://code.claude.com/docs/zh-CN/memory | https://code.claude.com/docs/zh-CN/skills | https://code.claude.com/docs/zh-CN/sub-agents |

## 关键差异辨析

### 1. Slash Command vs Skill
官方原话："**自定义命令已合并到 skills 中**。`.claude/commands/deploy.md` 和 `.claude/skills/deploy/SKILL.md` 都会创建 `/deploy` 并以相同的方式工作。"

→ 新写一律走 `<dir>/SKILL.md`；已有 `.claude/commands/*.md` 兼容运行但不享受 supporting files、progressive disclosure 等扩展能力。

### 2. CLAUDE.md vs .claude/rules/*.md
两者都自动加载，区别：
- **CLAUDE.md**：单文件无 frontmatter，常驻所有 session
- **`.claude/rules/<topic>.md`**：可拆分多文件，可加 `paths` frontmatter 限定**只在处理匹配文件时才加载**，节省 token

### 3. CLAUDE.md vs Skill
官方原话："当你不断将相同的说明、检查清单或多步骤程序粘贴到聊天中时，或者当 CLAUDE.md 的一部分已经演变成程序而不是事实时，创建一个 skill。"

→ CLAUDE.md 放"事实"（项目结构、命名规范），skill 放"流程"（部署步骤、提交流程）。

### 4. Skill 的 `context: fork` vs Subagent 的 `skills` 字段
两个方向：
- **Skill 用 `context: fork`**：skill 内容作为 prompt，**指定 agent 类型执行**（agent 提供 system prompt + tools）
- **Subagent 用 `skills` 字段**：subagent 的 body 是 system prompt，**预加载若干 skills** 作为参考资料

两者用的是同一底层机制，写哪个看你的中心是"任务"还是"系统提示"。

### 5. Subagent 不能嵌套
官方原话："Subagents cannot spawn other subagents."

→ 需要嵌套委派时用 skills 或在主对话里链式调用多个 subagent。

## 选哪个：决策树

```
要不要在每个 session 都常驻？
├─ 是 → CLAUDE.md / .claude/rules/
└─ 否 → 是不是用户主动触发的固定流程？
        ├─ 是 → Skill（设 disable-model-invocation: true 防 Claude 自动跑）
        └─ 否 → 是不是有大量输出/独立工具白名单/独立 context 需求？
                ├─ 是 → Subagent
                └─ 否 → Skill（默认让 Claude 按 description 决定）
```

## 引用本表

回答用户问题时，引用本表的任何条款都应附 `（来源：<上述 source_url 之一>，缓存于 2026-05-19）`。

如果用户问到 `paths` / `permissionMode` / `effort` / `model` 等具体字段的取值细节，跳转到对应 references 文件（slash-commands.md / memory-rules.md / skills.md / subagents.md）查详表。
