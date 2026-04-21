# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

共享基础包 monorepo。pnpm workspace 管理前端 + CLI，Python (uv) 单独管理后端。

## Commands

```bash
# 安装
pnpm install                                          # 前端 + CLI 依赖
cd backend && uv venv && uv pip install -e ".[dev]"   # 后端依赖

# 构建
pnpm build:eui                    # @dwydev/eui (Vite)
pnpm build:ekit                   # @dwydev/ekit (Vite)
pnpm build:frontend               # 同时构建 eui + ekit

# 测试
cd frontend/eui && pnpm vitest run                    # eui 全部测试
cd frontend/eui && pnpm vitest run src/components/button  # eui 单个组件测试
pnpm test:eapi                                        # 后端全部测试 (pytest -v)
cd backend && pytest tests/test_security.py -v        # 后端单个模块测试

# Lint（仅后端）
cd backend && ruff check src/ && ruff format --check src/

# 发布
pnpm build:eui && pnpm publish:eui      # @dwydev/eui → npm
pnpm build:ekit && pnpm publish:ekit    # @dwydev/ekit → npm
source .key && pnpm publish:eapi        # dwyeapi → PyPI (uv build && uv publish)
pnpm publish:cli                        # create-dwy → npm
```

## Architecture

### frontend/eui/ — `@dwydev/eui`

Vue 3 组件库，89 个组件。基于 Reka-ui 原语层 + shadcn-vue 设计风格 + Element Plus 式 API。

- **构建**: Vite 8 → ES modules only，vite-plugin-dts 生成 .d.ts
- **样式**: Tailwind CSS 4 (@tailwindcss/vite)，CSS 自定义属性做 design tokens
- **组件结构**: 每个组件一个目录 `src/components/{name}/`，包含 `EName.vue` + `index.ts` + `types.ts` + 可选 `.test.ts`
- **主题系统**: `src/theme/` 导出 tokens.css（设计变量）、dark.css（暗色模式）、presets.css（Tailwind 预设），通过 package.json exports 单独引入
- **Composables**: `src/composables/` — useConfigProvider, useFormField, useMessage, useNotification, useMessageBox, useTheme
- **关键依赖**: reka-ui, @floating-ui/vue, @tanstack/vue-table, vee-validate + zod, class-variance-authority + tailwind-merge
- **reka-ui 绑定约定**: reka-ui 组件统一用 `v-model`（`modelValue` / `update:modelValue`），**不是** `:checked` / `@update:checked`。封装 reka-ui 原语时必须用 `v-model` 或 writable computed 绑定
- **路径别名**: `@/` → `./src/`
- **测试**: Vitest + jsdom

### frontend/ekit/ — `@dwydev/ekit`

轻量工具库，6 个模块：

| 模块 | 内容 |
|------|------|
| request | Axios 工厂 `createRequest()`，插件架构（token/header/unwrap/refreshToken） |
| storage | `useStorage()` composable + 静态 storage 对象（localStorage 封装） |
| date | formatRelativeTime, formatDate, formatDateTime, formatTime |
| validators | isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength |
| hooks | useDebounce, useClickOutside, useEventListener |
| masking | maskPhone, maskEmail, maskIdCard, maskBankCard, maskName, maskAddress, maskIp, maskLicensePlate, maskText |

request 模块的 401 刷新 token 逻辑会自动重试失败请求，响应 unwrap 约定格式 `{ code, data, message }`。

### backend/ — `dwyeapi`

FastAPI 基础设施包，Python 3.11+，全异步。9 个扁平模块：

| 模块 | 内容 |
|------|------|
| config | BaseSettings（database_url, redis_url, secret_key） |
| database | AsyncEngine 工厂, DeclarativeBase, TimestampMixin (created_at/updated_at) |
| security | JWT create_token/decode_token, bcrypt hash/verify |
| exceptions | AppError 层级 → NotFoundError, BusinessError, PermissionDeniedError, AuthenticationError + FastAPI handler 注册 |
| response | success(), fail(), paginated() → `{ code, message, data, timestamp }` |
| pagination | PaginationParams, paginate(), OffsetLimit |
| cache | 异步 Redis 管理: configure(), get_redis(), close_redis() |
| dependencies | FastAPI 依赖注入工厂 |
| masking | PII 数据脱敏: mask_phone, mask_email, mask_id_card, mask_bank_card, mask_name, mask_address, mask_ip, mask_license_plate, mask_text |

- **Lint**: Ruff（规则: E, W, F, I, N, UP, B, SIM, RUF），行宽 120
- **测试**: pytest + pytest-asyncio (asyncio_mode = "auto")

### claude-cli/ — `create-dwy`

项目脚手架 + Claude 配置同步工具，命令行 `dwy`。

- **`dwy create [name]`**: 交互式创建项目，Handlebars 模板引擎，模板在 `templates/project/{template}/`
- **`dwy sync claude`**: 从 `templates/claude-global/` 同步全局 ~/.claude/ 配置（settings.json 智能合并）
- **`dwy sync project-claude`**: 同步项目级 .claude/ 配置
- 模板缓存在 `~/.dwy/cache/dwy/`，从 Gitee 拉取 dwy-shared 仓库

