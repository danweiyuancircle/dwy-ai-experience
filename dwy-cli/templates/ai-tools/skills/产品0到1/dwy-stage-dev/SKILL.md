---
name: dwy-stage-dev
description: "【dwy·TDD开发阶段】产品 0 到 1 的第四阶段编排。触发场景：用户说『开始开发 / 按 TDD 写代码 / 把 V1.0 开发出来 / 设计定了开始编码 / 多模块并发开发』，要按模块循环用 TDD 把当前版本所有模块做完时。可独立触发——设计架构已定，只想做开发，就触发我。"
---

## 职责（单一·编排层）
**任务级 block 分析 + 动态调度**，不掺产出内容。读任务依赖图，无 block 的任务多 Agent 并发、有 block 的串行，逐任务验收推进。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 上游 `confirmed.prototype` / `confirmed.architecture` / `confirmed.tasks` 缺失（如单独触发本阶段）→ **不报错**，基于已聊上下文 + 现有产出**轻量补齐**够本阶段用的架构/任务拆解结论，写回对应 `confirmed.*` 标注「上下文补齐」。仅当上下文完全不足才提示用户补信息。
- `run_mode` 缺失 → 默认 `standard`，或按用户当下意图问一次。
- `auto` 下开发全程自动跑（block 分析 → agent 池 → 逐任务验收 → 覆盖回查）；`standard` 同样自动跑（开发阶段本就无逐模块人工验收），区别仅在准出后是否问「继续上架」。

## 编排（block 分析 → agent 池调度）

### 第一步·block 分析（硬约束，先做）
调度前**必须先分析每个任务的前后 block 关系**（由任务 Interfaces 推出：`Consumes`=被谁 block、`Produces`=block 谁）。判定铁律：
- **无 block 的任务 → 多 Agent 并行**
- **有 block 的任务 → 串行**，被 block 的下游必须等其所有前置 block 任务 done 才能启动
- 与 `ai-tools/CLAUDE.md`「任务执行前必须先分析 block；无 block 的任务用多 Agent 并行」一致

### 第二步·agent 池调度
- 按 block 分析结果建 **ready 队列**（所有前置 block 已 done 的任务，即当前无 block 的）
- 多个子 Agent 并发领取 ready 队列任务，每个 agent 调 **dwy-tdd-dev** 跑单任务 RED→GREEN→REFACTOR
- 任务 done → 解锁被它 block 的下游 → 下游 block 全清进 ready → 空闲 agent 继续领；任务多时吞吐高
- **冲突隔离**：改同一批文件的并行任务各自独立 git worktree，完成后按 block 顺序合并；无文件交叠的并行任务无需隔离
- 落地用 Claude Code 原生 Agent 工具并发派发 + worktree

### 第三步·逐任务验收闭环（防漏需求）
- 每个任务 done 时，承做 agent 走闭环：**核验**（对照验证标准跑通，未过保持 `todo` 不跳过）→ **标记** `confirmed.dev_progress.<module>.<task> = done` → **记日志**（`09-开发日志.md` 一行：任务/验证结果/关键决策）→ **独立提交**（该任务源码+测试单独 commit，一任务一 commit，并发时各自在 worktree 内提交）
- worktree 内提交后，编排层按 block 顺序合并各任务分支

### 第四步·收尾覆盖回查
- 全部任务 done 后，对照 `开发任务拆解.md` 任务清单 + PRD 页面/功能逐项点检，确认无遗漏任务、无「标 done 实则未实现」
- 发现缺口 → 补任务再跑，不直接进 ship

## 自动流转（准出后）
- 回写 `current_stage = "ship"`，按 `run_mode`：`standard` 问「继续上架迭代 / 停」、`auto` 直接触发 `dwy-stage-ship`。

## 准出条件（硬约束）
- 当前版本（V1.0）**全任务测试通过** + 覆盖回查无遗漏
- `confirmed.dev_progress` 全 done（任务级记录 `<module>.<task>`）
- 回写 `state.json`：`current_stage = "ship"`，按 run_mode 流转下一阶段
