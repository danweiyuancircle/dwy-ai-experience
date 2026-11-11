---
name: dwy-mvp
description: "【dwy·MVP定义】产品 0 到 1 立项阶段（闸3）。触发场景：用户说『定义 MVP / 最小可行产品 / 先做哪些功能 / 砍功能 / 第一版做什么 / mvp』，要从想法收敛出第一版必须做的核心功能清单时。MVP 功能硬上限 ≤7 个。"
---

## 职责（单一）
从想法+验证结果，收敛出第一版 MVP 功能清单。**功能硬上限 ≤7 个**，超出的进后续版本。

## 输入（从哪读）
- state.json 的 `confirmed.idea`（含 explore 逼出的最窄切入 narrowest_wedge——MVP 砍 ≤7 直接对着它砍）、`confirmed.validation`、`confirmed.poc`
- `.dwy/prod/[项目]/01-立项/想法收敛.md`、`需求市场验证.md`、`技术验证.md`

## 实现
[包装型] 依赖 [pm-skills](https://github.com/phuryn/pm-skills) 的下列 Skill；dwy 只声明依赖，不捆绑下载。
按名称查找宿主已安装的 Skill/插件，不固定目录或版本；读取其 `SKILL.md` 及任务所需的 scripts/、配套文件，按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`prioritize-features`、`opportunity-solution-tree`
- 缺失时由 AI 核实来源与宿主适配信息，按已有授权和项目工具安装规则处理；依赖声明不等于安装授权。仍无法取得时说明缺口，暂停依赖步骤，不降级、替代或假称已执行，不要求用户运行 `dwy`。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/01-立项/MVP清单.md`
- 固定章节：MVP 功能清单（≤7 个）/ 优先级排序 / 砍到后续版本的功能
- **功能数超 7 个直接拒绝，强制收敛**
- 回写 state.json：`confirmed.mvp_features`
