# ai-tools 内部版本

本目录（`dwy-cli/templates/ai-tools`）rules / skills / hooks / commands / CLAUDE.md 等模板资产的**内部版本**，与 `create-dwy` npm 版本**解耦**。

- 当前版本：见同目录 `VERSION`（单一事实源）
- 用途：模板变更可追溯；发 `create-dwy` 时可对照本 CHANGELOG 摘发布说明；本地/多仓对照「模板包」新旧

## 维护约定（强制）

**每次**修改本目录下任意内容（含新增 / 删除 / 重命名）时，同一变更必须：

1. 按下方规则 bump `VERSION`
2. 在本文件**顶部**（当前版本段之上）追加新版本段
3. 条目写清路径与行为变化，不写空话

禁止：改了模板却不 bump、不写 CHANGELOG。

### 版本号（SemVer，0.x 阶段）

| 级别 | 何时 |
| ---- | ---- |
| **MAJOR**（`x.0.0`） | 破坏性：同步目录结构变更、托管块语义不兼容、删除已被广泛依赖的 skill/rule 且无迁移说明 |
| **MINOR**（`0.y.0`） | 新增 skill / rule / hook / command；既有规范**新增强制约束**或大段能力 |
| **PATCH**（`0.y.z`） | 文案修正、正反例补充、链接修复、不改变强制语义的小改 |

0.x 阶段允许不稳定；仍用 minor / patch 区分「新增能力」与「修正」。

### 版本段格式

```markdown
## x.y.z — YYYY-MM-DD

### Added
- …

### Changed
- …

### Fixed
- …

### Removed
- …
```

无某类变更可省略对应小节。日期用实际合并/提交日（`YYYY-MM-DD`）。

### 与 create-dwy 的关系

- 改本目录 ≠ 自动发 npm；发布 `create-dwy` 时另走 CLI 发版流程，并在 `dwy-cli/CHANGELOG.md` 摘要用户可感变化
- 本文件是模板侧明细；CLI CHANGELOG 可只写要点并指向 ai-tools 版本号（如 `ai-tools 0.1.0`）

---

## 0.28.0 — 2026-09-29

### Changed

- 会变的外部事实改为当前先验：探测失败就换源，当次结果不写回模板。团队栈（Support / Dio / SQLAlchemy、分层、署名、schema_version）不动。
- `rules/Android/`：AndroidAutoSize 只锁 Support 兼容线，`v1.2.1` 是起点先验。
- `rules/Flutter/`：Riverpod、freezed、mocktail 的 caret 标明不是该装的版本，实际走依赖新鲜度。
- `rules/HarmonyOS/dwy-arkts-ui-build.md`：DevEco 路径、模拟器名、hdc 目标改为本机探测。
- `rules/开发流程/dwy-dependency-freshness.md`：各栈查发布时间的 URL 是先验。PyPI 取最早 `upload_time`，Maven `lastUpdated` 不能单独当首次发布。
- `rules/数据库/dwy-postgres.md`：连接池 20/10 改为冷启动先验。无上限或打满 `max_connections` 才算违规。
- `skills/发布发版/dwy-github-action-publish/`：action tag、runner、manylinux、setuptools 下限复制前现查。
- `skills/发布发版/dwy-ios-app-store-release/`：商店字段字数是先验。内购截图像素只留在 `screenshot-specs.yaml`。
- `skills/安全/dwy-deploy-audit/`：镜像源名单不再打通过。公网 IP 多源探测，失败标 unknown，不用内网地址顶上。
- `skills/自媒体/media-platform-packaging/`：小红书 20 字、视频号 16 字、YouTube 逗号改为发布页先验。
- `skills/自媒体/dwy-doubao-tts/`：endpoint 和 `seed-icl-2.0` 移出硬约束。
- `skills/通用/dwy-shared/SKILL.md`：npm 官方源是先验。传播延迟和源不可达分开。
- `skills/DolphinDB/dwy-dolphindb/`：某次机器的 IP、内存、SDK `3.0.4`、500K / 65536 / 255 改为先验。语言约束仍要改。

## 0.27.0 — 2026-09-29

### Changed

