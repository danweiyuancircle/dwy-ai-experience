# media 流水线契约

> 各 skill **可单独跑**。  
> **铁律 A：** 每个 skill **只落一份主文档**（0070 另加机读 `shots.json`）。  
> **铁律 B：** 本集目录带**序号前缀**，一眼看出结构与顺序。  
> 编排节奏见 flow 的 `run_mode`（`fast` \| `standard`）。

---

## 0. 编号目录（media 根下）

```text
episode_dir/
  media/  或  制作/                 ← work_dir
    执行清单.md
    0010-product/                 ← 产品定义（群体·主题·分发·讲/不讲·分块时长）
    0020-topic/                   ← 选题竞品（多源检索 + 差异化讲法）
    0030-facts/                   ← 技术事实资料库（作者学习·可深；非口播）
    0040-script/                  ← 脚本（脉络+分镜+口播）
    0050-design/                  ← 风格+技术偏好
    0060-assets/                  ← 素材清单 + files/
    0070-package/                 ← 成片包 + shots.json
    0080-factory/                 ← 工厂适配（用户选引擎）
  remotion/                       ← 选 Remotion
  hyperframe/                     ← 选 HyperFrame
```

| 步 | stage | Skill | 目录 | **主文档** |
|----|--------|--------|------|------------|
| 0010 | product | uc-media-0010-product | `0010-product/` | **`产品卡-{主题}.md`** |
| 0020 | topic | uc-media-0020-topic | `0020-topic/` | `选题-{主题}.md`（**必含竞品表**） |
| 0030 | facts | uc-media-0030-facts | `0030-facts/` | `事实-*.md` + `sources.json` + **`index.html`**（作者深库·悬停溯源） |
| 0040 | script | uc-media-0040-script | `0040-script/` | `脚本-{主题}.md` |
| 0050 | design | uc-media-0050-design | `0050-design/` | `design-lock.md` |
| 0060 | assets | uc-media-0060-assets | `0060-assets/` | `素材清单.md` + `files/**` |
| 0070 | package | uc-media-0070-package | `0070-package/` | `成片包.md` + `shots.json` |
| 0080 | factory | uc-media-0080-factory | `0080-factory/` | `适配说明.md` + 工程目录 |
| flow | — | uc-media-flow | work_dir 根 | `执行清单.md` |

**禁止：** 无序号旧路径当新片真源；同一步多份平行终稿；仓根 `channel/profile.md` 当产品真源。

**兼容（旧 → 新）：**

| 旧 | 新 |
|----|-----|
| 0010-channel / 0010-position + 0020-brief | **0010-product** |
| 0030-topic … 0090-factory | **0020-topic … 0080-factory**（序 -10） |

---

## 1. 两段式

```text
内容轨：0010 product → 0020 topic → 0030 facts → 0040 script
制作轨：0050 design → 0060 assets → 0070 package → 0080 factory → render
```

---

## 2. PATHS 键

```text
work_dir
product_dir         # {work_dir}/0010-product
topic_dir           # {work_dir}/0020-topic
facts_dir           # {work_dir}/0030-facts
script_dir          # {work_dir}/0040-script
design_dir          # {work_dir}/0050-design
assets_dir          # {work_dir}/0060-assets
package_dir         # {work_dir}/0070-package
factory_dir         # {work_dir}/0080-factory
remotion_dir        # {episode_dir}/remotion
hyperframe_dir      # {episode_dir}/hyperframe
checklist_file      # {work_dir}/执行清单.md
```

```bash
mkdir -p "{work_dir}"/{0010-product,0020-topic,0030-facts,0040-script,0050-design,0060-assets/files,0070-package,0080-factory}
```

---

## 3. 上游必读

| 步 | 必读 |
|----|------|
| 0020 | `0010-product/产品卡-*.md` |
| 0030 | 产品卡（议题范围）+ 选题（可选）；**深度不限于成片「不讲」** |
| 0040 | `0030-facts/事实-*.md`（深库）+ `0010-product`（架构/受众/不讲） |
| 0050 | `0040-script/脚本-*.md` 已人审 |
| 0060 | design-lock + 脚本 |
| 0070 | 脚本 + design-lock + 素材清单 |
| 0080 | `0070-package/shots.json` 合法；**用户确认工厂** |

---

## 4. 0080 工厂选型

- 0050 design-lock 可写 **偏好** `production_stack`  
- **0080 必须用户二选一：** remotion | hyperframe  
- 未选 → **停**，不写码  

---

## 5. 硬停

**0030 事实**（fast 批次终点）→ **0040 脚本** → **0050 design** → **0070 成片包** → **0080 选型** → render。

---

## 6. `run_mode`

| 模式 | 行为 |
|------|------|
| **fast** | 自动连跑 0010→0020→0030；**0030 事实产出后停**等人确认 |
| **standard** | 每 skill 写完即停，确认后再下一步 |

解析：入参 → 清单 frontmatter → 开跑前问一次。
