---
name: uc-media-0050-design
description: |
  制作设计（0050）：本集 design-lock.md；优先复用跨集 design-defaults，只写本集增量。
  触发词：设计风格、style-lock、制作技术、0050。
---

# uc-media-0050-design · 制作设计

## 行为（本 skill 内聚）

1. **先读跨集默认（若有）**  
   `{project_root}/.dwy/uc-media/design-defaults.md`  
   无则从频道档案气质 + 近集惯例推断，并可**首次**写入 defaults（用户未反对时）。  
2. **写本集** `design-lock.md`：= defaults 引用 + **本集增量/例外**（勿整份重抄气质长文）。  
3. **不确定不胡编**：工厂只写 **偏好** / `undecided`；最终以 **0080 人选** 为准。

**硬停：** 人审前不进 0060。  
**flow `fast`：** 本步确认后可连跑 0060，在 0070 再停（见 flow 硬停表）。

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0050 |
| **stage** | `design` |
| **目录** | `{work_dir}/0050-design/` |
| **主文档** | **`design-lock.md`** |
| **上游** | `0040-script` 已人审；频道档案；可选 `design-defaults.md` |
| **风格扩展** | `uc-media-comic-kit` / `uc-media-knowledge-town`（若项目采用，按各自 skill 挂载） |
| **不做** | 批量生图；替用户最终锁定工厂 |

### design-lock 要点

- `style_id` / 气质 / 禁止项（可写「同 design-defaults」）  
- `production_stack` **偏好**：`remotion` | `hyperframe` | `undecided`  
  - 若 defaults 已有默认工厂偏好，本集只写覆盖  
- `asset_model` / 字幕安全区 / comic-kit 与否  
- 本集例外表（仅本集）  
- 签字：可进 0060  

### 跨集 design-defaults（可选，建议）

路径：`.dwy/uc-media/design-defaults.md`  

| 块 | 内容 |
|----|------|
| 默认 style_id / 气质关键词 | 与频道档案对齐 |
| 默认 production_stack 偏好 | |
| 禁止项 / 字幕安全区 | |
| 风格 skill | comic-kit / knowledge-town / 无 |

刷新：用户说「更新设计默认 / 重设画风默认」。  
