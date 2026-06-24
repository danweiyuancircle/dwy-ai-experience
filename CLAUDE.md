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
git push origin create-dwy@x.y.z        # create-dwy → npm（GitHub Actions OIDC 自动发布，免 token）
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

轻量工具库，薄封装主流开源库（axios / dayjs / zod / js-cookie / qs / file-saver / @vueuse/core），**严禁重复造轮子**（详见"ekit 依赖选择原则"）：

| 模块 | 内容 | 底层依赖 |
|------|------|---------|
| request | `createRequest()` + 插件（token/header/unwrap/refreshToken） | axios |
| storage | `useStorage()` + 静态 storage 对象 | @vueuse/core / localStorage |
| cookie | `useCookie()` + 静态 cookie 对象 | js-cookie |
| date | now / formatTimestamp / formatInTimezone / formatRelativeTime / formatDate / formatDateTime / formatTime / formatBy | dayjs（内部使用，不对外暴露实例/类型） |
| validators | isPhone / isEmail / isIdCard / isUrl / isRequired / minLength / maxLength + zod schema | zod |
| copy | copyText / useClipboard | @vueuse/core |
| qs | stringify / parse | qs |
| file | downloadFile / saveBlob / formatFileSize | file-saver |
| hooks | 再导出 @vueuse/core：useDebounce / useClickOutside / useEventListener / useThrottle / useWindowSize / useMediaQuery / useIntersectionObserver / useResizeObserver | @vueuse/core |
| masking | maskPhone / maskEmail / maskIdCard / maskBankCard / maskName / maskAddress / maskIp / maskLicensePlate / maskText | 自写（无合适开源） |

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

### dwy-cli/ — `create-dwy`

项目脚手架 + Claude 配置同步工具，命令行 `dwy`。

- **`dwy create [name]`**: 交互式创建项目，Handlebars 模板引擎，模板在 `templates/project/{template}/`
- **`dwy sync`**: 交互式选择一次，同步到 Claude Code 与 Codex；`dwy sync md` 同步 CLAUDE.md 到全局 ~/.claude/ 和 ~/.codex/AGENTS.md
- **`dwy claude sync`**: 从 `templates/claude-global/` 同步 skills/rules/commands/hooks 到项目 `.claude/`（settings.json 智能合并）；`dwy claude sync md` 仅同步 CLAUDE.md 到全局 ~/.claude/
- **`dwy codex sync`**: 把 Claude 模板转成 OpenAI Codex 格式同步到项目：rules→`AGENTS.md`（`<!-- DWY-RULES -->` 托管块，支持更新/删除且保留用户内容）、skills→`.agents/skills/`（拍平分类）、hooks→`.codex/hooks/` + `.codex/hooks.json`（Codex 版脚本读 stdin JSON）。Codex hooks 源在 `templates/codex-global/`；`dwy codex sync md` 仅把 CLAUDE.md 整文件同步到全局 ~/.codex/AGENTS.md
- 模板随 `create-dwy` 发布包内置于 `dwy-cli/templates/ai-tools`，`dwy` 运行时不再读取或刷新本机模板仓库缓存。

### frontend/playground/

Monorepo 文档门户，覆盖 EUI 组件 / EKit 工具 / Backend / CLI / Claude Code 五个模块。Vite SPA + Vue Router + markdown-it + Fuse.js 全局搜索。支持 `--host` 局域网访问。

## 缓存与配置存储约定

skill / 工具的本机判断缓存统一存项目内 `<project_root>/.dwy/<业务域>/`，按业务域建子目录，缓存目录统一：

- `<project_root>/.dwy/publish/`  — dwy-publish 发布方式缓存
- `<project_root>/.dwy/sdk-spec/` — dwy-sdk-spec SDK 版本类型 / 路径缓存

约束：

- 缓存内**不存绝对路径**，存相对项目根的相对路径，随项目走、可改名
- `.dwy/` 是本机判断缓存，必须加进 `.gitignore`，不入版本库
- 缓存文件用 JSON，含 `version` + `configured_at`

## 文档同步约束

- `docs/eui-integration-guide.md` 是 EUI 集成指南的唯一源文件
- 该文件变更后，必须同步到 `dwy-cli/templates/claude-global/skills/dwy-eui/references/eui-integration-guide.md`
- playground 的 `EuiIntegrationDoc.vue` 通过 `?raw` 导入同一文件，无需额外同步
- `docs/tasks-integration-guide.md` 是 Tasks 集成指南的唯一源文件
- 该文件变更后，必须同步到 `dwy-cli/templates/claude-global/skills/dwy-eapi/references/tasks-integration-guide.md`
- tasks 模块有变更时，需同步更新 `docs/tasks-integration-guide.md` 和 `dwy-cli/templates/claude-global/skills/dwy-eapi/SKILL.md` 中的 tasks 章节
- `docs/eui-design-guide.md` 是 EUI 中后台设计规范的唯一源文件
- `docs/eui-landing-design-guide.md` 是 EUI 落地页设计规范的唯一源文件
- 以上两个文件变更后，必须同步到 `dwy-cli/templates/claude-global/skills/dwy-eui/references/` 对应文件

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
| ekit | `cd frontend/ekit && pnpm vitest run` | `tests/{module}/{module}.test.ts` | `frontend/ekit/TEST_CASES.md` |
| eapi | `cd backend && pytest tests/ -v` | `tests/test_{module}.py` | `backend/TEST_CASES.md` |

### 禁止事项

