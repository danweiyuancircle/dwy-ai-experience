---
name: dwy-stage-design
description: "【dwy·设计架构阶段】产品 0 到 1 的第三阶段编排。触发场景：用户说『画原型 + 定架构 / 做设计 / 出原型出架构 / 需求定了开始设计 / 设计和技术架构一起搞』，要把 PRD 先展开成原型、原型定稿后再做技术架构时。可独立触发——需求已定，只想做设计架构，就触发我。"
---

## 职责（单一·编排层）
**串行**调度设计架构阶段，不掺产出内容：先原型（内部两轮门控），原型全部确认后才进架构。**架构依赖原型定稿**，原型未定不进架构。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- **先检 `schema_version`**：缺失或低于当前版本 → 按 `dwy-product-launcher/references/state-and-contract.md`「schema 版本与迁移」升级 state 再继续
- 上游 `confirmed.prd` / `confirmed.version_plan` 缺失（如单独触发本阶段）→ **不报错**，基于已聊上下文 + 现有产出**轻量补齐**够本阶段用的简版 PRD / 版本范围，写回对应 `confirmed.*` 标注「上下文补齐」。仅当上下文完全不足才提示用户补信息。
- `run_mode` 缺失 → 默认 `standard`，或按用户当下意图问一次。

## 编排（串行两步）
1. 调 **dwy-prototype** 走「线框初稿 → 高保真平面图」两轮门控；两轮分别回写 `confirmed.wireframe`、`confirmed.prototype`。
2. `confirmed.prototype` 写入后，才调 **dwy-architecture** 出技术架构。

子 skill 只向主窗口返回成果摘要，产出落各自文件。

## run_mode 感知
- `standard`：原型两轮门控照常问用户「线框是否通过 / 高保真是否通过」。
- `auto`：两轮门控由 AI 自动决策推进、不问用户，仍按「线框定稿 → 高保真 → 架构」顺序串。

## 自动流转（准出后）
- 回写 `current_stage = "dev"`，按 `run_mode`：`standard` 问「继续 TDD 开发 / 停」、`auto` 直接触发 `dwy-stage-dev`。

## 准出条件（硬约束）
- 设计与架构**均确认**：`confirmed.prototype` + `confirmed.architecture` 均写入
- 回写 `state.json`：`current_stage = "dev"`，按 run_mode 流转下一阶段
