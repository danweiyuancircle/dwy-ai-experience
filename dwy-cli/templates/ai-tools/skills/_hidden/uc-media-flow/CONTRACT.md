# media 流水线契约

> **铁律 A：** 每 skill 一份主文档（0070 + shots.json；0005 跨集池）。  
> **铁律 B：** 本集目录带序号前缀。  
> **铁律 C：** 频道定位/受众跨集固化。  
> **铁律 D：** 定题须人（0005）；**0010 内 AI 必须自动写出演讲地图**（可改）。  
> **铁律 E：** `主题 → 0010（竞品+推荐地图）→ 0030 按地图扩事实 → 0040 蒸馏`。  
> **铁律 F：** seed_links → 0010 必读复用。

---

## 0. 目录

```text
project_root/
  .dwy/uc-media/
    channel-profile.md
    topic-backlog.md
    design-defaults.md          # 可选
  episode/media/                # work_dir
    执行清单.md
    0005-ideation/              # 可选快照
    0010-product/               # 竞品 + AI 推荐演讲地图（合并）
    0030-facts/
    0040-script/
    0050-design/
    0060-assets/
    0070-package/
    0080-factory/
```

| 步 | stage | Skill | 主文档 |
|----|--------|--------|--------|
| 频道 | channel | 0010 闸门 | channel-profile.md |
| 0005 | ideation | uc-media-0005-ideation | topic-backlog.md |
| **0010** | **product** | **uc-media-0010-product** | **`0010-product/产品卡-*.md`** |
| 0030 | facts | uc-media-0030-facts | 事实-*.md + sources + index.html |
| 0040 | script | uc-media-0040-script | 脚本-*.md |
| 0050 | design | uc-media-0050-design | design-lock.md |
| 0060 | assets | uc-media-0060-assets | 素材清单.md |
| 0070 | package | uc-media-0070-package | 成片包 + shots.json |
| 0080 | factory | uc-media-0080-factory | 适配说明 + 工程 |
| 0090 | packaging | media-platform-packaging | 可选包装 |
| flow | — | uc-media-flow | 执行清单.md |

**0010 产品卡内含（单文件）：** 竞品表 · 差异化 · **AI 推荐讲/不讲/分块时长**。

**兼容：**

| 旧 | 新 |
|----|-----|
| 0010-topic + 0020-product 两步 | **仅 0010-product** |
| `0010-topic/竞品-*` · `0020-product/产品卡-*` | 合并进 `0010-product/产品卡-*` |
| 先地图后竞品 | 废；先分析后推荐地图（同步） |

---

## 1. 流程骨架

```text
跨集 channel-profile
可选 0005 人选主题
0010 竞品+差异化 → AI 自动推荐演讲地图（同文档）
0030 按地图内容柱扩事实
0040 按地图蒸馏口播
0050→0060→0070→0080→render
可选 0090 packaging
```

---

## 2. PATHS

```text
channel_profile, topic_backlog, design_defaults
work_dir
product_dir     # {work_dir}/0010-product
facts_dir       # {work_dir}/0030-facts
script_dir      # {work_dir}/0040-script
…
```

```bash
mkdir -p "{project_root}/.dwy/uc-media"
mkdir -p "{work_dir}"/{0005-ideation,0010-product,0030-facts,0040-script,0050-design,0060-assets/files,0070-package,0080-factory}
```

---

## 3. 上游必读

| 步 | 必读 |
|----|------|
| 0005 | 频道 |
| **0010** | 主题 + 频道 + seed_links |
| **0030** | **0010 产品卡 §3 内容柱**（硬） |
| 0040 | 0030 + **0010 地图** + 频道 |
| 0050+ | 同前 |

---

## 4–5. 工厂与硬停

0080 须确认工厂。  
硬停：**0005 人选** · **0010**（地图确认；fast 可连）· **0030** · **0040** · **0050** · **0070** · **0080** · render · 可选 0090。

---

## 6. `run_mode`

| 模式 | 行为 |
|------|------|
| **fast** | 无主题 0005 停 → **0010→0030 连跑后停** → 0040 停 → 0050 停 → 连 0060–0070 → 0080 |
| **standard** | 每步确认；0010 含「采纳/改地图」 |

0010「不做」→ 不进 0030。

---

## 7. 刷新

channel / backlog / design-defaults 触发词同前。  
0010 不做 → rejected；成片 → done。
