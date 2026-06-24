---
name: dwy-competitor
description: "【dwy·竞品分析】产品 0 到 1 立项阶段。触发场景：用户说『分析竞品 / 看看市面上有啥 / 竞品调研 / 对标分析 / 市场上谁在做 / competitor』，想知道已有玩家、市场规模和差异化切入点时。"
---

## 职责（单一）
盘点已有竞品 + 估算市场规模，找出差异化切入点。

## 输入（从哪读）
- state.json 的 `confirmed.idea`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__competitor-analysis.md`、`pm__market-sizing.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-market-research/skills/competitor-analysis/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-market-research/skills/market-sizing/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/竞品分析.md`
- 固定章节：竞品清单 / 各竞品优劣 / 市场规模（TAM/SAM/SOM）/ 差异化切入点
- 回写 state.json：`confirmed.competitors`
