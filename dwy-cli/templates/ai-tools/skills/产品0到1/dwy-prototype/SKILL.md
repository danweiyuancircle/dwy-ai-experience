---
name: dwy-prototype
description: "【dwy·UI原型】产品 0 到 1 设计与架构阶段。触发场景：用户说『画原型 / 出原型 / 做 UI 原型 / 把页面画出来 / prototype』，要在写 UI 代码前把页面与交互流程画成白板原型时。"
---

## 职责（单一）
把 PRD 的页面与交互画成白板 HTML 原型。**不重复造**，直接调用现有的 `dwy-whiteboard-prototype` skill。

## 输入（从哪读）
- state.json 的 `confirmed.prd`、`confirmed.tasks`
- `.dwy/prod/[项目]/02-需求规划/PRD.md`

## 实现
[自写型]
1. 直接调用现有 skill `dwy-whiteboard-prototype`（位于 `skills/开发流程/dwy-whiteboard-prototype/`）
2. 按其规范画白板：每页一个 HTML，状态全、跳转清
3. **不另起炉灶手搓白板引擎**，复用其 `assets/template.html`
4. 产出目录改为本阶段约定路径（见产出契约）

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/03-设计与架构/prototypes/`，每页一个 `<页面>-spec.html` + `index-spec.html` 总览
- 固定要求：覆盖 PRD 所有页面、状态全、跨白板跳转清
- 回写 state.json：`confirmed.prototype`
