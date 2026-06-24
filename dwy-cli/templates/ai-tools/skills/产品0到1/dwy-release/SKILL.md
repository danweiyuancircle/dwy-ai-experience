---
name: dwy-release
description: "【dwy·上架迭代】产品 0 到 1 上架迭代阶段（终点）。触发场景：用户说『上架 / 发布上线 / 出上架物料 / 配埋点 / 规划下一版 / release』，要准备上架物料、埋点指标并规划下一版迭代时。"
---

## 职责（单一）
产出上架物料 + 埋点指标设计 + 下一版迭代规划。

## 输入（从哪读）
- state.json 的 `confirmed.acceptance`、`confirmed.prd`、`confirmed.version_plan`
- `.dwy/prod/[项目]/04-上线交付/验收报告.md`
- `.dwy/prod/[项目]/02-需求规划/版本路线图.md`

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__release-notes.md`、`pm__gtm-strategy.md`、`pm__metrics-dashboard.md`、`pm__north-star-metric.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-execution/skills/release-notes/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-go-to-market/skills/gtm-strategy/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-product-discovery/skills/metrics-dashboard/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-marketing-growth/skills/north-star-metric/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/04-上线交付/上架物料.md`、`埋点与指标.md`、`下一版迭代规划.md`
- 固定章节：
  - 上架物料.md：发布说明 / GTM 策略 / 渠道文案
  - 埋点与指标.md：北极星指标 / 埋点清单 / 指标看板设计
  - 下一版迭代规划.md：数据反馈方向 / 下一版功能候选 / 优先级
- 回写 state.json：`confirmed.release`（上架物料就绪 + 下一版迭代方向）
