---
name: uc-media-0060-assets
description: |
  素材（0060）：0060-assets/素材清单.md + files/。触发词：素材、配图、生图、logo、0060。
---

# uc-media-0060-assets · 素材

## 行为（本 skill 内聚）

1. **能自动的全部自动**：按脚本镜号 + design-lock 生成完整 `素材清单.md`；能从 `shared/icons` 定位的 logo 先填好。  
2. **产出可改终稿**：用户改 method、补 `user_provided` 即可。  
3. **不确定不胡编**：找不到的官方 Logo 不 AI 乱画当真标；路径不存在标 `missing`。

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0060 |
| **stage** | `assets` |
| **目录** | `{work_dir}/0060-assets/` |
| **主文档** | **`素材清单.md`** |
| **媒体** | `files/**` |
| **上游** | `0050-design/design-lock.md` + `0040-script/脚本-*.md` |
| **禁止** | 每镜一篇说明 md 当真源 |

清单表含：shot_id / 层 / method / 路径 / 就绪；支持 `user_provided`。  