- `skills/安全/dwy-deploy-audit/references/checks-runtime.md`：内存和日志配额表改为冷启动先验。有 `docker stats` 或日志日增量时按实测判定。偏离表不再算违规。75% 内存合计和约 5% 日志天花板仍是安全上限。
- `skills/安全/dwy-deploy-audit/scripts/check_capacity.sh`、`check_logs.sh`、`check_docker.sh`：不再把「与 10m/50m/100m 或 65% 一致」印成通过。缺上限、硬限低于实测占用、配额能占满盘，才报问题。
- `rules/Docker/dwy-docker.md`：compose 里的 `512m` / `10m` 标明是字段示例，不是配额。

---

## 0.26.0 — 2026-09-29

### Changed

- `rules/Docker/dwy-docker.md`：镜像版本示例不再当推荐版本。镜像源是当前候选，当次探测后在内容正确的源里取延迟最低的，连通不算通过。
- `skills/Docker/dwy-docker/`：版本必须来自当次 tag 列表。`query_dockerhub.py` 只是 Docker Hub 先验，失败要换 registry。N-1 是偏好。`version-rules.md` / `ask-templates.md` / `templates.md` 里的版本号禁止照抄。
- `skills/Docker/dwy-mirror-source/`：取消「默认阿里云 / DaoCloud 首选」。写入前测延迟。`apply_mirrors.py` 增加 `--docker-mirrors`，按探测顺序覆盖内置列表。
- `skills/Docker/dwy-deploy-first/`：第 1 章合规标准改为当次选出的源或私服，不再把阿里云域名写成唯一合格项。
- `skills/安全/dwy-deploy-audit/`：镜像版本和镜像源的修复提示改指向上述探测，不再写死 N-1 数字和 `*.m.daocloud.io`。
- `rules/开发流程/dwy-dependency-freshness.md`：Docker 一行改为查 tag 首次发布时间。Hub `last_updated` 不能当成首次发布，Hub 不通时换镜像所在 registry。

---

## 0.25.0 — 2026-09-27

### Changed

- `rules/开发流程/dwy-git-commit.md`：提交前必须删掉 AI 署名，含环境自动塞入的 Cursor 署名。写死名单之外的由 AI 自行判断。hook 拦住后删掉再交，禁止绕过。
- `hooks/Git/pre-git-commit-ai-signature-check.sh`：拦截提示改为删掉署名后重试，不再建议手动提交绕过 hook。

---

## 0.24.0 — 2026-09-27

### Added

- `rules/开发流程/dwy-prod-branch.md`：`develop` 只更新测试环境，正式环境用 `preview`。AI 自行判断是否在用 `develop` 部署正式环境；是则按固定提示让用户确认，并建议合并到 `preview`。未确认不部署。

### Changed

- `skills/发布发版/dwy-publish/SKILL.md`：发布前若判断是 `develop` 部署正式环境，先按 `dwy-prod-branch` 问用户。

---

## 0.23.0 — 2026-09-21

### Changed

- `rules/Android/dwy-android-mvp.md`：实际 MVP 架构以当前项目上下文为准；写页面前必须先读本仓 Presenter / Contract / 业务 Base。本文件只定行为，不定骨架。静态页可不写 Presenter。业务 Base 仍落 BizFoundation。
- `rules/Android/dwy-android-core.md` / `dwy-android-layering.md`：去掉强制 Contract 示例与命名

---

## 0.22.0 — 2026-09-21

### Added

- `rules/Android/dwy-android-mvp.md`：手写 Contract MVP；`BaseActivity` / `BaseFragment` / `BaseDialog` 落在 BizFoundation。简单静态页和确认框允许无 Presenter；复杂 Dialog 走 Contract。不引 Mosby / Moxy。

### Changed

- `rules/Android/dwy-android-core.md`：架构改指向 `dwy-android-mvp`；包组织示例 ViewModel 改为 Contract / Presenter
- `rules/Android/dwy-android-layering.md`：域内改为 Presenter；点明业务 Base 在 `:biz-foundation`

---

## 0.21.0 — 2026-09-20

### Changed

- `rules/Android/dwy-android-core.md`：分端只保留设计基准（移动 `390×844` / TV `1280×720`）+ AutoSize `design_width`。去掉 `values-television`、flavor、`uiMode` 运行时切换等区分方式
- `rules/Android/dwy-android-support-only.md`：同步去掉资源分目录要求

---

## 0.20.0 — 2026-09-20

### Added

