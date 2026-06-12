# dwy-ai-experience

[中文](#中文) | [English](#english)

## 中文

[查看 English 版](#english)

`dwy-ai-experience` 是一个面向 AI 工具链的实践仓库，聚合前端组件库、CLI 脚手架、后端服务模板与发布流程规范。

## 关于本仓库

- 前端能力：`frontend/eui`、`frontend/ekit`
- 工具能力：`claude-cli`（代码规范、模板、规则与 hooks 同步）
- 后端能力：`backend`（FastAPI 服务）

## 目录

- [backend](./backend)
- [claude-cli](./claude-cli)
- [frontend/eui](./frontend/eui)
- [frontend/ekit](./frontend/ekit)

## 主要能力

- 统一代码与发布规则（AGENTS/CLAUDE/rules）
- CLI 版本与模板同步（`create-dwy`）
- GitHub Action 发布链路：npm 与 PyPI 使用 OIDC
- iOS / Android 全面屏适配约束规则收敛

## 使用方式

### 创建项目

```bash
npx create-dwy <project-name>
```

### 开发

```bash
cd frontend/eui && pnpm install
cd frontend/ekit && pnpm install
cd backend && uv sync
```

## 发布说明

- CLI 发布触发：推送 `create-dwy@x.y.z` tag
- 发布方式：GitHub Actions（OIDC），并自动创建 GitHub Release

## 许可证

MIT

## English

<details>
<summary>Expand English</summary>

`dwy-ai-experience` is an AI engineering repository that centralizes frontend libraries, CLI tooling, backend templates, and release workflows.

### About this repository

- Frontend packages: `frontend/eui`, `frontend/ekit`
- CLI tooling: `claude-cli` (sync rules, templates, and hooks)
- Backend: `backend` (FastAPI)

### Repository structure

- [backend](./backend)
- [claude-cli](./claude-cli)
- [frontend/eui](./frontend/eui)
- [frontend/ekit](./frontend/ekit)

### Highlights

- Unified project conventions (AGENTS/CLAUDE/rules)
- Project scaffolding and rules sync (`create-dwy`)
- GitHub Action releases for npm/PyPI with OIDC
- Standardized full-screen adaptation guidance for iOS/Android

### Getting started

```bash
npx create-dwy <project-name>
```

### License

MIT

</details>
