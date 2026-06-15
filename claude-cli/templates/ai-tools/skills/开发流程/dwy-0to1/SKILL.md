---
name: dwy-0to1
description: 端到端「0→1 产品孵化」编排器。用户丢一个产品想法进来，按九步带门流水线**逐步编排调用**同系列单点 skill：dwy-market-analysis（需求/市场）→ dwy-tech-feasibility（技术可行性）→（可选）dwy-spike（真机实测）→ dwy-prd-coarse（粗 PRD）→ dwy-prototype（低保真+高保真原型）→ dwy-prd-detailed（细 PRD）→ dwy-version-plan（版本规划）→ dwy-tdd-dev（逐版本 TDD 开发），每步卡用户确认门、产物落盘 docs/0to1/、用 STATE.md 做唯一真相源支持断点续传。涉及以下场景**必须**使用此 skill（即使用户没点名 'dwy-0to1'）：用户说『我想做个 X』『帮我把这个想法做成产品』『从 0 到 1 做个 XX』『帮我孵化这个想法』，或丢一个产品概念让我判断值不值得做、怎么落地；用户说『继续做 X』『接着上次的产品』『孵化进度到哪了』时读 STATE 续传/汇报。只想单独做其中一步（只画原型、只写 PRD、只做市场分析等），直接用对应的 dwy-* 单点 skill，不必走整条流水线。核心纪律——每步卡门等用户确认才进下一步，绝不跳步、绝不未确认就写代码，所有产物落盘 docs/0to1/ 以支持断点续传。
---

# dwy-0to1（编排器）

把一个产品想法，按九步带门的流水线推到逐版本 TDD 开发落地。本 skill 是**编排器**：自己不实现各步细节，而是按顺序**委托调用**同系列单点 skill，并独占 STATE 真相源、统一卡门、管跨步顺序。每步落盘 `docs/0to1/`，可中断、可断点续传——这次聊到粗 PRD，下次进来从粗 PRD 接着聊。

**核心纪律**：每步有明确产物、卡用户确认门、落盘。门没过不许进下一步，更不许提前写代码。

> 单点能力可独立使用：用户只想画个原型 / 写个 PRD / 做个市场分析，直接用对应的 `dwy-*` skill 即可，不必走整条流水线。本编排器只在「完整 0→1 / 继续上次孵化」时启用。

## 第一件事：读 STATE，决定从哪开始（断点续传）

**每次进入本 skill，先做这步，不要直接开干。**

1. `Glob docs/0to1/STATE.md`（相对当前项目根）。
2. **存在** → Read 它，看 `current_step` 和「进度」表、「下一步」：
   - 用 `AskUserQuestion` 跟用户确认：「上次做到 Step N（名称），下一步是 X。从这接着 / 改某步 / 整个重开？」
   - 按用户选择定位到对应步骤。
3. **不存在** → 这是新想法：
   - 先 `Read templates/STATE.md`，在 `docs/0to1/STATE.md` 建初始 STATE（用 `date +%Y-%m-%d` 取今天填 created/updated，current_step=1）。
   - `docs/0to1/` 目录不存在就先建。
   - 从 Step 1 开始。

> STATE.md 是整条流水线的**唯一真相源**。任何一步的状态、决策、产物路径都以它为准。它丢了，可以靠各产物文件名（`01-market.md`…编号即步号）+ frontmatter 重建。

## 门规则（每步通用，强制）

每一步都按「**委托 → 过门 → 记账**」走，缺一不可：