- `rules/Android/dwy-android-core.md`：屏幕适配分端设计基准。移动端 `390×844` dp（AutoSize 宽 `390`），TV 端 `1280×720` dp（AutoSize 宽 `1280`）；资源 `values` / `values-television`；双端禁止共用 `design_width` 与 dimens

### Changed

- `rules/Android/dwy-android-support-only.md`：Support 仓同步上述分端宽

---

## 0.19.0 — 2026-09-20

### Added

- `rules/Android/dwy-android-core.md`：屏幕适配固定 AndroidAutoSize `v1.2.1`，只按宽度（`design_width_in_dp` 对齐设计稿宽，手机稿 `390`）；禁止按高适配、禁止副单位；页面基类必须 `getResources()` + `AutoSizeCompat`
- `rules/Android/dwy-android-support-only.md`：Support 仓屏幕适配同样走 AutoSize，禁止改用 `androidx.window`

---

## 0.18.0 — 2026-09-20

### Added

- `rules/Android/dwy-android-core.md`：尺寸与字号一律 `dp`，禁止 `px` / `sp`（文字不跟系统字体缩放）；数值走 `dimens.xml`

---

## 0.17.0 — 2026-09-20

### Added

- `CLAUDE.md`：新增「团队基础库缺口回流」。AI 读当前项目识别用户自研基础库；落点按当场情况动态判断（改基础库还是改业务），不写死库名、也不写死「一律先改业务」。落在业务侧则事后总结提问。

---

## 0.16.0 — 2026-09-15

### Added

- `rules/开发流程/dwy-code-craft.md`：编码大局观（无 `paths`，通用包始终注入）。动笔前四问、第二次才抽、扩展靠加文件、反屎山预警、任务内收口 + `project-rules` 自进化；与「简单优先 / 精准改动」的边界写死在借口对照表

---

## 0.15.0 — 2026-09-15

### Added

- `rules/Python/dwy-python-layering.md`：四层目录（`app` / `features` / `biz_foundation` / `foundation`）、Feature 零互依、uv 根 `constraint-dependencies`
- `rules/Vue/dwy-vue-layering.md`：四层目录（`apps/web` / `packages/features` / `biz-foundation` / `foundation`）、Feature 零互依、pnpm `catalog:`
- `rules/Android/dwy-android-layering.md`：四层模块（`:app` / `:features:*` / `:biz-foundation` / `:foundation`）、禁止透传越层、Gradle Version Catalog
- `rules/iOS/dwy-apple-layering.md`：iOS+macOS 双壳、`DesktopKit` 仅桌面壳、根 `Package.swift` 锁定 `from:`

### Changed

- `dwy-python-backend` / `dwy-vue-core` / `dwy-android-core` / `dwy-swift-core`：项目结构改指向对应 layering，不再维护第二套目录树
- `skills/产品0到1/dwy-architecture/SKILL.md`：四层表改为引用 `dwy-*-layering`

---

## 0.14.0 — 2026-09-02

### Changed

- `skills/` 一级目录与同步 Tab 包名对齐：`通用` / `Vue` / `Python` / `Docker` / `DolphinDB`；不再使用 `元工具`、`基础库`、`脚手架`、`运维发布`、`开发流程`（skills）、`数据库`（skills）
- 跨包条目仍一份文件：`dwy-fullstack-scaffold` 放 `Vue/`，Python 包 `skillNames` 点名；`dwy-semver` 放 `发布发版/`，通用包点名

### Removed

- `skills/元工具/`、`skills/基础库/`、`skills/脚手架/`、`skills/运维发布/`、`skills/开发流程/`、`skills/数据库/`（内容已迁到对应包目录）

---

## 0.13.1 — 2026-09-02

### Changed

- 产品0到1 包装 skill：外部 skill 缺失时提示跑 `dwy` 选「刷新全局外部 skill」，不再写已删除的 `dwy skills install`

---

## 0.13.0 — 2026-09-02

### Changed

- `skills/发布发版/dwy-ios-app-store-release`：送审后截图锁死，改图必须撤审 → 换图保序 → 新建 submission 再送；只补现网已有槽；What's New 能力现网图看不到则必须更新截图；凭据优先读仓库 `AGENTS.md` / `CLAUDE.md` 约定。`iphone_65` 补 `preferred: 1242×2688`

---

## 0.12.0 — 2026-09-02

### Changed

