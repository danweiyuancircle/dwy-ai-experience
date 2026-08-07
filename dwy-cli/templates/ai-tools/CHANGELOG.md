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
