---
name: dwy-stage-ship
description: "【dwy·上架迭代阶段】产品 0 到 1 的第五阶段编排。触发场景：用户说『验收上线 / 发版上架 / 开始迭代 / 代码写完了走验收发布 / 确定下个版本方向』，要把已开发完的版本走完验收+发布并定迭代方向时。可独立触发——开发已完成，只想做验收上线，就触发我。"
---

## 职责（单一·编排层）
按序调度上架迭代阶段的原子 skill，不掺产出内容。验收把关 → 发布上线 → 收口迭代方向。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- 上游 `confirmed.dev_progress` 缺失（如单独触发本阶段）→ **不报错**，基于已聊上下文 + 现有源码/产出**轻量补齐**够本阶段用的开发完成结论，写回 `confirmed.dev_progress` 标注「上下文补齐」。仅当上下文完全不足才提示用户补信息。
- `run_mode` 缺失 → 默认 `standard`，或按用户当下意图问一次。

## 编排顺序
1. **dwy-acceptance** — 验收（对照 PRD 与验收标准把关）
2. **dwy-release** — 发布上线

## run_mode 感知
- `standard`：验收结论、迭代方向照常问用户。
- `auto`：验收自动判定；但**发布上线是高风险不可逆操作 → 仍停下让用户确认**（auto 不绕高风险不可逆动作），确认后再 release。

## 自动流转（准出后）
- 当前版本标记完成。若有下一版本，回写 `current_stage = "prd"` 进入下一轮版本编排：`standard` 问「继续做下一版 / 停」、`auto` 直接触发 `dwy-stage-prd`（下一版本无高风险闸门时连跑）。
- 无下一版本 → 流程正常结束（ship 是末阶段）。

## 准出条件（硬约束）
- 上线完成（release 前的高风险确认两种模式都做）+ 下一版迭代方向已定
- `confirmed.acceptance` / `confirmed.release` 均写入
- 回写 `state.json`：当前版本标记完成；若有下一版本，`current_stage` 复位到 `prd`，按 run_mode 流转
