---
name: dwy-stage-ship
description: "【dwy·上架迭代阶段】产品 0 到 1 的第五阶段编排。触发场景：用户说『验收上线 / 发版上架 / 开始迭代 / 代码写完了走验收发布 / 确定下个版本方向』，要把已开发完的版本走完验收+发布并定迭代方向时。可独立触发——开发已完成，只想做验收上线，就触发我。"
---

## 职责（单一·编排层）
按序调度上架迭代阶段的原子 skill，不掺产出内容。验收把关 → 发布上线 → 收口迭代方向。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 校验上游完整：`confirmed.dev_progress` 必须存在（当前版本全模块测试通过）
- 缺失 → 报错中断，提示先跑 dwy-stage-dev

## 编排顺序
1. **dwy-acceptance** — 验收（对照 PRD 与验收标准把关）
2. **dwy-release** — 发布上线

## 准出条件（硬约束）
- 上线完成 + 用户确认下一版迭代方向
- `confirmed.acceptance` / `confirmed.release` 均写入
- 回写 `state.json`：当前版本标记完成；若有下一版本，`current_stage` 复位到 `prd` 进入下一轮版本编排
