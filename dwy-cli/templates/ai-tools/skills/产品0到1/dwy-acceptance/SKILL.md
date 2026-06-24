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
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__test-scenarios.md`、`pm__intended-vs-implemented.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-execution/skills/test-scenarios/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-ai-shipping/skills/intended-vs-implemented/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/04-上线交付/验收报告.md`
- 固定章节：集成/E2E 场景结果 / 兼容性 / 合规与沙盒 / 文档vs代码差距 / 验收结论
- 回写 state.json：`confirmed.acceptance`（验收结论 / 是否达上线标准）