### frontend/playground/

Monorepo 文档门户，覆盖 EUI 组件 / EKit 工具 / Backend / CLI / Claude Code 五个模块。Vite SPA + Vue Router + markdown-it + Fuse.js 全局搜索。支持 `--host` 局域网访问。

## 文档同步约束

- `docs/eui-integration-guide.md` 是 EUI 集成指南的唯一源文件
- 该文件变更后，必须同步到 `claude-cli/templates/claude-global/skills/dwy-frontend-eui/eui-integration-guide.md`
- playground 的 `EuiIntegrationDoc.vue` 通过 `?raw` 导入同一文件，无需额外同步
- `docs/tasks-integration-guide.md` 是 Tasks 集成指南的唯一源文件
- 该文件变更后，必须同步到 `claude-cli/templates/claude-global/skills/dwy-backend-eapi/tasks-integration-guide.md`
- tasks 模块有变更时，需同步更新 `docs/tasks-integration-guide.md` 和 `claude-cli/templates/claude-global/skills/dwy-backend-eapi/SKILL.md` 中的 tasks 章节
- `docs/eui-design-guide.md` 是 EUI 中后台设计规范的唯一源文件
- `docs/eui-landing-design-guide.md` 是 EUI 落地页设计规范的唯一源文件
- 以上两个文件变更后，必须同步到 `claude-cli/templates/claude-global/skills/dwy-frontend-eui/` 对应文件

## 基础库开发规范

eui、ekit、eapi 三个基础库被多个项目依赖，变更必须严格遵循以下流程：

### 变更流程（强制）

1. **先改测试** — 新增/修改/删除模块前，先在对应测试文件中增删用例
2. **再写代码** — 实现功能，确保新增测试通过
3. **回归测试** — 根据变更影响范围选择回归策略（见下方回归策略）
4. **同步文档** — 更新对应包的 `TEST_CASES.md`，保持用例清单与实际测试一致

### 回归测试策略

按变更影响范围选择最小够用的回归范围，不做无意义的全量回归：

| 变更类型 | 回归范围 | 示例 |
|---------|---------|------|
| 单组件/单模块内部修复 | 仅该组件/模块的测试文件 | 修 DatePicker 样式 → `vitest run tests/components/date-picker.test.ts` |
| 修改共享工具/composable | 该工具 + 所有引用它的模块 | 改 `useFormField` → useFormField 测试 + 所有使用它的组件测试 |
| 修改导出入口/类型定义/构建配置 | 包全量测试 | 改 `index.ts` 导出 → `pnpm vitest run` |
| 升级依赖/修改基础设施 | 包全量测试 | 升级 reka-ui → `pnpm vitest run` |

| 包 | 测试命令 | 测试文件规范 | 用例文档 |
|----|---------|-------------|---------|
| eui | `cd frontend/eui && pnpm vitest run` | `tests/components/{name}.test.ts` | `frontend/eui/TEST_CASES.md` |
| ekit | `cd frontend/ekit && pnpm vitest run` | `src/{module}/{module}.test.ts` | `frontend/ekit/TEST_CASES.md` |
| eapi | `cd backend && pytest tests/ -v` | `tests/test_{module}.py` | `backend/TEST_CASES.md` |

### 禁止事项

- **禁止**不写测试就提交基础库代码变更
- **禁止** `TEST_CASES.md` 与实际测试文件不同步
- **禁止**删除模块时不删除对应测试
- **禁止**新增模块时不创建测试文件

## Git Commit Scope

本项目的 scope 枚举：`eui` | `ekit` | `eapi` | `cli` | `playground`

- 单包变更必须带 scope：`feat(eui): add Image component`
- 跨包变更省略 scope：`chore: upgrade Vite to 8.x`
- 仅改一个包内的文件时拆成单独 commit，不混包提交

## Release

### 包列表

| 包名 | scope | 版本文件 | 测试命令 | 构建命令 | 发布命令 | 验证命令 |
|------|-------|---------|---------|---------|---------|---------|
| @dwydev/eui | eui | frontend/eui/package.json | cd frontend/eui && pnpm vitest run | pnpm build:eui | pnpm publish:eui | npm view @dwydev/eui version |
| @dwydev/ekit | ekit | frontend/ekit/package.json | cd frontend/ekit && pnpm vitest run | pnpm build:ekit | pnpm publish:ekit | npm view @dwydev/ekit version |
| dwyeapi | eapi | backend/pyproject.toml | cd backend && pytest tests/ -v | — | source .key && pnpm publish:eapi | pip index versions dwyeapi |
| create-dwy | cli | claude-cli/package.json | — | — | pnpm publish:cli | npm view create-dwy version |

### 依赖顺序

多包发版时按此顺序：ekit → eui → eapi → cli

### Tag 命名

- 单包：`@dwydev/eui@1.3.0`、`create-dwy@0.6.0`
- 多包同时发布：每个包各打一个 tag

### CHANGELOG

- 命令：`pnpm changelog`
- 工具：changelogen

### PyPI 凭证

- Token 存储在项目根目录 `.key` 文件中（已 gitignore）
- 发布 eapi 前需先加载：`source .key`
