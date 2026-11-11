# create-dwy

## [0.35.0] - 2026-11-11

### Changed

- 产品流程只声明 `pm-skills`、`superpowers` 的依赖名称和来源，由 AI 检查宿主已有 Skill/插件并按授权处理；同步、刷新和升级不再下载或更新外部依赖，保留已有副本、许可证和版本记录。
- 工具发现按新增或扩展能力触发，明确小改动、熟悉技术栈和复用依赖仍须核实适配，并区分触发与重新检索。
- Apple Skills 最低支持 iOS / iPadOS 18，移除 iOS 17 兼容与测试要求；macOS 最低仍为 15。模板详情见 ai-tools 0.39.0。

### Removed

- 移除外部 Skills 下载器、产品流程自动补装操作及脚本安装动作，不再锁定外部 Skill 的版本或安装目录。

---

## [0.34.0] - 2026-11-09

### Added

- 随包提供 `dwy-tool-discovery` Skill，开发前按实际任务优先核实官方及成熟开源工具，安装前明确展示方案并取得确认。模板详情见 ai-tools 0.38.3。

### Fixed

- 外部 Skills 每个仓库拉取上限 15 秒；刷新时拉取失败或超时提示并跳过，保留旧副本和版本记录，继续处理其他来源，不阻断刷新。
- 所有来源拉取失败时不改写版本清单、不报告安装成功；文件复制或替换失败仍报告错误。

---

## [0.33.0] - 2026-11-09

### Added

- `dwy refresh` 同时刷新全局和当前项目已启用的共享 Skills、通用规范、Hooks 和仍可用的 Rules，保留个人内容、历史条目和已有选择。
- 刷新已安装外部 Skills 到 CLI 固定版本，不补装未选择项；复制或替换失败时保留原副本并报告错误。
- `dwy upgrade` 在版本验证后执行完整配置刷新；帮助和同步说明同步更新刷新范围。

---

## [0.32.0] - 2026-11-09

### Added

- 新增项目经验 Skill，在项目内按需查阅和沉淀可复用教训，并支持迁移旧自成长规则。

### Fixed

- 发布缓存仅提示忽略 `/.dwy/publish/`，避免隐藏其他项目资料。模板详情见 ai-tools 0.37.0。

---

## [0.31.0] - 2026-11-09

### Added

- Codex 中由 dwy 同步的 Hook 执行时显示带 `dwy` 前缀的功能说明，便于识别来源。模板详情见 ai-tools 0.36.1。

---

## [0.30.0] - 2026-11-08

### Added

- 支持通过 `dwy source` 查看、设置或清除本地模板来源，优先使用本地仓库或模板目录；本地不可用时回退 GitHub。

---

## [0.29.0] - 2026-11-08

### Added

- 同步时从 GitHub develop 获取最新 AI 模板，Skills 更新无需单独升级 CLI；网络不可用时回退本地缓存或随包模板。
- 成功检查模板更新后显示所用仓库提交时间，方便确认模板来源的新旧。

---

## [0.28.1] - 2026-11-08

### Changed

- 项目同步在确认后清理可识别的旧 Rules 托管内容，不再因旧规则自动勾选替代 Skills；个人内容和无法确认归属的文件继续保留。

---

## [0.28.0] - 2026-11-08

### Changed

- 将 Android、Flutter、HarmonyOS、数据库、Docker 和开发流程的剩余 Rules 迁移到按需安装的 Skills；补充旧项目的安全迁移与选择。
- 同步交互不再分发或选择 Rules；Claude Code、Codex 和 OpenCode 保持支持，原 Cursor 配置保留且不再提供同步入口。
- 模板详情见 ai-tools 0.35.0。

---

## [0.27.0] - 2026-11-07

### Changed

- 新增 Python、Vue 和 Apple 按需开发、架构与基础库 Skills；按版本查找公开接口和接入说明。
- 迁移 Python、Vue 旧托管 Rules，推荐对应 Skills；未选择替代项时保留旧内容，预览并保护个人配置。其他技术栈 Rules 保持可用。
- 修正 EUI、EAPI 版本线匹配范围和 Ekit Skill 元数据；模板详情见 ai-tools 0.34.0。

---

## [0.26.0] - 2026-11-06

### Changed

- `dwy-publish` 独立判断发版版本，移除 `dwy-semver`；已有安装需改用 `dwy-publish`。
- `dwy-sdk-spec` 改为 `dwy-commercial-sdk`，依据项目实际商业 SDK 保护要求检查，不再缓存项目配置；已有安装需选择新 skill，旧入口需自行移除。
- 模板详情见 ai-tools 0.33.0。

---

## [0.25.3] - 2026-11-06

### Patch Changes

