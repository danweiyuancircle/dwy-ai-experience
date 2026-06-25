---
name: dwy-stage-launch
description: "【dwy·立项阶段】产品 0 到 1 的第一阶段编排。触发场景：用户说『走立项流程 / 做立项 / 只想先把立项做完 / 验证这个想法值不值得做 / 想法收敛+竞品+需求验证+POC+MVP 一条龙』，要把模糊想法跑过三道闸门确认值不值得立项时。可独立触发——只想做立项不进后续，就触发我。"
---

## 职责（单一·编排层）
按序调度立项阶段的原子 skill，串起三道闸门，不掺产出内容。核心原则：**廉价验证在前、昂贵投入在后**。需求验证是总闸门，过不了不进任何后续重活。

## 前置校验（开工前读 state）
- 读 `.dwy/prod/[项目]/state.json`
- **先检 `schema_version`**：缺失或低于当前版本 → 按 `dwy-product-launcher/references/state-and-contract.md`「schema 版本与迁移」升级 state 再继续
- 立项是首阶段，无上游依赖；若 `state.json` 不存在则由本阶段初始化（写 `schema_version = "3"`）

## 编排顺序（带闸门）
1. **dwy-explore** — 想法探索收敛。用 YC forcing questions 逼清楚做什么、值不值，并收敛成结构化想法定义（产出 `想法收敛.md` + `confirmed.idea`）。想不清楚或明显不值 → 建议停下重想，不硬推；想清楚才进下一步
2. **dwy-competitor** — 竞品分析
3. **dwy-validate（闸 1·总闸门）** — 需求验证。**没人要即停整个流程**，不进任何后续
4. **dwy-poc（闸 2）** — 仅闸 1 过才做。技术可行性验证，**做不出即砍**
5. **dwy-mvp（闸 3）** — 仅闸 2 过才做。MVP 范围裁剪，**功能 ≤ 7 个**

> dwy-explore 与 dwy-validate 分工：explore 定性逼问给**方向**（做什么、给谁、最窄切入），validate 定量验证给**证据**（搜索量/竞品/访谈），不重复。

每道闸门未过 → 立即中断本阶段，回写 state 标记停止原因，不静默跳过。**硬闸门不受 run_mode 影响**：auto 下闸门未过同样停。

## run_mode 感知
- `dwy-explore` 末尾问得的 `run_mode` 决定本阶段内的非闸门门控：`standard` 照常问用户、`auto` 自动决策推进。
- 闸门（validate/poc/mvp）是硬约束，两种模式都按结果停或过。

## 自动流转（准出后）
- 三闸全过 + 立项确认 → 回写 `current_stage = "prd"`，按 `run_mode` 流转：`standard` 问「继续做需求版本 / 停」、`auto` 直接触发 `dwy-stage-prd`。

## 准出条件（硬约束）
- 三闸全过：`confirmed.validation` / `confirmed.poc` / `confirmed.mvp_features` 均写入
- 立项确认（standard 问用户；auto 自动判定，但闸门未过仍停）
- 回写 `state.json`：`current_stage = "prd"`，按 run_mode 流转下一阶段
