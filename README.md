# dwy-ai-experience

> dwy-ai-experience 是一个 AI 工程化实践仓库，聚合前端组件、CLI 脚手架与后端服务模板。

[English](./README.en.md)

## 目录

- [项目简介](#项目简介)
- [仓库结构](#仓库结构)
- [claude-cli 主要能力](#claude-cli-主要能力)
- [快速开始](#快速开始)
- [开发与构建](#开发与构建)
- [发布与版本管理](#发布与版本管理)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 项目简介

`dwy-ai-experience` 面向 AI 工具链场景，整合了以下能力：

- 前端组件与工具库：`frontend/eui`、`frontend/ekit`
- 通用脚手架与同步能力：`claude-cli`
- 后端服务：`backend`（FastAPI）

## 仓库结构

- `/backend`：后端服务与运行时
- `/frontend/eui`：Vue 组件库
- `/frontend/ekit`：Vue 工具库
- `/frontend/playground`：组件展示与文档站
- `/claude-cli`：脚手架与规则模板同步工具

## claude-cli 主要能力

`claude-cli` 是仓库的核心协作入口，面向团队标准化开发流程：

- 项目模板生成
  - `dwy create <project-name>`：创建标准项目结构
- 规则与技能同步
  - `dwy sync`：同步已选目录到本地开发约定
  - `dwy claude sync`：同步技能/规则到 `.claude/`
  - `dwy claude sync md`：同步仓库 `CLAUDE.md` 到全局
  - `dwy codex sync`：转换并同步到 `.agents/` 与 `.codex/hooks/`
- 发布流程约束
  - 统一 npm/pypi 发布规范，支持 GitHub Action OIDC 发布
- 平台与适配规范
  - 提供 iOS / Android 全面屏适配、图标规范、注释规范等通用约束

## 快速开始

### 安装

```bash
cd claude-cli
pnpm install
```

### 使用示例

```bash
# 创建项目
npx create-dwy your-project

# 同步全局约定
dwy sync
dwy claude sync

dwy codex sync
```

## 开发与构建

```bash
cd frontend/eui && pnpm install && pnpm build
cd frontend/ekit && pnpm install && pnpm build
cd backend && uv sync
```

## 发布与版本管理

### CLI

- tag 规则：推送 `create-dwy@x.y.z` tag 后触发发布
- 发布链路：GitHub Actions，使用 OIDC（无 `NPM_TOKEN` / `UV_PUBLISH_TOKEN`）
- 发布产物：自动发布 npm 并同步 GitHub Release

### 组件与工具包

- eui 与 ekit 使用统一构建与发布流程

## 贡献指南

- 遵循仓库现有约定与 `AGENTS.md`
- 修改请分包提交并注明变更范围
- 若更新公共规则模板，请同步 `claude-cli/templates/` 对应目录

## 许可证

MIT