- `rules/开发流程/dwy-dependency-freshness.md`：首次技术选型选版本必须只选正式版，禁止 beta / rc / alpha / preview / nightly 等预发布；AskUserQuestion 选项同样不列预发布号。7 天新鲜度约束仍在，两条同时满足

---

## 0.11.0 — 2026-08-18

### Changed

- `rules/开发流程/dwy-git-commit.md`：提交前必须先 `git fetch` + `git pull --rebase --autostash`，冲突全部处理完才能 `git commit`（多人协作，禁止先提交再拉）

---

## 0.10.0 — 2026-08-13

### Added

- `skills/自媒体/dwy-doubao-tts`：豆包声音复刻 2.0 口播配音
  - 脚本随 skill 同步，不放 `~/.grok/skills`
  - API Key / 音色 ID 只读用户全局 `~/.dwy/config.yaml` 的 `doubao_tts`，禁止写入仓库

---

## 0.9.0 — 2026-08-11

### Changed

- **0010 合并竞品 + 演讲地图**：删除分步 `uc-media-0010-topic` / `uc-media-0020-product`
  - 新单一 skill `uc-media-0010-product`：竞品/差异化后 **AI 强制自动填写** 讲/不讲/内容柱/时长
  - 主文档 `0010-product/产品卡-*.md`（§1 竞品 · §2 洞察 · §3 AI 地图）
  - 内容轨：`主题 → 0010 → 0030 按地图扩事实 → 0040`（无 0020 步）
  - flow / CONTRACT / 清单 v7 / 0005 / 0030 / 0040 / README 对齐

---

## 0.8.0 — 2026-08-11

### Changed

- **内容轨因果修正**：`主题 → 0010 竞品 → 0020 演讲地图 → 0030 按地图扩事实 → 0040 蒸馏`
  - skill 重命名：`uc-media-0010-topic`（竞品）、`uc-media-0020-product`（产品卡/地图）
  - 目录：`0010-topic/竞品-*.md`、`0020-product/产品卡-*.md`
  - 0030/0040/0005/flow/CONTRACT/README 全量对齐；清单 version 6
  - 兼容：旧先产品后竞品、旧路径映射表

---

## 0.7.0 — 2026-08-11

### Changed

- **流程优化（P0/P1）**
  - `uc-media-0005-ideation`：候选强制 `seed_links`；人选带入 0020
  - `uc-media-0020-topic`：先消化 seed 再补检；「不做」回写池 `rejected`；正文称竞品包
  - `uc-media-flow` / `CONTRACT`：fast 下 **0050 确认后连跑 0060→0070**；硬停收敛；风格 skill 挂载表
  - `uc-media-0050-design`：可选跨集 `design-defaults.md`，本集只写增量
  - `media-platform-packaging`：登记为可选 **0090 packaging**
  - 执行清单 **version 5**；README 总览流程图

---

## 0.6.0 — 2026-08-11

### Added

- `skills/自媒体/uc-media-0005-ideation/`：选题发现 skill
  - 硬依赖频道档案；多 agent（B站 / YouTube / 短视频 / 可选社区）搜集受众兴趣主题
  - 跨集真源 `.dwy/uc-media/topic-backlog.md`；可选本集快照 `0005-ideation/选题池-*.md`
  - **人选定**后进 0010；禁止自动代选；支持「刷新选题」force
  - 模板：`topic-backlog.template.md` · `选题池.template.md`

### Changed

- `skills/自媒体/uc-media-flow/CONTRACT.md` · `SKILL.md` · `执行清单.template.md`（version 4）：接入 stage `ideation`、PATHS `topic_backlog`、硬停「0005 人选」
- `skills/自媒体/uc-media-0010-product/`：无主题优先导向 0005；主题可来自选题池 `picked`
- `skills/自媒体/uc-media-0020-topic/`：明确为单题竞品，选题发现归 0005
- `skills/自媒体/README.md`：登记 0005 与 `topic-backlog.md`

---

## 0.5.0 — 2026-08-11

### Added

- `skills/自媒体/uc-media-0010-product/templates/channel-profile.template.md`：频道定位·受众·默认分发跨集模板
- `skills/自媒体/uc-media-0010-product/templates/产品卡.template.md`：本集产品卡模板（§0 只读引用频道档案）

### Changed

