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
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方法论产出，落到下方「产出契约」。
- **AI 自主拆解**：架构阶段文档（`技术架构.md`/`数据库设计.md`/`接口契约.md` + `PRD.md`/`版本路线图.md`）已建好，AI 据此**自行判断**模块怎么切、方案怎么选，按 writing-plans 方法论直接产出，不再逐点弹 `AskUserQuestion` 找用户拍板。仅当文档间出现**实质冲突或硬缺口**（无法据现有文档推断）时才向用户确认。
- 本 skill 依赖的外部 skill：`writing-plans`（对应 `~/.dwy/skills/writing-plans/`）
- 若 `~/.dwy/skills/writing-plans/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- 固定章节：
  - **模块划分**：按业务域/Features 内聚分模块
  - **任务清单（拆到 TDD 步）**：每个任务带
    - `Files`：精确文件路径（Create / Modify / Test）
    - `Interfaces`：`Consumes`（用前序任务的精确签名）+ `Produces`（后续任务依赖的函数名/参数/返回类型）——任务依赖图的数据来源
    - `Steps`：2-5 分钟一步的 RED→GREEN→REFACTOR（写失败测试 → 跑挂 → 最小实现 → 跑过 → commit），每步含**真实内容**
    - 一个**可独立测试的交付物** + 验证标准（精确命令 + 期望输出）
    - **No Placeholders**：禁 TBD / 「加校验」「处理边界」这类空泛，禁引用任何任务都没定义的类型/函数
  - **任务依赖图**：由各任务 Interfaces 的 Consumes/Produces 推出（到任务级，不只模块级）
- 任务粒度 = 「能带自己测试周期、值得新 reviewer 独立卡验收的最小单元」；setup/配置/脚手架折叠进它服务的任务，不单列
- 回写 state.json：`confirmed.tasks`
