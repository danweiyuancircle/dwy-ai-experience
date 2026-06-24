---
name: dwy-ideate
description: "【dwy·想法收敛】产品 0 到 1 立项第一步。触发场景：用户说『我有个想法 / 帮我把这个点子理清楚 / 想做个 XX / 收敛想法 / 立项 / ideate』，要把模糊念头通过苏格拉底式反问发散+收敛成清晰可执行的产品想法时。"
---

## 职责（单一）
把用户模糊的初始念头，通过苏格拉底式反问发散+收敛，产出一份清晰的产品想法定义。

## 输入（从哪读）
- 用户口述的初始想法（首个原子，无上游产出）

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/sp__brainstorming.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉 `https://raw.githubusercontent.com/obra/superpowers/v6.0.3/skills/brainstorming/SKILL.md` → 写入缓存目录 + 更新 manifest.json → 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/想法收敛.md`
- 固定章节：核心问题 / 目标用户 / 价值主张 / 关键假设 / 边界与不做什么
- 回写 state.json：`confirmed.idea`
