---
name: dwy-prd
description: "【dwy·PRD生成】产品 0 到 1 需求规划阶段。触发场景：用户说『写 PRD / 出需求文档 / 产品需求文档 / prd』，要把 MVP 清单细化成可开发的产品需求文档时。"
---

## 职责（单一）
把 MVP 功能清单细化成完整可开发的 PRD。

## 输入（从哪读）
- state.json 的 `confirmed.mvp_features`、`confirmed.idea`
- `.dwy/prod/[项目]/01-立项/MVP清单.md`

## 实现
[包装型] 依赖 [pm-skills](https://github.com/phuryn/pm-skills) 的下列 Skill；dwy 只声明依赖，不捆绑下载。
按名称查找宿主已安装的 Skill/插件，不固定目录或版本；读取其 `SKILL.md` 及任务所需的 scripts/、配套文件，按它的方式与用户交互/提问，产出按下方「产出契约」落地。
- **提问形式（Claude Code 下强制）**：借用外部 skill 的「问什么、怎么一步步收敛」方法论，但**每个要用户选择/拍板的问题用 `AskUserQuestion` 工具弹点选卡片**，不在正文列 A/B/C/D 让用户打字；保留「一次一问、答完再问下一个」的节奏，开放式补充靠卡片的「Other」兜底。其他工具（Codex 等无此组件）退回外部 skill 原生的正文问答。
- 本 skill 依赖的外部 skill：`create-prd`
- 缺失时由 AI 核实来源与宿主适配信息，按已有授权和项目工具安装规则处理；依赖声明不等于安装授权。仍无法取得时说明缺口，暂停依赖步骤，不降级、替代或假称已执行，不要求用户运行 `dwy`。

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/02-需求规划/PRD.md`
- 固定章节：背景与目标 / 用户场景 / 功能需求（逐条）/ 非功能需求 / 验收标准
- 回写 state.json：`confirmed.prd`
