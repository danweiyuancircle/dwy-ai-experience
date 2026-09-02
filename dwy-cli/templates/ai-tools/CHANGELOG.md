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
