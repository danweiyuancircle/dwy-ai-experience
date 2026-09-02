# create-dwy

## 0.18.0

### Minor Changes

- `dwy` / `dwy sync` 开头选动作：同步项目配置（按包或按条目），刷新全局外部 skill，或升级 dwy。删除 `dwy skills` / `dwy skills install` / `dwy scene`。
- 新增 `dwy upgrade`：把全局 `create-dwy` 升到 npm `latest` 正式版（npm/pnpm/yarn/bun）。源码目录拒绝自升级。
- 按包勾选写入 `.dwy/sync-state.json` 的 `selectionStyle` / `packs`。

---

## 0.17.1

### Patch Changes

- `dwy --help` 正式列出 `dwy skills install` / `dwy skills --help`，不再标成隐藏命令。`dwy skills` 无参数时打印 skills 子命令说明。

---

## 0.17.0

### Minor Changes

- `dwy` 交互同步开头增加「同步范围」：完整同步（默认）或仅 Skills。仅 Skills 不写、不删 Rules / Commands / Hooks。
- 最后增加「Skill 同步位置」：默认仅项目目录；可另选 Claude / Grok / Codex / Cursor / OpenCode 全局目录，并勾选要额外拷贝的 skill。只覆盖点名 skill，不删用户 home 里其它个人 skill。选择写入 `/.dwy/sync-state.json` 的 `skillScope` / `syncMode`。

---

## 0.16.1

### Patch Changes

- 交互同步每一步选项支持关键字搜索（Skills / Rules / Commands / Hooks、平台选择、陈旧项删除、导航与汇总确认）。
- 选项说明改为列表下方固定「说明」公共区展示当前聚焦项完整描述，不再跟在选项行尾导致截断错乱。
- 新增 `src/searchable-select.js`（基于 `@clack/core` AutocompletePrompt 自定义 render）；`@clack/prompts` 下限抬至 `^1.7.0`，显式依赖 `@clack/core`。

## 0.16.0

### Minor Changes

- `dwy` 开头自动检测更新全局外部 skill：未装 / 清单变更（cli 加了 skill 或改了 tag）才联网重装，已装且清单一致零开销；失败不阻塞 sync。用户无需再另记 `dwy skills install`。
- 新增 `dwy-commercial` 商业分析 skill（立项阶段 validate 之后、poc 之前）：商业模式 / 变现路径 / 定价 / 单位经济（CAC/LTV/毛利/回本）/ GTM 获客 + 商业可行性结论；startup 模式为硬闸门、builder 模式跳过。包装 pm-skills 的 `business-model` / `monetization-strategy` / `pricing-strategy` / `startup-canvas` / `porters-five-forces` + `gtm-strategy`。
- `dwy skills install` 降级为隐藏的强制刷新兜底（向后兼容保留，日常无需手动）；`printHelp` 只露 `dwy` 主入口，`dwy sync` 为别名。

## 0.15.0

### Minor Changes

- 新增「产品 0→1」三层 skill 体系（总控 `dwy-product-launcher` + 5 个可独立触发的阶段 skill + 13 个产出物级原子 skill）：从模糊想法渐进式推进到上线产品，立项阶段三道闸门（需求市场验证为总闸门 → 技术 POC → MVP≤7），廉价验证在前、昂贵投入在后。
- 新增 `dwy skills install` 命令：把 pm-skills / superpowers 的外部 skill 安装到全局 `~/.dwy/skills/`（一台机一份、全项目共享），含完整 `scripts/` 与 LICENSE；再次运行即覆盖更新。`dwy claude sync` 选中相关 skill 时自动自检安装。
- 外部 skill 进全局纯数据目录而非 `.claude/skills/`，避免被工具当 skill 加载、与 `dwy-*` 触发冲突。
- 改造 `dwy-whiteboard-prototype`：配色按产品定位推荐（保留 `:root` 语义变量结构）、尺寸按目标端推荐、图标不再用 emoji。

## 0.14.7

### Patch Changes

- 平台选择交互默认按当前项目本地目录回填：存在 `.claude`、`.codex` / `.agents` / `AGENTS.md`、`.cursor`、`.opencode` 时，自动勾选对应平台；无本地目录时退回默认 `Claude Code + Codex`。
- 将跨语言通用基础约束并入 `CLAUDE.md`，删除重复的 `rules/Global/dwy-common-code-baseline.md`，减少全局规则分散。
- 将 Docker 规则从 `rules/Global/dwy-docker.md` 调整到 `rules/Docker/dwy-docker.md`，按技术域归类。
- 为 Android 与 Flutter 规则补充全面屏、刘海屏、挖孔屏适配约束，统一要求基于安全区域与响应式布局实现。

## 0.14.6

### Patch Changes

- `dwy` 交互同步时，默认勾选优先读取项目目录下 `/.dwy/sync-state.json` 的上次托管选择结果，减少每次重新勾选 `rules`、`skills`、`commands`、`hooks`。
- 新增 iOS 适配开发规则 `dwy-ios-layout-adaptation.md`，统一原型基准为 `393×852 pt`，补充 `375 / 393 / 430 pt` 验证矩阵与 Safe Area 约束。
- 补充 iOS 与 Android 应用图标安全边距规则：iOS 图标源稿使用 `1024x1024` PNG，Android 启动图标源稿使用 `mipmap-xxxhdpi` `192x192`，主体默认预留 `10%` 安全边距。

## 0.14.5

### Patch Changes

- `dwy` 同步模板改回运行时从仓库缓存拉取，默认更新 `~/.dwy/cache/dwy` 后再读取模板，不再依赖 CLI 包内静态模板。
- 新增项目级同步状态文件 `/.dwy/sync-state.json`，记录各平台上次由 `dwy` 托管的 skills / rules / commands / hooks。
- 当模板仓库移除已同步项时，再次执行 `dwy` 会罗列缺失项并让用户选择是否删除；未确认删除的旧项会继续保留。

## 0.14.4

### Patch Changes

- 将 iOS 规则 `dwy-swift-style.md` 重命名为 `dwy-swift-core.md`，并重构为精简版规范。
- 新增规则级配置收口约束，要求可配置项统一在 `AppConfig` 管理。
- 加强国际化规则：默认要求中文/英文支持，统一 `localizationBundle + loc() + LocalizationManager + AppLanguage` 实施要点。
- 模板同步改为仅使用 CLI 内置 `dwy-cli/templates/ai-tools`，不再读取外部缓存目录或按 `origin` 拉取远端模板仓库。

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
- 模板源统一收敛到 `/Users/chances/WebstormProjects/dwy-shared/dwy-cli/templates/ai-tools`，随 CLI 包一起发布，不再运行时拉取远端模板仓库。
- 新增多平台适配层：支持 `Claude Code`、`Codex`、`Cursor`、`OpenCode` 的 rules / skills / commands / hooks 同步。
- 基准规范文件 `/Users/chances/WebstormProjects/dwy-shared/dwy-cli/templates/ai-tools/CLAUDE.md` 现在会按平台分别同步到 `.claude/CLAUDE.md`、根 `AGENTS.md`、`.cursor/rules/00-dwy-global.mdc`。
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
