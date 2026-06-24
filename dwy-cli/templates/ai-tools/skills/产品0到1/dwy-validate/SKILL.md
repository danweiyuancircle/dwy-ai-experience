---
name: dwy-validate
description: "【dwy·需求市场验证】产品 0 到 1 总闸门（闸1）。触发场景：用户说『验证需求 / 这需求是真的吗 / 有没有市场 / 需求验证 / 市场验证 / validate』，要在投入开发前确认需求真实存在且有市场时。这是总闸门，过不了流程直接停。"
---

## 职责（单一）
验证需求真实存在 + 有市场，给出 pass/fail 结论。**总闸门**：过不了流程直接停，不进后续。

## 输入（从哪读）
- state.json 的 `confirmed.idea`、`confirmed.competitors`、`confirmed.exploration`（explore 已定性逼出的需求证据 Q1、现状替代 Q2——本 skill 把它变成定量验证）
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`竞品分析.md`、`想法探索.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`market-sizing`、`sentiment-analysis`、`interview-script`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

验证方式三选一：
- 搜索量/竞品热度（AI 自动）
- 落地页测点击
- 5 个目标用户访谈

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/需求市场验证.md`
- 固定章节：验证方式 / 证据数据 / 市场判断 / **pass/fail 结论（含理由）**
- 回写 state.json：`confirmed.validation`（含 `pass` 布尔字段）
- **fail 时流程必须中断，不进闸2**