1. **委托调用单点 skill**：用 Skill 工具调对应 `dwy-*`，在调用指令里带「**流水线模式**」+ 前序产物路径 + 落盘路径（见路由表）。被调 skill 负责本步的工作、完成前自检（先验证再声称）、并**自己跑领域门**（`AskUserQuestion` 把产物摆给用户问 通过/改/换方向）。
2. **过门**：被调 skill 的门**用户点头**了，这步才算过。用户要改 → 让 skill 迭代重做再摆，**没点头不进下一步、更不许写生产代码**。
3. **记账（编排器独占）**：门过了，**编排器立刻更新 `docs/0to1/STATE.md`**——这步状态改 `done`、gate 列填 `✅ <date>`、产物路径、按 `templates/STATE.md`「关键决策」清单填本步定下的决策（Step1 真需求结论/差异化/核心能力/硬约束、Step2 技术方案、Step3 是否实测/端、Step4 定位/定价、Step8 选定版本/全局架构骨架）、`current_step` 指向下一步、写一句「下一步」。被调 skill **不碰 STATE**，记账只由编排器做，这是一次原子 checkpoint。

红线：**绝不跳步、绝不跳门、绝不在用户确认前写生产代码。**

## 九步流水线（路由）

每步：**委托调用下表的 skill（流水线模式，给前序产物路径 + 落盘路径）→ 过门 → 编排器更新 STATE**。

| # | 步骤 | 委托调用 | 流水线 args（前序 → 落盘） | 产物 |
|---|------|---------|--------------------------|------|
| 1 | 需求 & 市场分析 | `dwy-market-analysis` | 无前序 → `docs/0to1/01-market.md` | 01-market.md |
| 2 | 技术可行性 | `dwy-tech-feasibility` | 读 `01-market.md` → `docs/0to1/02-tech-feasibility.md` | 02-tech-feasibility.md |
| 3 | 实测（可选） | `dwy-spike` | 读 `02-tech-feasibility.md` → 代码 `docs/0to1/spike/`、结论 `docs/0to1/03-spike-result.md` | 03-spike-result.md + spike/ |
| 4 | 粗 PRD | `dwy-prd-coarse` | 读 `01-market.md` + `02-tech-feasibility.md`（+ 存在时 `03-spike-result.md`） → `docs/0to1/04-prd-coarse.md` | 04-prd-coarse.md |
| 5 | 低保真原型 | `dwy-prototype`（`phase=lowfi`） | 读 `04-prd-coarse.md` → `docs/0to1/prototype-lowfi/` | prototype-lowfi/index.html |
| 6 | 高保真原型 | `dwy-prototype`（`phase=hifi`） | 读 `04-prd-coarse.md` + `prototype-lowfi/` → `docs/0to1/prototype-hifi/` | prototype-hifi/ |
| 7 | 细 PRD | `dwy-prd-detailed` | 读 `04-prd-coarse.md` + `prototype-hifi/` → `docs/0to1/05-prd-detailed.md` | 05-prd-detailed.md |
| 8 | 版本规划 | `dwy-version-plan` | 读 `05-prd-detailed.md` → `docs/0to1/06-version-plan.md` | 06-version-plan.md |
| 9 | 逐版本 TDD 开发 | `dwy-tdd-dev` | 读 `06-version-plan.md` + `05-prd-detailed.md` + STATE 选定版本 → 实施计划 `docs/0to1/plans/vN-<slug>.md`，代码进项目源码 | plans/ + 代码 |

**Step 3 分支（编排器据 STATE 决策路由）**：
- Step 2 过门时记的「是否实测」= **否** → Step 3 不调 `dwy-spike`，进度表标 `skipped(无需实测)`，`current_step` 直接到 4。
- = **是** → 调 `dwy-spike`；它会先问做哪一端，编排器把答案记进 STATE 的 `target_platform`（Step 5/6/9 都按这个端走）。实测不通过 → `current_step` 回 2 重选方案。

**Step 5/6 同一个 skill 两道门**：`dwy-prototype` 在低保真（`phase=lowfi`）、高保真（`phase=hifi`）各调一次、各卡一道门，目的不同（验流程 vs 做底稿），别合并。

**Step 9 循环**：对 STATE「选定版本」里的每个版本依次调 `dwy-tdd-dev` 走完，编排器更新「版本开发进度」表；全部版本完，Step 9 标 `done`，给交付报告。每版完成的 commit 由 `dwy-tdd-dev` 按 Git 提交规范执行（敏感扫描 + 格式 + 禁 AI 署名），不裸 commit。

