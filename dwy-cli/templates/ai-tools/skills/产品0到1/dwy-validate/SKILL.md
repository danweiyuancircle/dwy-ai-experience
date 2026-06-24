---
name: dwy-validate
description: "【dwy·需求市场验证】产品 0 到 1 总闸门（闸1）。触发场景：用户说『验证需求 / 这需求是真的吗 / 有没有市场 / 需求验证 / 市场验证 / validate』，要在投入开发前确认需求真实存在且有市场时。这是总闸门，过不了流程直接停。"
---

## 职责（单一）
验证需求真实存在 + 有市场，给出 pass/fail 结论。**总闸门**：过不了流程直接停，不进后续。

## 输入（从哪读）
- state.json 的 `confirmed.idea`、`confirmed.competitors`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`竞品分析.md`

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__market-sizing.md`、`pm__sentiment-analysis.md`、`pm__interview-script.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-market-research/skills/market-sizing/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-market-research/skills/sentiment-analysis/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-product-discovery/skills/interview-script/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

验证方式三选一：
- 搜索量/竞品热度（AI 自动）
- 落地页测点击
- 5 个目标用户访谈

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/需求市场验证.md`
- 固定章节：验证方式 / 证据数据 / 市场判断 / **pass/fail 结论（含理由）**
- 回写 state.json：`confirmed.validation`（含 `pass` 布尔字段）
- **fail 时流程必须中断，不进闸2**
