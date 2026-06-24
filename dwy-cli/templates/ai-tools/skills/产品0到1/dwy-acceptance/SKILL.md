---
name: dwy-acceptance
description: "【dwy·验收测试】产品 0 到 1 上架迭代阶段。触发场景：用户说『验收 / 验收测试 / 跑集成测试 / E2E 测试 / 上线前测试 / acceptance』，要在上架前做集成/E2E/兼容/合规验收并查文档与代码实际差距时。不重复单元测试。"
---

## 职责（单一）
集成/E2E/兼容/合规/沙盒验收 + 文档 vs 代码实际差距分析。**不重复单元测试**（单测归 dwy-tdd-dev）。

## 输入（从哪读）
- state.json 的 `confirmed.dev_progress`、`confirmed.prd`、`confirmed.architecture`
- 项目源码 + `.dwy/prod/[项目]/02-需求规划/PRD.md`
- `.dwy/prod/[项目]/03-设计与架构/接口契约.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`test-scenarios`、`intended-vs-implemented`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/04-上线交付/验收报告.md`
- 固定章节：集成/E2E 场景结果 / 兼容性 / 合规与沙盒 / 文档vs代码差距 / 验收结论
- 回写 state.json：`confirmed.acceptance`（验收结论 / 是否达上线标准）
