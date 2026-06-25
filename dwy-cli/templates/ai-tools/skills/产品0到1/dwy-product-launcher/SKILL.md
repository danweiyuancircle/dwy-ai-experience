---
name: dwy-product-launcher
description: "【dwy·全流程总控】从模糊想法到上线产品的唯一入口。触发场景：用户说『我想做个产品 / 从 0 到 1 把这个做出来 / 走完整流程 / 帮我把想法变成产品 / 一条龙做产品 / product launcher』，要把一个模糊念头逐步推进时。**渐进式：从立项第一步直接开始，每阶段完成后问继不继续，不预设终点、用户随时可停。** 只想做其中某一阶段，也可直接触发对应 dwy-stage-* 阶段 skill。"
---

## 职责（总控·编排层）
从模糊想法到产品的唯一入口。按顺序串 5 个阶段 skill，维护 state.json（进度 + 已确认结论），并做多版本子 Agent 编排。**不掺产出内容**，产出由阶段内原子 skill 落地。

## 渐进式推进（核心交互，读 run_mode）
**不在入口预问"走到哪个阶段"。** 直接从立项第一步开始往下走。`dwy-explore` 在 idea 收敛后会问一次 `run_mode`（standard/auto），之后推进节奏读它：
- **standard**：每个阶段准出后问一句「继续下一步 / 到此为止」，用户当场决定。终点不预设、随时可喊停。
- **auto**：阶段间不问，自动连跑到底、最后出结果；**仅硬闸门未过才停**（立项的 validate/poc、高风险不可逆操作）。

```
开始 → dwy-stage-launch（立项·三闸门）
     → 阶段完成，问：继续做需求版本？ → 用户选 继续 / 停
继续 → dwy-stage-prd（需求版本）
     → 阶段完成，问：继续做设计架构？ → 继续 / 停
继续 → dwy-stage-design（设计架构）
     → 问：继续 TDD 开发？ → 继续 / 停
继续 → dwy-stage-dev（TDD 开发）
     → 问：继续上架迭代？ → 继续 / 停
继续 → dwy-stage-ship（上架迭代）→ 完
```

规则：
- **从第一步直接开始**，不让用户提前选终点
- standard 下每阶段准出后**只问"继不继续"**，不问"要走到哪"；auto 下不问、直接流转
- 闸门内（立项的需求验证/POC）若没过，**无论 standard/auto 都自动停**在当前阶段，不往下走
- 用户喊停时，已完成阶段的产出和 state.json 都已落盘，下次可断点续跑

按序的五阶段：
1. **dwy-stage-launch** — 立项（三闸门：需求验证 → POC → MVP）
2. **dwy-stage-prd** — 需求版本
3. **dwy-stage-design** — 设计架构
4. **dwy-stage-dev** — TDD 开发
5. **dwy-stage-ship** — 上架迭代

进度以 `state.json` 的 `current_stage` 为准；可从任意阶段断点续跑。

## 读 state 先检 schema 版本（老项目升级入口）
读到**已存在**的 `state.json` 时，**先检 `schema_version`**：缺失或低于当前（`"2"`）→ 按 `references/state-and-contract.md`「七、schema 版本与迁移」执行迁移，迁移后再续跑。这是老用户旧 state 无感升级的入口。

## 首次初始化（只建根，不建阶段目录）
新项目首次进入时，**只**做两件最小事：
- 建项目根目录 `.dwy/prod/[项目]/`（不建 01~04 任何阶段子目录）
- 初始化 `state.json`（写 `schema_version = "2"`）

产品产出 `.dwy/prod/[项目]/` 入库，无需改 `.gitignore`（外部 skill 在全局 `~/.dwy/skills/`，不落项目）。若包装型原子 skill 触发时 `~/.dwy/skills/<name>/` 不存在，提示用户先跑 `dwy skills install`。

**阶段目录渐进式按需建**：`01-立项/` 进立项时才建，`02-需求规划/` 进需求阶段才建……不要一次把四个阶段目录全建出来（那不是渐进式）。state schema、各 skill 的 `confirmed.*` 字段契约、外部 skill 全局安装见 `references/state-and-contract.md`。

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
