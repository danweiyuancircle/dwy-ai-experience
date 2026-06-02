---
project: <产品名>
slug: <kebab-slug>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
current_step: 1
target_platform: none       # Step3 选定后改: ios | android | desktop | web | none
---

# <产品名> · 0→1 孵化状态

> 本文件是整条流水线的唯一真相源。每过一个门必须更新它。

## 进度

| 步 | 名称 | 状态 | 产物 | gate |
|---|------|------|------|------|
| 1 | 需求&市场分析 | pending | 01-market.md | |
| 2 | 技术可行性 | pending | 02-tech-feasibility.md | |
| 3 | 实测spike | pending | 03-spike-result.md | |
| 4 | 粗PRD | pending | 04-prd-coarse.md | |
| 5 | 低保真原型 | pending | prototype-lowfi/ | |
| 6 | 高保真原型 | pending | prototype-hifi/ | |
| 7 | 细PRD | pending | 05-prd-detailed.md | |
| 8 | 版本规划 | pending | 06-version-plan.md | |
| 9 | 开发 | pending | plans/ | |

<!-- 状态枚举：pending | in-progress | awaiting-approval | done | skipped(原因) -->
<!-- gate 列：门过了填 ✅ + 日期（如 ✅ 2026-06-02）；待用户确认填 ⏳ -->

## 关键决策

<!-- 每步定下的、后续步骤要用的决策都记在这里 -->
- 真需求结论：<Step1，做 / 不做 / 调整方向>
- 差异化打法：<Step1>
- 技术方案：<Step2 选定的库/方案>
- 是否实测：<Step3，是(端=xxx) / 否>
- 端：<Step3 选定：ios|android|desktop|web|none>
- 产品定位：<Step4>
- 定价策略：<Step4>
- 选定版本：<Step8，可多个，如 v1+v2>

## 版本开发进度（Step 9）

| 版本 | 实施计划 | 状态 | code-review |
|------|---------|------|-------------|
| v1 | plans/v1-<slug>.md | pending | — |

<!-- 版本状态：pending | in-progress | done。code-review：— / 进行中 / ✅全绿 -->

## 下一步

<一句话写清：从哪步、哪个子项接着干。例：继续 Step4，讨论粗 PRD 的定价策略部分。>
