---
name: dwy-product-launcher
description: "【dwy·全流程总控】从模糊想法到上线产品的唯一入口。触发场景：用户说『我想做个产品 / 从 0 到 1 把这个做出来 / 走完整流程 / 帮我把想法变成产品 / 一条龙做产品 / product launcher』，要把一个模糊念头一路串到上线、并管理多版本迭代时。只想做其中某一阶段，请直接触发对应 dwy-stage-* 阶段 skill。"
---

## 职责（总控·编排层）
从模糊想法到产品的唯一入口。按顺序串 5 个阶段 skill，维护 state.json（进度 + 已确认结论），并做多版本子 Agent 编排。**不掺产出内容**，产出由阶段内原子 skill 落地。

## 五阶段串行
按序调度，每阶段准出后才进下一阶段（阶段 skill 各自做前置校验 + 准出回写）：
1. **dwy-stage-launch** — 立项（三闸门：需求验证 → POC → MVP）
2. **dwy-stage-prd** — 需求版本
3. **dwy-stage-design** — 设计架构
4. **dwy-stage-dev** — TDD 开发
5. **dwy-stage-ship** — 上架迭代

进度以 `state.json` 的 `current_stage` 为准；可从任意阶段断点续跑。

## 首次初始化
新项目首次进入时，按 `references/state-and-contract.md` 落地：建 `.dwy/prod/[项目]/` 目录树、初始化 `state.json`、在项目 `.gitignore` 加 `.dwy/prod/.cache/`（**只忽略缓存，产品文档入库**）。目录结构、state schema、各 skill 的 `confirmed.*` 字段契约、缓存 manifest 格式全部以该参考文件为准。

## state.json（进度 + 结论）
落 `.dwy/prod/[项目]/state.json`，含：
- `current_stage` — 当前阶段
- `current_version` — 当前版本（如 `V1.0`）
- `confirmed.*` — 各原子的已确认结论引用（idea / competitors / validation / poc / mvp_features / prd / version_plan / tasks / prototype / architecture / dev_progress / acceptance / release）
- `versions` — 各版本状态（路线图 + 完成情况）

## 多版本编排逻辑

### 版本间：串行
- V1.1 依赖 V1.0，版本一个接一个做
- **每个版本起独立子 Agent**（独立上下文窗口），读版本路线图 + 上一版代码
- 产出写回 `.dwy/prod/` 和源码，**只向主窗口返回成果摘要**（不返回全量代码，省上下文）

### 版本内：多模块并发
- 互不依赖的模块用多个子 Agent **并发**
- 改同一批文件时各自独立 **worktree**，避免互相覆盖

## 准出条件（硬约束）
- 全部规划版本上线完成
- `state.json` 各版本标记完成，`confirmed.*` 齐全
