---
name: dwy-stage-prd
description: "【dwy·需求版本阶段】产品 0 到 1 的第二阶段编排。触发场景：用户说『写 PRD / 出需求文档 / 做需求版本规划 / 拆版本拆任务 / 立项过了开始写需求』，要把已立项的 MVP 展开成 PRD、切版本、排开发顺序时。可独立触发——立项已在别处做完，只想做需求版本，就触发我。"
---

## 职责（单一·编排层）
按序调度需求版本阶段的原子 skill，不掺产出内容。把立项结论展开成可开发的需求与版本切分。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 上游 `confirmed.mvp_features` 缺失（如单独触发本阶段）→ **不报错**，基于已聊上下文 + 现有产出**轻量补齐**一份够用的 MVP 范围，写回 `confirmed.mvp_features` 标注「上下文补齐」。
- **安全边界**：补的是 MVP 范围，**禁止**凭空标 `confirmed.validation`/`confirmed.poc` 的 `pass=true`——若想做真实立项验证，仍需跑 dwy-stage-launch。
- `run_mode` 缺失（没跑过 explore）→ 默认 `standard`，或按用户当下意图问一次。

## 编排顺序
1. **dwy-prd** — 写产品需求文档
2. **dwy-version** — 版本规划（V1.0 / V1.1 …路线图）
3. **dwy-tasks** — 任务拆分 + 开发顺序

## run_mode 感知
- `standard`：PRD / V1.0 范围 / 开发顺序照常问用户确认。
- `auto`：基于上下文自动决策，不问用户。

## 自动流转（准出后）
- 回写 `current_stage = "design"`，按 `run_mode`：`standard` 问「继续做设计架构 / 停」、`auto` 直接触发 `dwy-stage-design`。

## 准出条件（硬约束）
- PRD + V1.0 范围 + 开发顺序确认（standard 问用户 / auto 自动判定）
- `confirmed.prd` / `confirmed.version_plan` / `confirmed.tasks` 均写入
- 回写 `state.json`：`current_stage = "design"`，按 run_mode 流转下一阶段
