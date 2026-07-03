---
name: dwy-commercial
description: "【dwy·商业分析】产品 0 到 1 立项阶段（闸1 之后）。触发场景：用户说『商业分析 / 商业模式 / 怎么赚钱 / 变现 / 定价 / 单位经济 / CAC/LTV / GTM 获客 / 商业可行性 / commercial』，要在需求验证后判断商业模式跑不跑得通、能不能赚钱时。startup（创业/产品）模式下是硬闸门：商业不可行即停流程；builder（练手/学习）模式跳过不挡流程。"
---

## 职责（单一）
盘商业模式 + 变现路径 + 定价 + 单位经济 + GTM 获客，给商业可行性 **pass/fail** 结论。**startup 模式硬闸门**：过不了流程停，不进闸 2（POC）。**builder 模式跳过**：读 `confirmed.idea.mode`，builder 直接回 skipped、不挡流程、不产出。

## 输入（从哪读）
- state.json 的 `confirmed.idea`（含 `mode` = startup/builder、`target_user`、`narrowest_wedge`、`value_prop`、`key_assumptions`——变现与定价对着这个人和这点切入定）
- state.json 的 `confirmed.competitors`（竞品定价、现有变现方式对着它定差异化）
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`竞品分析.md`、`需求市场验证.md`

## 模式分流（开工第一步）
读 `confirmed.idea.mode`：
- **builder**（练手 / 学习 / 开源 / hackathon / 纯兴趣）→ 不逼商业，回写 `confirmed.commercial = { mode: "builder", pass: true, skipped: true, reason: "builder 模式不评估商业可行性" }`，不产出文件、不挡流程，直接放行进闸 2
- **startup**（奔着有人用、可能收钱、要做成产品）→ 走下面完整商业分析

## 实现
[包装型] 用全局本地 skill（位于 `~/.dwy/skills/<外部skill名>/`）：
读其 `SKILL.md`（及同目录 scripts/、配套 .md），按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill（各对应 `~/.dwy/skills/<名>/`）：
  - `startup-canvas` — 整体盘点（战略 9 节 + 商业模式 2 节），作为引子框架，先跑它把商业全貌摸一遍
  - `business-model` — 商业模式画布 9 模块（详细展开成本结构 / 收入流）
  - `monetization-strategy` — 3-5 个变现方案（含 CAC/LTV/回本/毛利单位经济 + 低成本验证实验）
  - `pricing-strategy` — 定价模型选型 + 分层 + 价值计量 + 价格敏感度
  - `porters-five-forces` — 赛道竞争结构（补「赛道」维度，判断利润空间是否被结构压扁）
  - `gtm-strategy` — 首批用户从哪来、渠道、获客成本估算、90 天路线
- 若 `~/.dwy/skills/<名>/` 不存在：提示用户先跑 `dwy skills install`（或 `dwy claude sync` 会自动装），不要自己用内置能力顶替。

### 推荐跑法（顺序，可按上下文跳）
1. `startup-canvas` 先出整体画布（摸商业全貌 + 战略一致性）
2. `monetization-strategy` 出 3-5 个变现方案 + 各自单位经济 → 用户选 1-2 个主攻
3. `pricing-strategy` 对选定方案细化定价
4. `porters-five-forces` 判赛道结构是否压扁利润（利润空间 → 可行性）
5. `gtm-strategy` 出首批获客路径
6. 综合给可行性结论（pass/fail）

### 可行性判据（pass/fail 怎么判）
startup 模式给 pass 至少满足：
- 能讲通一条**具体变现路径**（不是「以后可以收钱」）
- 单位经济估算**合理**：LTV/CAC ≥ 3（或能说清到达该值的路径），毛利率不为负
- 有**低成本验证实验**可证伪付费意愿（落地页/预售/访谈愿付价）
- `porters-five-forces` 没暴露致命结构（如：供方垄断 + 买方集中 + 无差异化壁垒 → 利润被压扁）
四条任一明显不成立 → fail，写清哪条挂了、缺什么证据。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/商业分析.md`
- 固定章节：
  - 商业模式画布（9 模块 或 startup-canvas 摘要）
  - 变现路径（3-5 个方案，每个含：怎么收钱 + 单位经济 CAC/LTV/毛利率/回本周期估算 + 风险；**标注用户主攻的 1-2 个**）
  - 定价策略（模型选型 + 2-4 层分层 + 价值计量 + 价格敏感度判断）
  - 赛道结构（波特五力摘要 + 利润空间判断）
  - GTM 获客路径（首批用户来源 + 渠道 + 获客成本估算 + 90 天动作）
  - **可行性结论 pass/fail**（含理由 + 必须先验证的关键假设 + 对应低成本实验）
- 回写 state.json：`confirmed.commercial`（含 `mode`、`pass` 布尔、`skipped` 布尔、`monetization` 主攻方案、`unit_economics` 关键数字、`gtm` 首批渠道）
- **startup 模式 fail 时流程必须中断**，不进闸 2（POC）；builder 模式不写 fail