- `skills/自媒体/uc-media-0010-product/SKILL.md`：拆分双真源——频道档案写 `<project_root>/.dwy/uc-media/channel-profile.md`（有则复用），本集产品卡只写主题·讲/不讲·分块时长；支持「更新频道定位 / 重写受众」强制刷新
- `skills/自媒体/uc-media-flow/CONTRACT.md` · `SKILL.md` · `执行清单.template.md`：频道闸门、PATHS `channel_profile`、进度表 channel 行
- `skills/自媒体/uc-media-0020-topic/` · `uc-media-0040-script/` · `uc-media-0050-design/`：上游必读频道档案；受众/语气/气质不再从本集卡重生成
- `skills/自媒体/README.md`：目录结构补充 `.dwy/uc-media/`

---

## 0.4.2 — 2026-08-10

### Added

- `skills/自媒体/media-platform-packaging/assets/cover-style-master-v1.png`：封面视觉母版（style reference）

### Changed

- `skills/自媒体/media-platform-packaging/SKILL.md`：固定视觉母版约束 + 提示词骨架强制引用该母版；生成后 25% 缩放可读性检查

---

## 0.4.1 — 2026-08-10

### Changed

- `skills/自媒体/media-platform-packaging/`：同步源仓更新
  - 平台表拆分 B站 / YouTube：B站用 `#标签`，YouTube 标签字段用英文逗号分隔关键词
  - `references/platform-copy-examples.md` 增补 YouTube 标签格式示例

---

## 0.4.0 — 2026-08-10

### Added

- `skills/自媒体/media-platform-packaging/`：多平台自媒体包装与封面（源：`xiaoyuan-knowledge-town/.agents/skills/media-platform-packaging`）
  - B站 / 抖音 / 小红书 / 微信视频号标题、简介、标签规则
  - 16:9、4:3、3:4 封面版式与生图流程（依赖 `imagegen`）
  - `references/platform-copy-examples.md`：标题长度与封面文字优先级示例
  - 产出约定写入 `media/0070-package/` 包装清单

### Changed

- `skills/自媒体/README.md`：Skills 表登记 `media-platform-packaging`

---

## 0.3.0 — 2026-08-07

### Added

- 新分类 `skills/自媒体/`：迁入短视频 / 科普自媒体全流程 skills（源：`xiaoyuan-knowledge-town/function-tools/skills`）
  - **编排**：`uc-media-flow`（CONTRACT + 执行清单模板，`fast`/`standard`）
  - **流水线**：`uc-media-0010-product` → `0020-topic` → `0030-facts` → `0040-script` → `0050-design` → `0060-assets` → `0070-package` → `0080-factory`
  - **扩展**：`uc-media-comic-kit`（漫画科普表达）、`uc-media-knowledge-town`（知识小城视觉 / Remotion 预设）
  - 含 scripts（facts HTML、shots 校验、cue timeline）、templates、schema、Remotion 组件资产
  - 硬编路径 `templates/skills/…` 改为 skill 包相对路径，适配 `dwy` sync 后 `.claude/skills/` / `.agents/skills/`

---

## 0.2.0 — 2026-07-23

### Added

- `skills/运维发布/dwy-deploy-first/`：通用「首次部署」skill（分章）
  - 第 1 章：镜像源强制配置 — apt → 阿里云；uv/pip → 阿里云 PyPI
  - 禁止默认 `astral.sh/uv/install.sh`；与 `dwy-mirror-source`（本机工具源）、`dwy-docker`（工程规范）边界划清
  - `references/chapter-01-mirrors.md`：通用 Dockerfile 片段（Debian/Ubuntu/Alpine + uv/pip）

---

## 0.1.0 — 2026-07-20

### Added

- 建立 ai-tools 内部版本：`VERSION` + 本 `CHANGELOG.md` 及维护约定
- `skills/元工具/dwy-shared/SKILL.md`：入库流程增加步骤 6.5，改模板必须同批 bump `VERSION` + `CHANGELOG.md`
- `rules/Android/dwy-android-core.md`：新增「数据实体类封装（强制）」
  - **Java**：字段 `private`，提供 `getXxx`/`setXxx` 与 `toString`；禁止 public 实例字段
  - **Kotlin**：优先 `data class` + `val`（自带 `toString`）；禁止 `@JvmField`；非 data class 必须手写 `toString`
  - 不强制 `equals`/`hashCode`
  - 联动 §2.6 注释、§八反模式、§九自检项 #22
