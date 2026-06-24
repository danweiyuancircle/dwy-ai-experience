---
name: dwy-prd
description: "【dwy·PRD生成】产品 0 到 1 需求规划阶段。触发场景：用户说『写 PRD / 出需求文档 / 产品需求文档 / prd』，要把 MVP 清单细化成可开发的产品需求文档时。"
---

## 职责（单一）
把 MVP 功能清单细化成完整可开发的 PRD。

## 输入（从哪读）
- state.json 的 `confirmed.mvp_features`、`confirmed.idea`
- `.dwy/prod/[项目]/01-立项/MVP清单.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- 本 skill 依赖的外部 skill：`create-prd`（对应 `~/.dwy/skills/create-prd/`）
- 若 `~/.dwy/skills/create-prd/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/PRD.md`
- 固定章节：背景与目标 / 用户场景 / 功能需求（逐条）/ 非功能需求 / 验收标准
- 回写 state.json：`confirmed.prd`
