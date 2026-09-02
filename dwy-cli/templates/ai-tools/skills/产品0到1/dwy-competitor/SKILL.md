---
name: dwy-competitor
description: "【dwy·竞品分析】产品 0 到 1 立项阶段。触发场景：用户说『分析竞品 / 看看市面上有啥 / 竞品调研 / 对标分析 / 市场上谁在做 / competitor』，想知道已有玩家、市场规模和差异化切入点时。"
---

## 职责（单一）
盘点已有竞品 + 估算市场规模，找出差异化切入点。

## 输入（从哪读）
- state.json 的 `confirmed.idea`（含 explore 逼出的具体目标人 target_user、最窄切入 narrowest_wedge——差异化对着这个人定）
- `.dwy/prod/[项目]/01-立项/想法收敛.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`competitor-analysis`、`market-sizing`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy`，选「刷新全局外部 skill」（日常同步也会自检安装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/竞品分析.md`
- 固定章节：竞品清单 / 各竞品优劣 / 市场规模（TAM/SAM/SOM）/ 差异化切入点
- 回写 state.json：`confirmed.competitors`
