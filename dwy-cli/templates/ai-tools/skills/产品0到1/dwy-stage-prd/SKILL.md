---
name: dwy-stage-prd
description: "【dwy·需求版本阶段】产品 0 到 1 的第二阶段编排。触发场景：用户说『写 PRD / 出需求文档 / 做需求版本规划 / 拆版本拆任务 / 立项过了开始写需求』，要把已立项的 MVP 展开成 PRD、切版本、排开发顺序时。可独立触发——立项已在别处做完，只想做需求版本，就触发我。"
---

## 职责（单一·编排层）
按序调度需求版本阶段的原子 skill，不掺产出内容。把立项结论展开成可开发的需求与版本切分。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 校验上游完整：`confirmed.mvp_features` 必须存在（立项阶段三闸全过）
- 缺失 → 报错中断，提示先跑 dwy-stage-launch

## 编排顺序
1. **dwy-prd** — 写产品需求文档
2. **dwy-version** — 版本规划（V1.0 / V1.1 …路线图）
3. **dwy-tasks** — 任务拆分 + 开发顺序

## 准出条件（硬约束）
- 用户确认 PRD + V1.0 范围 + 开发顺序
- `confirmed.prd` / `confirmed.version_plan` / `confirmed.tasks` 均写入
- 回写 `state.json`：`current_stage = "design"`
