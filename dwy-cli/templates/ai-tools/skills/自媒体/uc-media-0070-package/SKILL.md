---
name: uc-media-0070-package
description: |
  成片包（0070）：0070-package/成片包.md + shots.json。工厂入口。
  触发词：package、成片包、对轨冻结、0070。
---

# uc-media-0070-package · 成片包

**Schema：** [`shots.schema.json`](./shots.schema.json)  
**模板：** [`成片包.template.md`](./成片包.template.md)  
**说明：** [`人审说明.md`](./人审说明.md)

## 行为（本 skill 内聚）

1. **能自动的全部自动**：从脚本 + design-lock + 素材清单组装 `成片包.md` + `shots.json`，并跑 validate。
2. **产出可改终稿**：人审改时长/vo 后重校验。
3. **不确定不胡编**：上游缺失不猜秒数、不编 vo。  

使用 `knowledge-town-paper-film-v1` 时，另产出 `cue-timeline.json` 作为字幕、旁白、视觉动作与 SFX 的唯一对轨真源；`shots.json` 写入 `cue_timeline_file` 和每镜 `cue_ids`，但不复制或改写 cue 时码。

**本步硬停：** 人审通过前不进 0080。

---

## 大步骤契约

| 项 | 内容 |
|----|------|
| **序** | 0070 |
| **stage** | `package` |
| **目录** | `{work_dir}/0070-package/` |
| **人读** | **`成片包.md`** |
| **机读** | **`shots.json`** |
| **上游** | 脚本 + design-lock + `0060-assets/素材清单.md` |
| **下游** | 0080-factory |

```bash
# 脚本相对本 skill 包（sync 后：.claude/skills/uc-media-0070-package/ 或 .agents/skills/…）
python3 scripts/validate_shots.py \
  "{work_dir}/0070-package/shots.json"
```
