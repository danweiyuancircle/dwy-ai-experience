---
name: dwy-stage-dev
description: "【dwy·TDD开发阶段】产品 0 到 1 的第四阶段编排。触发场景：用户说『开始开发 / 按 TDD 写代码 / 把 V1.0 开发出来 / 设计定了开始编码 / 多模块并发开发』，要按模块循环用 TDD 把当前版本所有模块做完时。可独立触发——设计架构已定，只想做开发，就触发我。"
---

## 职责（单一·编排层）
调度 TDD 开发原子 skill 按模块循环，不掺产出内容。版本内互不依赖的模块**多模块并发**。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 校验上游完整：`confirmed.prototype` + `confirmed.architecture` + `confirmed.tasks` 必须存在
- 缺失 → 报错中断，提示先跑 dwy-stage-design

## 编排（按模块循环 + 并发）
- 按 `confirmed.tasks` 的模块清单逐个调 **dwy-tdd-dev**
- 互不依赖的模块用多个子 Agent 并发；改同一批文件时各自独立 worktree 防冲突
- 有依赖的模块按依赖顺序串行

## 准出条件（硬约束）
- 当前版本（V1.0）**全模块测试通过**
- `confirmed.dev_progress` 写入（记录已完成模块与测试状态）
- 回写 `state.json`：`current_stage = "ship"`
