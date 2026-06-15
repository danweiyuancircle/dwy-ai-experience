<div align="center">
  <h1>dwy-ai-experience</h1>
  <p><strong>dwy 的个人 AI 仓库</strong></p>
  <p>聚焦 AI 工具链、项目脚手架、规则同步与工程化发布流程</p>
  <p>
    <a href="./README.en.md">English</a>
  </p>
  <p>
    <img src="https://img.shields.io/github/actions/workflow/status/danweiyuancircle/dwy-ai-experience/publish-cli.yml?label=Build%20%26%20Release%20CLI" alt="Build and Release CLI" />
    <img src="https://img.shields.io/npm/v/create-dwy?label=create-dwy" alt="create-dwy version" />
    <img src="https://img.shields.io/github/license/danweiyuancircle/dwy-ai-experience" alt="license" />
    <img src="https://img.shields.io/badge/platform-Claude%20%2F%20Codex-blue" alt="platform" />
  </p>
</div>

## 简介

`dwy-ai-experience` 是一个围绕 AI 开发体验搭建的 monorepo，当前主要覆盖三类能力：

- `dwy-cli`：项目脚手架、规则模板、Claude/Codex 同步入口
- `frontend/*`：前端组件库、工具库与演示站
- `backend`：FastAPI 后端基础设施与服务模板

这个仓库的重点不是单个包，而是把团队协作规范、项目初始化方式、AI 编码约束和发布流程统一收敛到一套可复用工具链。

## 核心包

### `@dwydev/eui`

基于 shadcn UI 样式、Element UI 写法、Tailwind CSS 4 和 Reka UI 的 Vue 3 组件库，面向中后台、管理台、业务表单和内部工具。

```bash
npm install @dwydev/eui
```

### `dwyeapi`

面向 FastAPI 项目的基础设施库，提供配置、异常、数据库、安全、缓存、分页、日志等后端通用能力。

```bash
pip install dwyeapi
```

### `@dwydev/ekit`

Vue 3 工具库，提供 hooks、请求封装、时间处理、下载、cookie、querystring 等项目常用工具能力。

```bash
npm install @dwydev/ekit
```

## 主要特性

- 统一项目初始化、规则分发、技能同步与 hooks 同步
- 支持 `Claude` 与 `Codex` 两套本地协作配置落地
- npm / PyPI 发布流程收敛到 GitHub Actions OIDC
- 内置移动端全面屏、图标库、注释规范等通用工程规则

## Claude CLI

`dwy-cli` 是这个仓库最核心的模块，目标不是只做“创建项目”，而是把团队协作规范直接写进工具链。

### 核心命令

- `dwy create <project-name>`
  - 创建标准项目模板
- `dwy sync`
  - 同步选中的共享约定到当前项目
- `dwy claude sync`
  - 同步技能、规则、命令与 hooks 到项目 `.claude/`
- `dwy claude sync md`
  - 同步仓库 `CLAUDE.md` 到全局配置
- `dwy codex sync`
  - 将 Claude 模板转换并同步到 `.agents/`、`.codex/hooks/`、`AGENTS.md`

### 解决的问题

- 让新项目快速继承统一目录结构与基础工程配置
- 让团队规则不再依赖口头约定或复制粘贴
- 让 Claude Code / Codex 的项目级配置可持续同步
- 让发布流程逐步收敛到可审计的 GitHub Actions

## 仓库结构

- `/dwy-cli`
  - `create-dwy` CLI、本地同步逻辑、模板与规则源
- `/frontend/eui`
  - Vue 组件库
- `/frontend/ekit`
  - Vue 工具库
- `/frontend/playground`
  - 组件演示与文档站
- `/backend`
  - FastAPI 基础设施与后端模板

## Libraries

### `@dwydev/eui`

Vue 3 组件库，定位是基于 shadcn UI 的样式、Element UI 的写法，结合 Tailwind CSS 4 和 Reka UI，提供可直接复用的业务组件能力。

- 组件基础：按钮、输入框、弹层、菜单、表格、日历等
- 风格与交互：shadcn UI 样式 + Element UI API 写法
- 设计基座：Tailwind CSS 4 + Reka UI
- 适用场景：中后台、管理台、内部工具、业务表单

```bash
npm install @dwydev/eui
```

### `@dwydev/ekit`

Vue 3 工具库，提供项目常用 hooks、请求封装、时间处理、下载与 cookie 等通用能力，目标是减少业务项目重复造轮子。

- 通用 hooks 与辅助函数
- 请求层插件链封装
- 文件下载、cookie、querystring 等常用工具

```bash
npm install @dwydev/ekit
```

### `dwyeapi`

FastAPI 基础设施库，提供后端项目常用的配置、异常、数据库、安全、缓存、分页、日志等能力。

- 配置管理：基于 `pydantic-settings`
- 数据库：`SQLAlchemy asyncio`
- 安全能力：JWT、密码哈希
- 基础设施：Redis、分页、日志、统一异常处理

```bash
pip install dwyeapi
```

如需任务队列或邮件扩展：

```bash
pip install "dwyeapi[tasks]"
pip install "dwyeapi[email]"
```

## 快速开始

### 安装 CLI 依赖

```bash
cd dwy-cli
pnpm install
```

### 创建并同步

```bash
npx create-dwy your-project

dwy sync
dwy claude sync
dwy codex sync
```

## 开发

```bash
cd frontend/eui && pnpm install && pnpm build
cd frontend/ekit && pnpm install && pnpm build
cd backend && uv sync
```

## 发布

### CLI

- tag 规则：`create-dwy@x.y.z`
- 发布方式：GitHub Actions + OIDC
- 发布结果：自动发布 npm，并自动创建 GitHub Release

### Libraries

- `eui` 与 `ekit` 使用统一的构建与发布流程

## Contributing

- 遵循仓库内 [`AGENTS.md`](./AGENTS.md) 与对应模板约定
- 跨包改动尽量拆分提交，保持变更边界清晰
- 如果修改共享模板或规则，同步更新 `dwy-cli/templates/`

## License

MIT
