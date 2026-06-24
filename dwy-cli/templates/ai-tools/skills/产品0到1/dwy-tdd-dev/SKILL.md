---
name: dwy-tdd-dev
description: "【dwy·TDD开发】产品 0 到 1 开发阶段。触发场景：用户说『开始开发 / 写代码 / TDD 开发 / 按任务开发 / 实现功能 / tdd』，要按模块循环 RED→GREEN→REFACTOR 开发并自动推进时。单元测试归此阶段。"
---

## 职责（单一）
按模块循环 RED→GREEN→REFACTOR 开发，测试通过自动进下一模块（无人工逐模块验收）。单元测试归此阶段。

## 输入（从哪读）
- state.json 的 `confirmed.tasks`、`confirmed.architecture`、`confirmed.dev_progress`
- `.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- `.dwy/prod/[项目]/03-设计与架构/技术架构.md`、`数据库设计.md`、`接口契约.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`test-driven-development`、`systematic-debugging`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

每模块循环：RED 写失败测试 → GREEN 最小实现通过 → REFACTOR 重构。测试通过自动进下一模块。

## 产出契约（硬约束）
- 落到：项目源码目录 + 各模块单元测试 + `.dwy/prod/[项目]/09-开发日志.md`
- 固定章节（开发日志）：模块进度 / 关键决策 / 遇到的问题与解法
- 回写 state.json：`confirmed.dev_progress.<module> = todo|done`（逐模块维护）
