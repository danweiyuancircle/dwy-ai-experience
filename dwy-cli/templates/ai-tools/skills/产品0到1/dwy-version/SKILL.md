---
name: dwy-version
description: "【dwy·版本规划】产品 0 到 1 需求规划阶段。触发场景：用户说『版本规划 / 排版本 / 版本路线图 / V1 做啥 V2 做啥 / roadmap』，要把 PRD 需求按版本切片排路线图时。准出复查 V1.0 范围不膨胀。"
---

## 职责（单一）
把 PRD 需求按版本切片，排出版本路线图。准出复查 V1.0 范围没膨胀。

## 输入（从哪读）
- state.json 的 `confirmed.prd`、`confirmed.mvp_features`
- `.dwy/prod/[项目]/02-需求规划/PRD.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`outcome-roadmap`、`prioritize-features`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy`，选「刷新全局外部 skill」（日常同步也会自检安装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/版本路线图.md`
- 固定章节：版本切片（V1.0/V1.x/V2.0…）/ 各版本目标 / V1.0 范围准出复查
- **V1.0 范围超出 MVP 清单直接告警，强制收敛**
- 回写 state.json：`confirmed.version_plan`
