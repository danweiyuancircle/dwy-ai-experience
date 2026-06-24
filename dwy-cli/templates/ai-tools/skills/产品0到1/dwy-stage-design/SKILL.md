---
name: dwy-stage-design
description: "【dwy·设计架构阶段】产品 0 到 1 的第三阶段编排。触发场景：用户说『画原型 + 定架构 / 做设计 / 出原型出架构 / 需求定了开始设计 / 设计和技术架构一起搞』，要把 PRD 同时展开成交互原型和技术架构时。可独立触发——需求已定，只想做设计架构，就触发我。"
---

## 职责（单一·编排层）
并行调度设计架构阶段的两条原子线，不掺产出内容。设计线与架构线互不依赖，**两线并行**。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 校验上游完整：`confirmed.prd` + `confirmed.version_plan` 必须存在
- 缺失 → 报错中断，提示先跑 dwy-stage-prd

## 编排（并行两线）
两条线无依赖，**用子 Agent 并发执行**（各自独立上下文）：
- **dwy-prototype** — 交互原型设计
- **dwy-architecture** — 技术架构设计

两个子 Agent 只向主窗口返回成果摘要，产出落各自文件。

## 准出条件（硬约束）
- 设计与架构**均确认**：`confirmed.prototype` + `confirmed.architecture` 均写入
- 回写 `state.json`：`current_stage = "dev"`
