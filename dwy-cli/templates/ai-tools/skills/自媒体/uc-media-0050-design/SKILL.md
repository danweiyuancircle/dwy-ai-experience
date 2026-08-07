---
name: uc-media-0050-design
description: |
  制作设计（0050）：0050-design/design-lock.md；可预填工厂偏好，0080 仍由用户确认。
  触发词：设计风格、style-lock、制作技术、0050。
---

# uc-media-0050-design · 制作设计

## 行为（本 skill 内聚）

1. **能自动的全部自动**：读已人审脚本 + 产品气质 + 近集成片惯例，写满 `design-lock.md`（含 `production_stack` **偏好**）。  
2. **产出可改终稿**：用户改风格字段即可。  
3. **不确定不胡编**：工厂未表态不得写成最终锁定（只写偏好 / undecided）。

**本步硬停：** 人审通过前不进 0060。工厂最终以 **0080 用户选择** 为准。

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0050 |
| **stage** | `design` |
| **目录** | `{work_dir}/0050-design/` |
| **主文档** | **`design-lock.md`** |
| **上游** | `0040-script/脚本-*.md` 已人审 |
| **不做** | 批量生图；替用户最终锁定工厂 |

### design-lock 要点

- `style_id` / 气质 / 禁止项  
- `production_stack` **偏好**：`remotion` | `hyperframe` | `undecided`  
- `asset_model` / 字幕安全区 / 是否 comic-kit  
- 签字：可进 0060  
