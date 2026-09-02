---
name: dwy-tdd-dev
description: "【dwy·TDD开发】产品 0 到 1 开发阶段。触发场景：用户说『开始开发 / 写代码 / TDD 开发 / 按任务开发 / 实现功能 / tdd』，要按模块循环 RED→GREEN→REFACTOR 开发并自动推进时。单元测试归此阶段。"
---

## 职责（单一）
按模块循环 RED→GREEN→REFACTOR 开发，测试通过自动进下一模块（无人工逐模块验收）。单元测试归此阶段。

## 输入（从哪读）
- state.json 的 `confirmed.tasks`、`confirmed.architecture`、`confirmed.dev_progress`
- `.dwy/prod/[项目]/02-需求规划/开发任务拆解.md`
- `.dwy/prod/[项目]/04-架构设计/技术架构.md`、`数据库设计.md`、`接口契约.md`

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方法论产出，落到下方「产出契约」。
- **AI 自主开发**：架构阶段文档（`技术架构.md`/`数据库设计.md`/`接口契约.md`）+ `开发任务拆解.md` 已建好，AI 据此**自行**按模块循环 RED→GREEN→REFACTOR，测试通过自动进下一模块，不再逐点弹 `AskUserQuestion` 找用户拍板。仅当文档间出现**实质冲突或硬缺口**（无法据现有文档推断）时才向用户确认。
- 本 skill 依赖的外部 skill：`test-driven-development`、`systematic-debugging`（各对应 `~/.dwy/skills/<名>/`）
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy`，选「刷新全局外部 skill」（日常同步也会自检安装），不要自己用内置能力顶替。

每任务循环：RED 写失败测试 → GREEN 最小实现通过 → REFACTOR 重构。

**逐任务验收闭环（一任务一闭环，按序执行）**：每个任务 done 时——
1. **核验**：对照该任务在拆解时定的验证标准（精确命令 + 期望输出）跑通过；未过保持 `todo`，不得跳过
2. **标记**：`confirmed.dev_progress.<module>.<task> = done`
3. **记录**：`09-开发日志.md` 记一行（任务 / 验证结果 / 关键决策）
4. **独立提交**：该任务的源码 + 测试**单独 commit**（一任务一 commit，不攒一坨），message 带任务标识；多 agent 并发时各自在自己 worktree 内提交

**逐任务绿 = 必要不充分**：本闭环跑的是「该任务、在自己 worktree、领任务那一刻代码态」下的测试，并发时各 agent 互相看到的是中间失败态。它**不替代**合并后的全量收口——真实准出态只能由「全部分支合并后、统一工作树、一次性跑的全量单测 + 构建打包」定义，那道**合并后全量收口闸由编排层 `dwy-stage-dev` 独占执行**（见其第四步），承做 agent 不自行下「全量已绿」结论。

## 产出契约（硬约束）
- 落到：项目源码目录 + 各任务单元测试 + `.dwy/prod/[项目]/09-开发日志.md`
- 固定章节（开发日志）：任务进度 / 验证结果 / 关键决策 / 遇到的问题与解法
- 回写 state.json：`confirmed.dev_progress.<module>.<task> = todo|done`（逐任务维护）
