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
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- 本 skill 依赖的外部 skill：`writing-plans`（对应 `~/.dwy/skills/writing-plans/`）
- 若 `~/.dwy/skills/writing-plans/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- 固定章节：模块划分 / 每模块任务清单（含验证标准）/ 依赖顺序
- 回写 state.json：`confirmed.tasks`
