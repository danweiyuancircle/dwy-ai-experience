---
name: dwy-stage-design
description: "【dwy·设计架构阶段】产品 0 到 1 的第三阶段编排。触发场景：用户说『画原型 + 定架构 / 做设计 / 出原型出架构 / 需求定了开始设计 / 设计和技术架构一起搞』，要把 PRD 先展开成原型、原型定稿后再做技术架构时。可独立触发——需求已定，只想做设计架构，就触发我。"
---

## 职责（单一·编排层）
**串行**调度设计架构阶段，不掺产出内容：先原型（内部两轮门控），原型全部确认后才进架构。**架构依赖原型定稿**，原型未定不进架构。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 校验上游完整：`confirmed.prd` + `confirmed.version_plan` 必须存在
- 缺失 → 报错中断，提示先跑 dwy-stage-prd

## 编排（串行两步）
1. 调 **dwy-prototype** 走「线框初稿 → 高保真平面图」两轮门控；两轮各自需用户讨论通过，分别回写 `confirmed.wireframe`、`confirmed.prototype`。
2. `confirmed.prototype` 写入后，才调 **dwy-architecture** 出技术架构。

子 skill 只向主窗口返回成果摘要，产出落各自文件。

## 准出条件（硬约束）
- 设计与架构**均确认**：`confirmed.prototype` + `confirmed.architecture` 均写入
- 回写 `state.json`：`current_stage = "dev"`
