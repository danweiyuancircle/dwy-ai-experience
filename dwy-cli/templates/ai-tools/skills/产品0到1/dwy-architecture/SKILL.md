---
name: dwy-architecture
description: "【dwy·技术架构】产品 0 到 1 设计与架构阶段。触发场景：用户说『设计架构 / 出技术方案 / 设计库表 / 定接口契约 / 技术架构 / architecture』，要在开发前定下技术架构、数据库设计和接口契约时。"
---

## 职责（单一）
按项目 rules 产出技术架构 + 数据库库表设计 + 接口契约。

## 输入（从哪读）
- state.json 的 `confirmed.prd`、`confirmed.tasks`、`confirmed.prototype`
- `.dwy/prod/[项目]/02-需求规划/PRD.md`、`开发任务拆解.md`
- 项目 `.claude/rules/` 下的技术栈与编码规则

## 实现
[自写型]
1. 读项目 `.claude/rules/`，按项目既定技术栈与规范产出架构
2. 技术架构：分层、模块边界、技术选型理由
3. 数据库设计：库表、字段、索引、关系
4. 接口契约：路由、请求/响应 schema（遵循项目响应格式约定）
5. **走 rules 土建**，不引入项目规范外的技术栈

## 产出契约（硬约束）
- 落到：`.dwy/prod/[项目]/03-设计与架构/技术架构.md`、`数据库设计.md`、`接口契约.md`
- 固定章节：
  - 技术架构.md：分层架构 / 模块划分 / 技术选型
  - 数据库设计.md：库表清单 / 字段定义 / 关系与索引
  - 接口契约.md：接口清单 / 请求响应 schema / 错误码
- 回写 state.json：`confirmed.architecture`
