# create-dwy

## 0.14.3

### Patch Changes

- 完善 Git 提交相关规范与模板文档，统一提交规则与 AI 署名治理说明。
- 优化 iOS 规则中图标策略，优先 SF Symbols，缺省使用成熟第三方 SVG 方案。
- 强化 `dwy-tdd-dev` 与 `dwy-0to1` 流程文档内的提交规范引用方式。

## 0.14.2

### Patch Changes

- 重构 `templates/ai-tools/skills/运维发布/dwy-publish`：主入口只负责识别“应用部署”或“SDK 发版”，再按类型读取独立流程文件。
- 新增 `references/application-release.md` 与 `references/sdk-release.md`，将应用部署和 SDK 发版流程拆开，避免单文件内混合两套末端流程。
- `dwy-publish` 主入口改为使用相对路径读取流程文件，避免模板内写死仓库绝对路径。

## 0.14.1

### Patch Changes

- 修正 `templates/ai-tools/skills` 内多处写死的绝对 skill 路径，统一改为 skill 内相对路径，例如 `./scripts/`、`./references/`、`./preference.json`，避免项目级/插件级安装时路径失效。

## 0.14.0

### Minor Changes

- CLI 重构为单一交互式入口，移除旧的命令式 `create` / `sync` / `claude` / `codex` 流程。
- 模板源统一收敛到 `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/ai-tools`，随 CLI 包一起发布，不再运行时拉取远端模板仓库。
- 新增多平台适配层：支持 `Claude Code`、`Codex`、`Cursor`、`OpenCode` 的 rules / skills / commands / hooks 同步。
- 基准规范文件 `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/ai-tools/CLAUDE.md` 现在会按平台分别同步到 `.claude/CLAUDE.md`、根 `AGENTS.md`、`.cursor/rules/00-dwy-global.mdc`。
- 平台未选中时会清理 dwy 托管内容，同时保留用户自定义文件、用户自定义 hook 配置和 `AGENTS.md` 非托管内容。

## 0.13.8

### Patch Changes

- GitHub Release 改为只展示当前版本的 changelog 段落，不再附带 full release notes，便于按版本查看真实发布内容。

## 0.13.7

### Patch Changes

- `dwy` 同步模板前会先检查本地缓存仓库 `origin` 是否仍指向当前 CLI 目标仓库 `https://github.com/danweiyuancircle/dwy-ai-experience.git`；若不一致，则删除 `/Users/chances/.dwy/cache/dwy` 后重新 clone，避免旧 Gitee 缓存继续被 pull。

## 0.13.6

### Patch Changes

- 调整 CLI 发布工作流，GitHub Actions 在 npm 发布完成后自动创建对应的 GitHub Release，版本展示统一为 `create-dwy@x.y.z`。

## 0.13.5

### Patch Changes

- 默认模板仓库源改为 GitHub：`DWY_REPO_URL` 从 `https://gitee.com/snailyuanyuan/dwy-shared.git` 切换为 `https://github.com/danweiyuancircle/dwy-shared.git`，确保 `dwy` CLI 同步链路只跟踪 GitHub。

## 0.13.4

### Patch Changes

- 默认模板仓库源改为 GitHub：`DWY_REPO_URL` 从 `https://gitee.com/snailyuanyuan/dwy-shared.git` 切换为 `https://github.com/danweiyuancircle/dwy-shared.git`，确保 `dwy` CLI 同步链路只跟踪 GitHub。

## 0.13.2

### Patch Changes

- 新增顶层命令 `dwy sync`，一次选择后同时同步 Claude Code 与 Codex 配置。
- `dwy sync -i` 支持重新交互式选择；`dwy sync --dry-run` 支持预演；`dwy sync md` 同步 `CLAUDE.md` 到 `~/.claude/CLAUDE.md` 和 `~/.codex/AGENTS.md`。
- 复用现有 `dwy claude sync` / `dwy codex sync` 的扫描、缓存选择、删除未选模板项和写入逻辑；`commands` 仅同步到 `.claude/commands`，`skills` / `rules` / `hooks` 同步到两端。
- 新增 CLI 聚合同步回归测试，覆盖一次缓存选择同时写入 `.claude`、`.agents`、`.codex` 和 `AGENTS.md`。