## 产物目录（项目内 docs/0to1/）

```
docs/0to1/
  STATE.md                    # 断点真相源（编排器独占读写）
  01-market.md                # Step1 需求/市场/竞品/差异化
  02-tech-feasibility.md      # Step2 方案对比 + 推荐
  03-spike-result.md          # Step3 实测结论（不是代码）
  spike/                      # Step3 丢弃式 POC（仅需实测时）
  04-prd-coarse.md            # Step4 粗 PRD
  prototype-lowfi/index.html  # Step5 低保真原型
  prototype-hifi/             # Step6 高保真原型（按端套壳）
  05-prd-detailed.md          # Step7 细 PRD（页面级）
  06-version-plan.md          # Step8 版本规划
  plans/
    v1-<slug>.md              # Step9 每版本一份实施计划
```

各产物文件 frontmatter 由对应 skill 写（`status` / `updated`）；STATE 丢失时靠文件名编号 + frontmatter 重建。

## 关键边界 / 禁止

- **编排器只编排、不实现**：各步的「怎么做」在对应 `dwy-*` skill 里，本文件只管顺序、门、STATE。被调 skill 不碰 STATE，记账只由编排器做。
- **spike 是丢弃式**（Step 3）：实测代码隔离在 `docs/0to1/spike/`，只为验证核心流程跑不跑得通。开发期（Step 9）**只继承结论，不继承 spike 代码**——TDD 铁律是没失败测试不写生产代码，spike 不算。
- **两个原型卡不同门**：低保真（Step 5）验流程方向、高保真（Step 6）做细 PRD 底稿，目的不同别合并。**例外**：单页小工具可合并成一轮；CLI / 后端 / 库类**无 GUI** 产品，原型步**优先降级**为「终端会话 mock / API 契约示例」——产出了降级产物就在 STATE 标 `done(降级:无GUI)`；**只有连 mock/契约都没意义时才直接跳过**（标 `skipped(无GUI)`）。详见 `dwy-prototype` 的降级表。
- **自包含 + 可增强**：本编排器只依赖同系列 `dwy-*` skill，不依赖 gstack / superpowers 插件。Step 9 的 `dwy-tdd-dev` 已内置 spec/code 双审 + 版本级 code-review，等价覆盖 `dwy-dev-qa` 核心；需要更全面的系统级 QA 时才额外委托 `dwy-dev-qa` 或 `/code-review`，避免重复审查。
- **流水线边界**：交付止于「可运行代码 + 交付报告」。**上线 / 部署 / 市场验证是流水线边界外的人工动作**——Step1「真需求结论」的真正验证靠上线后人工度量。要再迭代就重进本 skill：方向变回 Step 1、产品调整回 Step 4、只加版本回 Step 8。
- **不跳步、不跳门、不提前写代码**（见「门规则」）。

## 文件结构

```
.claude/skills/dwy-0to1/
├── SKILL.md                       ← 本文件（编排骨架 + STATE 协议 + 门规则 + 路由）
└── templates/
    └── STATE.md                   ← 状态文件模板（编排器独占）
```

九步的执行细则与产物模板已拆到同级独立 skill，可单独触发，也被本编排器按路由表委托调用：

```
开发流程/
├── dwy-market-analysis/           ← Step1 需求/市场分析
├── dwy-tech-feasibility/          ← Step2 技术选型可行性
├── dwy-spike/                     ← Step3 丢弃式实测
├── dwy-prd-coarse/                ← Step4 粗 PRD（含 templates/prd-coarse.md）
├── dwy-prototype/                 ← Step5+6 低保真+高保真原型
├── dwy-prd-detailed/              ← Step7 细 PRD（含 templates/prd-detailed.md）
├── dwy-version-plan/              ← Step8 版本规划（含 templates/version-plan.md）
└── dwy-tdd-dev/                   ← Step9 逐版本 TDD 开发（含 templates/impl-plan.md）
```
