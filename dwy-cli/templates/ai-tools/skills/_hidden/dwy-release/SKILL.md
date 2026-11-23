---
name: dwy-release
description: "【dwy·上架迭代】产品 0 到 1 上架迭代阶段（终点）。触发场景：用户说『上架 / 发布上线 / 出上架物料 / 配埋点 / 规划下一版 / release』，要准备上架物料、埋点指标并规划下一版迭代时。"
---

## 职责（单一）
产出上架物料 + 埋点指标设计 + 下一版迭代规划。

## 输入（从哪读）
- state.json 的 `confirmed.acceptance`、`confirmed.prd`、`confirmed.version_plan`
- `.dwy/prod/[项目]/05-上线交付/验收报告.md`
- `.dwy/prod/[项目]/02-需求规划/版本路线图.md`

## 实现
[包装型] 依赖 [pm-skills](https://github.com/phuryn/pm-skills) 的下列 Skill；dwy 只声明依赖，不捆绑下载。
按名称查找宿主已安装的 Skill/插件，不固定目录或版本；读取其 `SKILL.md` 及任务所需的 scripts/、配套文件，按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`release-notes`、`gtm-strategy`、`metrics-dashboard`、`north-star-metric`
- 缺失时由 AI 核实来源与宿主适配信息，按已有授权和项目工具安装规则处理；依赖声明不等于安装授权。仍无法取得时说明缺口，暂停依赖步骤，不降级、替代或假称已执行，不要求用户运行 `dwy`。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/05-上线交付/上架物料.md`、`埋点与指标.md`、`下一版迭代规划.md`
- 固定章节：
  - 上架物料.md：发布说明 / GTM 策略 / 渠道文案
  - 埋点与指标.md：北极星指标 / 埋点清单 / 指标看板设计
  - 下一版迭代规划.md：数据反馈方向 / 下一版功能候选 / 优先级
- 回写 state.json：`confirmed.release`（上架物料就绪 + 下一版迭代方向）
