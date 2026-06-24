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
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__outcome-roadmap.md`、`pm__prioritize-features.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-execution/skills/outcome-roadmap/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-product-discovery/skills/prioritize-features/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/版本路线图.md`
- 固定章节：版本切片（V1.0/V1.x/V2.0…）/ 各版本目标 / V1.0 范围准出复查
- **V1.0 范围超出 MVP 清单直接告警，强制收敛**
- 回写 state.json：`confirmed.version_plan`
