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
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__create-prd.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉 `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-execution/skills/create-prd/SKILL.md` → 写入缓存目录 + 更新 manifest.json → 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/PRD.md`
- 固定章节：背景与目标 / 用户场景 / 功能需求（逐条）/ 非功能需求 / 验收标准
- 回写 state.json：`confirmed.prd`
