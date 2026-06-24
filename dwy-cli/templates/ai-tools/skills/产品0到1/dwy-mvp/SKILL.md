---
name: dwy-mvp
description: "【dwy·MVP定义】产品 0 到 1 立项阶段（闸3）。触发场景：用户说『定义 MVP / 最小可行产品 / 先做哪些功能 / 砍功能 / 第一版做什么 / mvp』，要从想法收敛出第一版必须做的核心功能清单时。MVP 功能硬上限 ≤7 个。"
---

## 职责（单一）
从想法+验证结果，收敛出第一版 MVP 功能清单。**功能硬上限 ≤7 个**，超出的进后续版本。

## 输入（从哪读）
- state.json 的 `confirmed.idea`、`confirmed.validation`、`confirmed.poc`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`需求市场验证.md`、`技术验证.md`

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/pm__prioritize-features.md`、`pm__opportunity-solution-tree.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉以下链接 → 写入缓存目录 + 更新 manifest.json → 执行
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-product-discovery/skills/prioritize-features/SKILL.md`
   - `https://raw.githubusercontent.com/phuryn/pm-skills/v2.0.0/pm-product-discovery/skills/opportunity-solution-tree/SKILL.md`
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/MVP清单.md`
- 固定章节：MVP 功能清单（≤7 个）/ 优先级排序 / 砍到后续版本的功能
- **功能数超 7 个直接拒绝，强制收敛**
- 回写 state.json：`confirmed.mvp_features`
