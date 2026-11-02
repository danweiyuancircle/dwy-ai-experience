# dwy-ai-experience

团队共享基础库与开发工具 monorepo，按 CLI、后端、前端网页和 Apple 客户端四类组织。

[English](README.en.md) · [文档索引](docs/README.md) · [源码与包分发](docs/private-distribution.md)

## 目录与包

| 路径 | 包 / 用途 |
| --- | --- |
| `dwy-cli/` | `create-dwy`：CLI、项目脚手架和 AI 配置同步 |
| `dwy-cli/templates/ai-tools/` | 分发用 skills、rules、hooks 与 hook 清单 |
| `dwy-cli/templates/project/` | 项目脚手架模板 |
| `backend/src/dwyeapi/` | `dwyeapi`：FastAPI 基础设施 |
| `backend/packages/device-fingerprint/` | `dwy-device-fingerprint`：独立设备指纹包 |
| `backend/packages/auth/` | `dwy-auth`：应用认证与独立管理员会话 |
| `frontend/eui/` | `@dwydev/eui`：Vue 组件库 |
| `frontend/ekit/` | `@dwydev/ekit`：前端工具库 |
| `frontend/admin-shell/` | `@dwydev/admin-kit`：管理端基础框架 |
| `frontend/auth-web/` | `@dwydev/auth-web`：网页认证组件与 Cookie 会话 |
| `frontend/playground/` | 文档与组件演示站 |
| `ios/` | AppleAppKit：iOS/macOS 框架、客户端认证、测试与模板 |
| `ci/`、`scripts/`、`.github/` | 跨包验证与构建发布工具 |

根 `Package.swift` 是远程 SwiftPM 入口，源码和测试位于 `ios/`。根 `package.json`、`pnpm-workspace.yaml`、`pnpm-lock.yaml` 统一管理 CLI 与前端；Python 使用 uv 独立管理。

根 `.claude/`、`.agents/` 是开发本仓库时使用的配置，与 CLI 分发模板分开。

## 本地开发

使用 `.node-version` 指定的 Node 和根 `package.json` 指定的 pnpm。以下命令从仓库根执行：

```bash
pnpm install --frozen-lockfile
uv sync --project ci --frozen

pnpm build:frontend
pnpm --dir frontend/auth-web build
pnpm --dir frontend/playground dev
node dwy-cli/bin/index.js --help
```

Python 锁定开发环境统一位于 `ci/`，其中引用本仓库的 EAPI、应用认证和设备指纹源码。

## 验证

```bash
uv run --project ci --frozen pytest backend/tests backend/packages/auth/tests scripts/tests -q -o asyncio_mode=auto
pnpm --dir frontend/eui test
pnpm --dir frontend/ekit test
pnpm --dir frontend/admin-shell test
pnpm --dir frontend/auth-web test
pnpm --dir dwy-cli test
swift test
```

Apple 验证需要完整 Xcode 环境。本机使用 Node 26 时，如 Vitest/jsdom 受实验性 Web Storage 影响，可按 [docs/private-distribution.md](docs/private-distribution.md) 局部设置测试环境。

## AI 配置基线

`dwy-cli/templates/ai-tools/AGENTS.md` 是通用基线源文件，包含新功能开发前的工具发现与风险评估规则。`dwy` / `dwy sync` 按「范围 → 平台 → 本次处理内容 → 逐项选择 → 清单确认」执行，默认只选择 Skills。未选择的类型及其同步记录保持原样，确认前不写入任何配置。项目脚手架统一生成 `AGENTS.md`；Claude Code 的用户级全局入口使用原生的 `CLAUDE.md`。

- 当前项目：可选择 Skills、项目 Rules、Hooks。
- 全局：可选择 Skills、全局通用规范、Hooks，不提供 Cursor。
- 类型按所选平台能力过滤。Skills / Rules 按分类逐项勾选；Hooks 选中类型后按平台自动同步；全局通用规范显示摘要。
- 取消已有勾选会移除当前范围的托管入口；未勾选整个类型则不处理该类型。确认页列出本次写入、备份和清理项。
- 用户主目录及其别名不能作为项目范围同步，需选择全局或进入项目目录，避免项目入口与全局入口重合。

