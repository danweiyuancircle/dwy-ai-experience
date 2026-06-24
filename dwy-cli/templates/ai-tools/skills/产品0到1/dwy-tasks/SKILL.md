---
name: dwy-tasks
description: "【dwy·任务拆解】产品 0 到 1 需求规划阶段。触发场景：用户说『拆任务 / 拆解开发任务 / 排开发计划 / 写实施计划 / tasks』，要把 V1.0 版本范围拆成可执行的开发任务清单时。"
---

## 职责（单一）
把 V1.0 版本范围拆成可执行、可验证的开发任务清单。

## 输入（从哪读）
- state.json 的 `confirmed.version_plan`、`confirmed.prd`
- `.dwy/prod/[项目]/02-需求规划/版本路线图.md`、`PRD.md`

## 实现
[包装型]
1. 先读本地缓存 `.dwy/prod/.cache/skills/sp__writing-plans.md`
2. 命中 → 直接读取执行
3. 没命中 → WebFetch 拉 `https://raw.githubusercontent.com/obra/superpowers/v6.0.3/skills/writing-plans/SKILL.md` → 写入缓存目录 + 更新 manifest.json → 执行
4. **fetch 失败：直接报错中断，不降级、不用内置能力顶替**

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- 固定章节：模块划分 / 每模块任务清单（含验证标准）/ 依赖顺序
- 回写 state.json：`confirmed.tasks`
