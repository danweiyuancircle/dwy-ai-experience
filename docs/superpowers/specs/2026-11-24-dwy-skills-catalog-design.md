# dwy skills：第三方 Skills / Plugins 编排管理

日期：2026-11-24  
状态：已确认，进入实现  
范围：`dwy-cli` 新子命令 `dwy skills`

## 问题

第三方 skills / plugins 目前各自安装，没有统一入口。需要：

1. 维护一份可迁移的全局收藏清单
2. 交互选择后用**官方命令**安装 / 更新 / 卸载
3. 扫描本机已装项，统一查看与管理
4. 换机：导出清单 → 导入 → 按清单安装

## 非目标（第一版）

- 不改 `dwy sync` / `refresh` / `migrate` 流程
- 不下载或复制第三方内容（不做自建安装器）
- 不做云账号同步、不做后台自动更新
- 不评测第三方安全性（只编排；风险提示指向官方来源）
- dwy 模板 skills 仍只由 sync 体系管理；本命令对它们只读

## 命令面

| 命令 | 作用 |
|------|------|
| `dwy skills` | 交互主入口：安装（收藏）/ 管理已装 / 编辑收藏 |
| `dwy skills list` | 列出本机已装（skills 目录 + Claude plugins）与来源标注 |
| `dwy skills catalog` | 收藏源管理（list / add / remove / export / import） |
| `dwy skills add <源>` | 加入收藏；`--install` 可立刻安装 |
| `dwy skills install [名…]` | 从收藏安装；`--all` 安装全部收藏 |
| `dwy skills update [名…]` | 官方 update |
| `dwy skills remove [名…]` | 官方 uninstall / remove |

`dwy --help`、`CLAUDE.md` 命令列表、`dwy-cli/CHANGELOG.md` 必须同步。

## 存储

路径：`~/.dwy/skills-catalog/catalog.json`（可用 `homeDir` 注入，便于测试）

```json
{
  "version": 1,
  "entries": [
    {
      "id": "vercel-labs/agent-skills",
      "kind": "skills-cli",
      "source": "vercel-labs/agent-skills",
      "skills": ["react-best-practices"],
      "agents": ["claude-code", "codex"],
      "note": "",
      "added_at": "2026-11-24T00:00:00.000Z"
    },
    {
      "id": "feature-dev@claude-plugins-official",
      "kind": "claude-plugin",
      "source": "feature-dev@claude-plugins-official",
      "added_at": "2026-11-24T00:00:00.000Z"
    },
    {
      "id": "claude-plugins-official",
      "kind": "claude-marketplace",
      "source": "anthropics/claude-plugins-official",
      "added_at": "2026-11-24T00:00:00.000Z"
    }
  ]
}
```

约束：

- 不存绝对路径、不存 token / 密码
- `id` 稳定、唯一；同 source 重复 add 为更新而非翻倍
- 跨机：`catalog export <file>` / `catalog import <file>`；新机再 `install --all` 或交互勾选

## 本机已装扫描

1. **Skills 目录**（与现有全局 dest 对齐）：`~/.claude/skills`、`~/.agents/skills`、`~/.cursor/skills`、`~/.config/opencode/skills`、`$CODEX_HOME/skills`（若存在）
2. **Claude plugins**：解析 `claude plugin list` / marketplace list 输出（优先结构化；必要时稳健解析文本）
3. **Codex plugins**：解析 `codex plugin list --json` 的已安装 `pluginId`（`name@marketplace`）
4. **来源标注**：
   - `catalog`：id/source 命中收藏
   - `dwy-template`：名称属于当前 dwy 模板 skills（只读，禁止本命令 remove）
   - `unknown`：其余

## 安装路由（编排层）

| kind | 安装 | 更新 | 卸载 |
|------|------|------|------|
| `skills-cli` | `npx skills add <source> -g -a <agents> [-s …]` | `npx skills update …` | `npx skills remove …` |
| `claude-plugin` | `claude plugin install <plugin@marketplace>` | `claude plugin update …` | `claude plugin uninstall …` |
| `claude-marketplace` | `claude plugin marketplace add <source>` | `claude plugin marketplace update …` | `claude plugin marketplace remove …` |
| `codex-plugin` | `codex plugin add <plugin@marketplace>` | `codex plugin remove` 再 `add`（官方无 update） | `codex plugin remove …` |
| `codex-marketplace` | `codex plugin marketplace add <source>` | `codex plugin marketplace upgrade …` | `codex plugin marketplace remove …` |

规则：

- 默认全局；agents 可多选（Claude Code / Codex / Cursor / OpenCode 等，映射到官方 `-a` 值）
- 确认前不执行写操作
- 预览必须列出将执行的完整命令
- 官方命令失败：记录该条错误，继续后续项，结束汇总
- 不把 `-y` 用于用户未在 dwy 预览中确认的危险跳过路径；用户已在预览确认同一批动作后，允许向非交互官方 CLI 传必要的跳过确认参数以便编排跑完

## 交互流程（`dwy skills`）

1. 选择操作：从收藏安装 / 管理已装（更新·卸载） / 编辑收藏
2. 可搜索多选目标；已装项展示来源与 agent
3. 选择 agents（默认：条目自带或上次选择 / 全局常用）
4. 预览官方命令清单
5. 确认后顺序执行；汇总成功 / 失败

复用现有 `searchableSelect` / `tabMultiselect` 风格，不新造交互体系。

## 与 dwy sync 的边界

- `dwy sync` 继续只管理模板内 skills / rules / hooks
- 产品流程「外部 Skill 依赖」仍由 AI 按需处理；本命令是用户主动的收藏与编排入口
- list 中出现的 dwy 模板 skill：展示为只读；remove 拒绝并提示使用 `dwy sync`

## 验收

- `dwy --help` 含 `skills` 及主要子命令说明
- 空 catalog 可 add，list catalog 可见
- export → 另一 home/目录 import → install 预览命令正确
- 能扫描到本机已有 Claude plugin / skills 目录项并标注来源
- 取消确认后无本机变更
- 对 dwy 模板 skill 的 remove 被拒绝
- 单元测试覆盖：catalog CRUD、路由命令生成、来源标注、export/import；官方命令调用用假 runner，不打真实网络

## 实现落点（预期）

- `dwy-cli/bin/index.js`：路由 `skills`
- `dwy-cli/src/cli-help.js`：帮助文案
- `dwy-cli/src/skills-catalog.js`：catalog 读写 / export / import
- `dwy-cli/src/skills-scan.js`：本机扫描与来源标注
- `dwy-cli/src/skills-install.js`：官方命令生成与执行
- `dwy-cli/src/skills-cmd.js`：子命令与交互编排
- `dwy-cli/tests/skills-*.test.js`：测试
- 文档：`CLAUDE.md`、`dwy-cli/CHANGELOG.md`、必要时 `docs/cli-sync.md` 边界说明