- **禁止**不写测试就提交基础库代码变更
- **禁止** `TEST_CASES.md` 与实际测试文件不同步
- **禁止**删除模块时不删除对应测试
- **禁止**新增模块时不创建测试文件

## ekit 依赖选择原则

ekit 是**薄封装层**，定位"再导出 + 少量适配"。禁止重复造轮子，所有工具必须优先用成熟开源库。自写实现几乎一定比开源库兼容性差（缺 fallback、SSR-safe、跨标签页同步、边界处理）。

### 决策顺序（强制）

1. **`@vueuse/core` 有现成的** → 直接再导出（参考 `src/hooks/vueuse.ts` 模式）
2. **有其他成熟开源库**（npm stars > 1k、近 6 个月有维护） → 薄封装，只加 JSON 序列化、中文默认值等必要适配
3. **都没有** → 才可自写，且必须在 PR / commit body 说明"调研了哪些库、为何不用"

### 各模块依赖映射表

| 模块 | 必须使用的开源依赖 | 封装策略 |
|------|-------------------|---------|
| request | axios | 工厂 + 插件链（token / header / unwrap / refreshToken） |
| storage | `@vueuse/core` 的 `useStorage` | composable 直接再导出；静态 `storage` 对象可保留（非组件场景） |
| cookie | js-cookie | 薄封装 + JSON 自动序列化 |
| date | dayjs | 统一格式化/运算入口；**禁止** `new Date()` / `toLocaleString()` 手写 |
| validators | zod | schema 为主，`isXxx` 布尔壳调 `safeParse` |
| copy | `@vueuse/core` 的 `useClipboard` | 再导出；`copyText(text)` 可作为一次性快捷函数保留 |
| qs | qs | 再导出 `stringify` / `parse` |
| file | file-saver | 下载文件入口 `downloadFile` / `saveBlob` |
| hooks | `@vueuse/core` | **全部再导出**：`useDebounce`(→`refDebounced`) / `useClickOutside`(→`onClickOutside`) / `useEventListener` / `useThrottle` / `useWindowSize` 等 |
| masking | —（无开源方案） | 自写，PR 说明原因 |

### 禁止事项

- **禁止**在 ekit 中重新实现 `@vueuse/core` 已提供的 composable（`useClipboard`、`useStorage`、`useEventListener`、`onClickOutside`、`refDebounced`、`useMediaQuery`、`useIntersectionObserver` 等）
- **禁止**直接 `navigator.clipboard.writeText` / `localStorage.getItem` / `document.addEventListener` 手写同步/监听逻辑
- **禁止**自写日期运算（加减、比较、起止），一律走 dayjs API
- **禁止**为了"轻量"而不依赖 VueUse：`@vueuse/core` 已是 eui 的 peerDep，ekit 再依赖零成本

### 对外不泄露底层库类型（防腐层原则）

ekit 虽然底层用开源库实现，但**对外契约必须是 ekit 自有类型**，不能让底层库的类型名渗透到公共 API。这样以后要替换底层实现（axios → fetch、dayjs → date-fns、qs → native URLSearchParams 等），消费者代码不用改。

#### 硬性规则

- **禁止**从 `src/index.ts` re-export 底层库的实例 / 类 / 命名空间（反例：`export { dayjs }`、`export { default as axios }`）
- **禁止**从 `src/index.ts` re-export 底层库的类型别名（反例：`export type { AxiosInstance, IStringifyOptions, CookieAttributes }`）
- **禁止**函数签名直接暴露底层库类型（反例：`createRequest(): AxiosInstance`、`now(): dayjs.Dayjs`）
- **允许**底层库类型**仅出现在 `src/{module}/` 内部实现文件**（如 `src/request/client.ts` 用 axios 类型适配）

#### 对外契约规范

- **HTTP**：`HttpClient / HttpConfig / HttpResponse / HttpError / HttpPlugin / HttpMethod / HttpResponseType`
- **QS**：`StringifyOptions / ParseOptions`
- **Cookie**：`CookieOptions`
- **File**：`FileRequester / DownloadOptions`
- **Date**：`DateInput`（string | number | Date）、函数返回 `Date / string / number` 原生类型

#### 例外（刻意暴露的集成点）

- **validators** 导出的 zod schema（`phoneSchema` 等）是**刻意**的公共 API，供消费者配合 `vee-validate` 使用，不视为泄露
- **VueUse 再导出**（`useStorage / useClipboard / useDebounce` 等）是 Vue 生态共识接口，替换成本远大于收益，不视为泄露
- **插件内部**（如 `HttpPlugin` 的 `onRequest / onResponse`）参数类型必须是 ekit 自有契约，禁止掺入 axios 类型

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
| create-dwy | cli | dwy-cli/package.json | — | — | `git push origin create-dwy@x.y.z`（GitHub Actions OIDC 自动发布） | npm view create-dwy version |

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

### create-dwy (CLI) 发布

走 GitHub Actions + npm OIDC Trusted Publishing，**不用 NPM_TOKEN**：

1. 改 `dwy-cli/package.json` 的 `version`，commit 推 `origin`
2. 打 tag `create-dwy@x.y.z`（版本号须与 package.json 一致，否则 CI 校验失败）
3. `git push origin create-dwy@x.y.z` → 触发 `.github/workflows/publish-cli.yml` 自动发布

- `origin` 即 GitHub 仓库 `danweiyuancircle/dwy-ai-experience`，推 tag 即触发 CI
- npm 侧已绑定 Trusted Publisher：`danweiyuancircle/dwy-ai-experience` + `publish-cli.yml`
