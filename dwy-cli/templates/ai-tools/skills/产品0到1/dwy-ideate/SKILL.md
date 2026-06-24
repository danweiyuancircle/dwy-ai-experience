---
name: dwy-ideate
description: "【dwy·想法收敛】产品 0 到 1 立项第一步。触发场景：用户说『我有个想法 / 帮我把这个点子理清楚 / 想做个 XX / 收敛想法 / 立项 / ideate』，要把模糊念头通过苏格拉底式反问发散+收敛成清晰可执行的产品想法时。"
---

## 职责（单一）
把用户模糊的初始念头，通过苏格拉底式反问发散+收敛，产出一份清晰的产品想法定义。

## 输入（从哪读）
- `state.json` 的 `confirmed.exploration` + `.dwy/prod/[项目]/01-立项/想法探索.md`（dwy-explore 已逼清的方向）
- 若未经 dwy-explore（用户直接触发本 skill 且想法已清晰）：用户口述的初始想法

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`brainstorming`（对应 `~/.dwy/skills/brainstorming/`）
- 若 `~/.dwy/skills/brainstorming/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/想法收敛.md`
- 固定章节：核心问题 / 目标用户 / 价值主张 / 关键假设 / 边界与不做什么
- 回写 state.json：`confirmed.idea`
