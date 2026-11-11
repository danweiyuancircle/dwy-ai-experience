# dwy-ai-experience

团队共享基础库与开发工具 monorepo，按 CLI、后端、前端网页和 Apple 客户端四类组织。

[English](README.en.md) · [文档索引](docs/README.md) · [CLI 同步](docs/cli-sync.md) · [源码与包分发](docs/private-distribution.md)

## 目录与包

| 路径 | 包 / 用途 |
| --- | --- |
| `dwy-cli/` | `create-dwy`：CLI、项目脚手架和 AI 配置同步 |
| `dwy-cli/templates/ai-tools/` | 分发用 skills、rules、hooks 与 hook 清单 |
| `dwy-cli/templates/project/` | 项目脚手架模板 |
| [`assets/notification-icons/`](assets/notification-icons/README.md) | 共享通知图标：购买、订阅、退款、告警、审核、报表、邮件与普通通知，提供 SVG / PNG |
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

`dwy-cli/templates/ai-tools/AGENTS.md` 是通用基线源文件。`dwy` / `dwy sync` 按「范围 → Skills → 项目 Rules → 通用规范 → Hooks → CLI → 清单确认」执行。通用规范和 Hooks 默认启用；CLI 首次只选 Codex，并恢复当前范围已同步的其他 CLI。启动不联网检查模板；确认前不修改项目、全局配置或已安装共享 Skills。项目脚手架统一生成 `AGENTS.md`；Claude Code 的用户级全局入口使用原生的 `CLAUDE.md`。完整说明见 [docs/cli-sync.md](docs/cli-sync.md)。

- 当前项目：可选择 Skills、Hooks、Rules、AGENTS.md 通用规范。
- 全局：可选择 Skills、Hooks、AGENTS.md 通用规范，不提供 Cursor。
- Skills / Rules 按分类逐项勾选；项目已有有效全局通用规范或全部所需 Hooks 时，直接跳过对应操作页，不重复安装。最终选择 CLI 后重新核算继承和实际操作。
- 取消 Skills / Rules 的已有勾选会移除当前范围的托管入口；Hooks / 通用规范显式选择移除时只删除当前范围的托管内容。确认页列出写入、备份和清理项，执行后输出已完成信息。
- 用户主目录及其别名不能作为项目范围同步，需选择全局或进入项目目录，避免项目入口与全局入口重合。

| 平台 | 所选 Rules 的项目位置 | 通用基线的全局位置 |
|------|----------|------------------------|
| Claude Code | 根 `AGENTS.md` 的托管规则块 | `~/.claude/CLAUDE.md` |
| Codex | 根 `AGENTS.md` 的托管规则块 | `$CODEX_HOME/AGENTS.md`，默认 `~/.codex/AGENTS.md` |
| OpenCode | 根 `AGENTS.md` 的托管规则块 | `~/.config/opencode/AGENTS.md` |
| Cursor | `.cursor/rules/dwy-<规则名>.mdc` | 不支持文件同步，使用应用设置 |

三种 CLI 共用项目根 `AGENTS.md`。通用规范使用基线托管块，Rules 使用规则托管块，两者独立更新与移除，并保留手写内容。更新 Rules 不清理基线；历史基线入口的迁移只在显式处理通用规范时进行。旧 Claude 基线文件无托管标记时，仅在其内容与当前模板完全一致时清理；无法确认归属的文件保留。

任一所选 CLI 已有有效的 dwy 全局基线时，项目基线只能继承和清理重复项，不能再启用。因为多个 CLI 共用项目文件，混合选择的其他 CLI 若缺少全局规范，需要另行补齐其全局入口。仅存在个人 AGENTS.md 不算已安装。全局启用基线会在清单中列出当前项目重复块清理；全局移除不自动向项目回填。

Hooks 与 Skills 独立管理。全局脚本存在且在对应事件和 matcher 下注册了完整执行命令时，项目继承该 Hook，只为缺少全局提供者的条目补装。全局启用 Hooks 会明确清理当前项目的重复脚本与注册项；显式移除只处理已识别的托管项，保留个人命令、其他设置和个人脚本。不会扫描或自动修改其他项目。

Claude Code 直接读取项目 `AGENTS.md` 需要 v2.1.277 或更新版本，并启用对应内置插件；默认情况下，工作目录及祖先目录中若存在 `CLAUDE.md`、`.claude/CLAUDE.md` 或 `CLAUDE.local.md`，会优先读取这些旧文件。全局 `~/.claude/CLAUDE.md` 会与项目指令一起加载。加载条件见 [Claude Code 官方说明](https://code.claude.com/docs/en/memory#agents-md)。

## Skills 共享副本与老项目迁移

Skills 模板随 CLI 包分发，新增或变更 Skills 需要 CLI 发版；运行时不通过 Git 拉取模板，也不联网检查模板更新。开发时 `DWY_TEMPLATE_SOURCE_DIR` 可优先覆盖模板目录。用户目录 `.dwy/skills/<name>` 保存共享副本，项目和全局通过整个 Skill 目录的链接引用它。项目选择页将被全部适用 CLI 有效全局入口覆盖的 Skills 标注为“全局已启用”并禁选；部分 CLI 已覆盖时仍可选，只补缺少全局入口的项目链接。CLI 最后选择，最终计划重新核算覆盖。

相同平台已有有效全局入口时，项目不保留重复入口，真实目录先备份，清理操作在确认页单独列出。项目同步不改写全局提供者。默认勾选只来自当前范围，不混入另一范围的记录。主交互确认后刷新所选共享内容；`dwy refresh` 获取最新模板，刷新全局和当前项目已启用的 dwy Skills、规范、Hooks 和仍可用的 Rules。其他项目的共享 Skills 链接同时生效，项目独立配置需进入对应项目刷新。显式脚本接口与 `dwy migrate` 默认只补缺，不刷新已有内容。

产品流程 Skills 只声明 `pm-skills`、`superpowers` 的依赖名称与来源，由 AI 检查宿主已安装的 Skill/插件，缺失时按已有授权和项目工具安装规则处理。dwy 不再下载或更新这些外部依赖，已有副本、许可证和版本记录保留。

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