| 平台 | 所选 Rules 的项目位置 | 通用基线的全局位置 |
|------|----------|------------------------|
| Claude Code | 根 `AGENTS.md` 的托管规则块 | `~/.claude/CLAUDE.md` |
| Codex | 根 `AGENTS.md` 的托管规则块 | `$CODEX_HOME/AGENTS.md`，默认 `~/.codex/AGENTS.md` |
| OpenCode | 根 `AGENTS.md` 的托管规则块 | `~/.config/opencode/AGENTS.md` |
| Cursor | `.cursor/rules/dwy-<规则名>.mdc` | 不支持文件同步，使用应用设置 |

三种 CLI 共用项目根 `AGENTS.md`。只有选择项目 Rules 才更新项目托管块、清理旧项目基线和迁移旧规则入口；只有选择全局通用规范才更新原生全局指令入口。托管块之外的手写内容保留。旧 Claude 基线文件无托管标记时，仅在其内容与当前模板完全一致时清理；无法确认归属的文件保留。

Claude Code 直接读取项目 `AGENTS.md` 需要 v2.1.277 或更新版本，并启用对应内置插件；默认情况下，工作目录及祖先目录中若存在 `CLAUDE.md`、`.claude/CLAUDE.md` 或 `CLAUDE.local.md`，会优先读取这些旧文件。全局 `~/.claude/CLAUDE.md` 会与项目指令一起加载。加载条件见 [Claude Code 官方说明](https://code.claude.com/docs/en/memory#agents-md)。

## Skills 共享副本与老项目迁移

Skills 内容来自 CLI 包内模板，用户目录 `.dwy/skills/<name>` 保存一份共享副本；项目和全局的发现目录通过整个 Skill 目录的软链接引用它。项目选择页根据实际入口判断覆盖：全部适用平台均已全局启用时禁用重复勾选；只有部分平台启用时仍可选，只给缺少全局入口的平台建立项目链接。

相同平台已有有效全局入口时，项目不保留重复入口，真实目录先备份，清理操作在确认页单独列出。项目同步不改写全局提供者。默认勾选只来自所选范围及平台，不混入另一范围的记录。`dwy sync` / `dwy migrate` 仅准备缺失或损坏的共享副本，已有共享内容只由 `dwy refresh` / `dwy upgrade` 更新。

选择产品流程 Skills 时，缺失的外部依赖会在确认清单中列出，确认后联网拉取固定版本；已有外部副本保留。

```bash
# 老项目：在项目根目录执行一次，无需重新勾选
dwy migrate

# 日常更新：升级 CLI 后自动刷新共享 Skills
dwy upgrade

# 通过包管理器手动升级 CLI 后，刷新一次即可影响所有已迁移项目
dwy refresh
```

`dwy migrate` 只迁移项目已有、能通过当前模板名称或历史同步记录识别的托管 Skills；未知个人 Skill 不改动，当前包已移除的历史条目保留并报告。原真实目录先备份到项目或用户目录的 `.dwy/skill-backups`，重复执行不会重复备份已有正确链接。原有的整个 Skills 根目录链接保留，不通过它改写外部目录。

旧项目需各执行一次迁移，之后无需逐项目更新 Skills。链接只在当前机器有效，跨机器使用需重新同步；正在运行的 AI 会话可能缓存 Skill，需要重新加载。macOS / Linux 使用目录软链接，Windows 使用目录 junction。

开发中的命令可用 `node dwy-cli/bin/index.js migrate` 或 `node dwy-cli/bin/index.js refresh` 执行；迁移其他项目时，使用指向本仓库 CLI 入口的实际路径，并在目标项目根目录运行。

## 接入与分发

- 认证总览：[docs/auth.md](docs/auth.md)。
- EUI 接入与设计规范、Tasks 接入等：[docs/README.md](docs/README.md)。
- Apple 框架与示例：[ios/README.md](ios/README.md)。
- 公开源码与包安装：[docs/private-distribution.md](docs/private-distribution.md)。

GitHub 源码公开，npm/PyPI 包公开发布，允许任何人安装使用。按包标签触发 `.github/workflows/publish-*.yml`，发布使用 OIDC；`dwy upgrade` 从 npm 更新正式版。CLI 默认读取包内模板，无需源码仓库权限。SwiftPM 继续使用同一 Git 仓库的语义化标签，跨包 CI 和可选 GitHub 快照保留在 `.github/workflows/private-release.yml`。

历史迁移来源、发布与消费者验收证据保留在 [docs/archive/README.md](docs/archive/README.md)，不作为当前接入说明。