- 修复项目中全局 Skills 禁选后，已启用分类 Tab 失去颜色区分的问题。包含项目已勾选或全局已启用 Skills 的非当前分类保持青色，当前分类保持青色底；禁选逻辑和可勾选项计数保持不变。
- 补充部分／全部全局覆盖状态以及真实交互输出的颜色回归。

---

## [0.25.2] - 2026-11-06

### Patch Changes

- 恢复 AI 模板随 CLI 包分发，移除启动时的远端 Git 检查、下载和模板缓存读取，避免运行 `dwy` 长时间等待。Skills 变更通过发布 CLI 交付，`dwy refresh` 从当前包内模板刷新已安装副本；保留显式开发目录覆盖。
- 补齐普通项目交互的全局 Skills 禁选：有效全局入口已覆盖的条目标注“全局已启用”，禁止重复勾选；末步新增其他 CLI 时只补缺失入口，保留已有全局内容。
- 保留范围优先、CLI 末尾选择、全局规范与 Hooks 跳页以及升级后的实际版本校验。

---

## [0.25.1] - 2026-11-06

### Patch Changes

- 修复 `dwy upgrade` 查询官方源却从滞后镜像安装 `latest`，实际仍是旧版却显示升级成功的问题。查询与安装使用同一 registry，并固定查询所得的正式版本，不修改用户的镜像配置。
- 安装后检查当前 PATH 中实际执行的 `dwy --version`，版本一致才刷新共享 Skills 并报告成功；刷新失败单独报错。补充旧版入口、真实子进程回读和 registry 输入校验回归。

---

## [0.25.0] - 2026-11-06

### Minor Changes

- 同步流程简化为「范围 → Skills → 项目 Rules → 通用规范 → Hooks → CLI → 预览确认」。规范和 Hooks 默认启用；Codex 默认选中，并恢复当前范围已同步的其他 CLI。项目已有有效全局规范或完整 Hooks 时跳过对应选择，不重复安装。
- 模板从公开源码仓库 master 分支运行时获取，新增 Skills 无需再发布 CLI。使用增量 Git 对象缓存和验证后的模板快照；离线保留有效缓存，无缓存才回退随包模板。首次下载显示进度，异常退出后的锁可自动恢复。
- 确认后刷新当前范围所需的共享 Skills，项目补其他 CLI 入口时保留有效全局同名共享内容；执行后报告实际完成信息。保留旧脚本的显式同步范围、个人配置及取消前目标不写入的约束。
- 新增版本克制与想法收录 Skill，支持新增功能分析、阶段收敛、持久化想法清单和新版本规划提醒。
- 修复无同步记录的旧 Cursor Rules 默认选择恢复，补充全局继承、内容保护、增量更新、离线及多进程锁回归，并更新同步帮助与使用说明。

---

## [0.24.1] - 2026-11-03

### Patch Changes

- 包含 0.24.0 的 Skills / Hooks / Rules / 通用规范管理、显式移除和全局去重能力。
- 收敛配置管理集成测试的无断言日志，规避 Node 22 测试运行器在大量中文 stdout 下的 IPC 反序列化问题；保留全部断言和真实终端输出测试，不改变 CLI 行为。

---

## [0.24.0] - 2026-11-03

### Minor Changes

- 全局提供 Skills、Hooks 和 AGENTS.md 通用规范，项目另外提供 Rules。全局首次默认启用通用规范；Hooks 与规范增加显式启用/更新和移除动作，未选择的类型保持原样，规范移除后不自动复选。
- 项目通用规范与 Rules 分别操作各自托管块，移除任一项保留其他内容。任一所选 CLI 已有有效全局基线时，项目禁止重复安装，共享项目文件的混合平台场景提示补齐缺失的全局入口。
- Hooks 按有效脚本及对应事件、matcher 和完整命令注册判断全局提供者，项目只补缺失项。全局启用后明确清理当前项目重复脚本和注册项；移除全局配置不自动回填项目。
- Hook 清理支持历史托管项，保留同名个人路径、组合命令和其他设置；配置目录及单文件链接在规划和执行时检查，防止项目操作穿透改写全局或外部目标。
- 补充配置独立启停、移除记忆、继承、取消及真实终端回归，旧测试统一注入临时用户目录。

---

## [0.23.0] - 2026-11-02

### Minor Changes

- 同步改为「范围 → 平台 → 本次处理内容 → 逐项选择 → 清单确认」。默认只选 Skills；项目 Rules、全局通用规范和 Hooks 必须显式选择，未选择的类型及其记录保持原样。全局不提供 Cursor。
- 默认勾选只读取当前范围及所选平台。项目 Skills 全部适用平台已有有效全局入口时显示“全局已启用”并禁用重复勾选；部分平台覆盖时只为缺少入口的平台安装。
- 确认页和执行共用操作清单，列出共享副本、入口、旧项清理、配置和同步记录。项目去重只备份或移除项目入口，不改写全局提供者；用户主目录及其别名不能作为项目范围同步。
- `sync` / `migrate` 只准备缺失或损坏的共享副本，已有内容由 `refresh` / `upgrade` 刷新。产品流程的外部依赖补装也纳入确认清单，只拉取缺失内容并保留已有副本。
- 全局 Codex Hooks 遵循自定义 `CODEX_HOME`，命令路径正确引用空格和单引号；同步保留个人配置，补充平台兼容、取消无写入和真实终端交互回归。

