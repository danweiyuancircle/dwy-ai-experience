---
name: dwy-competitor
description: "【dwy·竞品分析】产品 0 到 1 立项阶段。触发场景：用户说『分析竞品 / 看看市面上有啥 / 竞品调研 / 对标分析 / 市场上谁在做 / competitor』，想知道已有玩家、市场规模和差异化切入点时。"
---

## 职责（单一）
盘点已有竞品 + 估算市场规模，找出差异化切入点。

## 输入（从哪读）
- state.json 的 `confirmed.idea`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- 本 skill 依赖的外部 skill：`competitor-analysis`、`market-sizing`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/竞品分析.md`
- 固定章节：竞品清单 / 各竞品优劣 / 市场规模（TAM/SAM/SOM）/ 差异化切入点
- 回写 state.json：`confirmed.competitors`