---

## [0.22.0] - 2026-11-02

### Minor Changes

- Skills 改为用户目录 `.dwy/skills/<name>` 内的一份共享副本，项目和全局入口使用整个目录的软链接；同平台已有有效全局入口时清理项目重复入口。原真实目录先备份，自定义 Skills、Rules 和 Hooks 保留。
- 新增 `dwy migrate`，在老项目根目录一键迁移已有托管 Skills，无需重新勾选；重复执行不重复备份，已移除的历史模板和已有整个 Skills 根目录链接保留并报告。
- 新增 `dwy refresh`，使用当前 CLI 包内模板刷新所有已安装的共享副本；`dwy upgrade` 升级成功后自动调用新进程刷新，所有已迁移项目无需分别更新。
- 共享副本刷新加入互斥及整批失败恢复；扫描和清理统一保护目录链接目标，防止自链和穿透根链接误删文件。全局默认选择覆盖自定义 `CODEX_HOME`。
- CHANGELOG 规则明确要求每个版本条目包含版本号和日期，禁止 `Unreleased` 等占位标题，与是否发布无关；发布记录提取兼容带日期和方括号的版本标题。

---

## 0.21.0

### Minor Changes

- 通用基线默认写入所选 AI CLI 的全局入口：Claude Code 使用 `~/.claude/CLAUDE.md`，Codex 使用 `$CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`），OpenCode 使用 `~/.config/opencode/AGENTS.md`。
- Claude Code、Codex、OpenCode 的所选 Rules 共用项目根 `AGENTS.md` 的托管规则块，项目不再重复注入通用基线。位置选择仅控制 Skills / Hooks；Cursor Rules 始终写入项目。
- 基线源文件及项目脚手架模板统一使用 `AGENTS.md`，新增新功能开发前的官方／成熟社区工具发现与风险评估规则。
- 迁移可识别的旧托管基线和 Rules，保留个人内容；全局历史 Rules 不再成为新项目的默认选择，切换 CLI 后取消的共享规则不会重新勾选。
- 更新确认预览、命令行帮助和接入说明，覆盖全局基线、项目 Rules、旧配置迁移及取消无写入的验证。

---

## 0.20.0

### Minor Changes

- 同步流程简化为 Skills → Rules → 全局／当前项目 → 平台 → 确认。按实际分类逐项勾选，无回退；移除动作、初始化、同步范围、技术栈包和场景包菜单。
- 全局同步整套配置到 Claude Code、Codex、OpenCode 用户目录，保留个人规则和设置；Cursor 只提供项目规则同步。
- 最终确认列出更新和删除的托管项；取消不写配置，不清理未选择的平台。旧同步记录沿用已选条目。
- Hooks 按支持的平台自动同步；Commands 停用，保留已有命令文件。
- 启动展示 dwy 品牌；列表只展示勾选框和名称，移除重复类型标签。
- `dwy --help` 补充同步步骤、交互按键、常见用法及平台支持说明。

---

## 0.19.1

### Patch Changes

- 上下移动时当前条目用指针 + 反底标出。原先只靠 dim，已勾选或 JetBrains 终端里看不出光标。

---

## 0.19.0

### Minor Changes

- 按包勾选改为顶部 Tab + 下方多选：技术栈和场景包同一屏，`←/→` 切 Tab，Space 勾子项，`a` 全选本 Tab。skill / rule / hook 用图标和颜色区分。
- `skills/` 模板目录与包名对齐（`通用` / `Vue` / `Python` / `Docker` / `DolphinDB` 等）。对应 ai-tools `0.14.0`。

---

## 0.18.4

### Patch Changes

- 按包勾选改用 `@clack/prompts` 的 `groupMultiselect`：Space 勾父级=全选子项，子项可单独取消。去掉「下一步再取消子项」那一屏。

---

## 0.18.3

### Patch Changes

- 技术栈/场景包下的子条目随父包显示为已勾选，不再画成删除线空框。逐条取消仍在下一步预勾清单里。

---

## 0.18.2

### Patch Changes

- 技术栈包与场景包都会在包名下列出子条目；选包后统一进入预勾清单，可逐条取消。

---

## 0.18.1

### Patch Changes

- `dwy` 菜单只留两项：同步全局 skills、同步项目配置。升级只走 `dwy upgrade`。
- 同步项目配置里分「按场景和技术栈」与「一个一个选」。按包后直接列出已预勾子条目，可取消。

---

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
