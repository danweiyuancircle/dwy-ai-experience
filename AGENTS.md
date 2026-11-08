

## 分支与工作目录

- `master` 为主干，`develop` 为日常开发分支；验收通过后将 `develop` 合入 `master`。
- 默认直接在仓库主工作目录的 `develop` 上修改，不另建功能分支或额外 worktree；用户明确要求时例外。
- 分支整合不重写已交付的语义化标签，也不自动删除既有分支或 worktree。

## 源码与公开包分发

GitHub 源码仓库公开；npm 与 PyPI 安装包公开发布，允许任何人安装使用。所有 registry 发布必须由 `.github/workflows/publish-*.yml` 使用 OIDC 完成，不使用长期发布 token。发布前验证实际仓库可访问；根工作区保留 `private: true`，可发布 npm 包使用公开 access，Python 包不得包含禁止上传的 Private classifier。`.github/workflows/private-release.yml` 保留跨包 CI 与可选 GitHub 快照，不作为唯一分发渠道。SwiftPM 继续通过同一 Git 仓库的语义化标签消费。不得在 URL、包配置或提交文件中写入私有凭据。

# AGENTS.md

Compact instructions for OpenCode sessions working in `dwy-shared`.

## Monorepo Layout

| Directory | Package Manager | Package | Type |
|-----------|-----------------|---------|------|
| `frontend/eui/` | pnpm | `@dwydev/eui` | Vue 3 component library (~95 components) |
| `frontend/ekit/` | pnpm | `@dwydev/ekit` | Vue 3 utility library |
| `frontend/admin-shell/` | pnpm | `@dwydev/admin-kit` | Vue 3 administrator framework |
| `frontend/auth-web/` | pnpm | `@dwydev/auth-web` | Administrator login components and Cookie sessions |
| `frontend/playground/` | pnpm | — | Docs portal (Vite SPA) |
| `dwy-cli/` | pnpm | `create-dwy` | CLI scaffold + Claude config sync |
| `backend/` | uv | `dwyeapi` | FastAPI infrastructure (Python 3.11+) |
| `backend/packages/device-fingerprint/` | uv | `dwy-device-fingerprint` | Standalone native device fingerprint package |
| `backend/packages/auth/` | uv | `dwy-auth` | Application authentication and independent administrator sessions |
| `ios/` | SwiftPM (root `Package.swift`) | `AppleAppKit` | iOS/macOS frameworks, authentication, tests, and templates |

`pnpm-workspace.yaml` only covers `frontend/*` and `dwy-cli`. Python backend is managed separately by uv and **not** in the pnpm workspace.

**Package manager**: use the pnpm version declared by root `package.json`; the workspace lockfile is `pnpm-lock.yaml`. Do not use yarn.

### 通用规则（语言无关）

- 导出的类、函数、组件 props 写清用途和调用约束。不看代码就看不出的约束要写。一行就能看懂的语句不写注释。
- 图标默认优先使用成熟且稳定的图标库（如 `lucide-vue-next`、`heroicons`、`@iconify/vue`、`@tabler/icons` 等）。禁止使用 emoji 作为功能性图标或状态标识。
- 开发 iOS 和 Android 客户端时，默认按全面屏/刘海屏适配处理，优先基于安全区域和自适应布局而非固定边距。

## Developer Commands

### One-time setup

```bash
pnpm install                                          # frontend + CLI only
cd backend && uv venv && uv pip install -e ".[dev]"  # backend deps
```

### Build

```bash
pnpm build:eui         # @dwydev/eui (Vite, ES modules only)
pnpm build:ekit        # @dwydev/ekit (Vite)
pnpm build:frontend    # both eui + ekit
```

### Dev

```bash
cd frontend/eui && pnpm dev      # vite build --watch (not a dev server)
cd frontend/playground && pnpm dev   # vite --host (docs portal, LAN accessible)
```

### Test

```bash
# eui — Vitest + jsdom
cd frontend/eui && pnpm vitest run
cd frontend/eui && pnpm vitest run tests/components/button.test.ts
cd frontend/eui && pnpm vitest run tests/utils/cn.test.ts

# ekit — Vitest + jsdom
cd frontend/ekit && pnpm vitest run

# eapi — pytest + pytest-asyncio (asyncio_mode = "auto")
cd backend && pytest tests/ -v
cd backend && pytest tests/test_security.py -v             # single module
```

### Lint

```bash
cd backend && ruff check src/ && ruff format --check src/  # ruff only; no frontend linter
```

### Public package release

Keep the Git source public and publish installable packages to public npm/PyPI through `.github/workflows/publish-*.yml` using OIDC. Each package tag is `<package-name>@<version>` and must match its manifest. The root workspace remains private; distributable npm packages use public access. Standard semantic Git tags remain the SwiftPM entry point and may create a GitHub snapshot. See `docs/private-distribution.md`.

## Architecture Quirks

### eui (@dwydev/eui)

- **Stack**: Vue 3 + Reka-ui primitives + Tailwind CSS 4 + vite-plugin-dts (`.d.ts` generation)
- **Build output**: ES modules only (`formats: ['es']`); externalized deps include `vue`, `reka-ui`, `@vueuse/core`, `lucide-vue-next`, `zod`, etc.
- **Path alias**: `@/` → `./src/`
- **Reka-ui binding rule**: always use `v-model` (`modelValue`/`update:modelValue`), never `:checked`/`@update:checked`
- **EConfigProvider is mandatory** at the app root. Without it, date pickers/calendars render in English, z-index is uncoordinated, and UI text falls back to defaults. See `references/eui-integration-guide.md` for full setup.
- **Known peer-dep issue**: `vue-sonner` may need manual install in consuming projects due to pnpm strict hoisting.

### ekit (@dwydev/ekit)

- **Thin wrapper policy**: do not reinvent wheels. Priority: 1) `@vueuse/core` re-export, 2) mature npm library thin wrapper, 3) custom implementation (with justification).
- **Type leakage rule**: never re-export underlying library types/classes from `src/index.ts`. Public API must use ekit-owned types (e.g., `HttpClient`, not `AxiosInstance`).
- **Request module**: factory + plugin chain (`tokenPlugin`, `unwrapPlugin`, `refreshTokenPlugin`). Unwrap expects `{ code, message, data, timestamp }`.

### eapi (dwyeapi)

- **Environment**: `BaseSettings.environment` defaults to `"prod"` (safe-by-default). Use `is_dev()` / `is_prod()` / `get_environment()`.
- **FastAPI docs**: only expose `/docs`, `/redoc`, `/openapi.json` when `is_dev()`.
- **Ruff config**: line length 120, rules `E,W,F,I,N,UP,B,SIM,RUF`.
- **Conftest quirk**: `backend/tests/conftest.py` has an `autouse` fixture that resets the global environment back to `"prod"` after every test to prevent state leakage.
- **Tasks module**: requires `[tasks]` extra (`arq`).

### CLI (create-dwy)

- No build step (`build:cli` is a no-op).
- 已实现入口必须出现在 `dwy --help`；禁止把可用命令藏成「隐藏命令」。
- Commands: `dwy` / `dwy sync`（范围 → Skills → 项目 Rules → 通用规范 → Hooks → CLI → 确认）；`dwy refresh`（从当前 CLI 包内模板刷新已安装共享 Skills）；`dwy migrate`（迁移老项目入口）；`dwy upgrade`（更新到 npm 正式版 latest）；`dwy --help` / `dwy --version`。
- Skills / Rules 按分类显示 Tab；通用规范和 Hooks 默认启用，项目已有有效全局提供者时跳过对应选择且不重复写入。CLI 最后选择，Codex 默认选中，并恢复当前范围已同步的其他 CLI。Commands 停用并保留本地文件，启动时展示 dwy 品牌。
- 不存在 `dwy claude sync` / `dwy codex sync` / `dwy sync md` / `dwy skills install`（平台选择与刷新外部 skill 都在 `dwy` 交互里完成）。
- AI 模板随 CLI 包分发，目录为 `dwy-cli/templates/ai-tools`；启动不联网检查或下载模板，新增 Skills 需发布 CLI。`DWY_TEMPLATE_SOURCE_DIR` 仅供开发者显式覆盖。目标配置和所选共享 Skills 仅在确认后修改；项目已被有效全局入口完整覆盖的 Skills 禁止重复勾选。详见 `docs/cli-sync.md`。

## Workflow Conventions

### Git commit scope (mandatory for single-package changes)

Scope enum: `eui` | `ekit` | `eapi` | `cli` | `playground`

```
feat(eui): add Image component
chore: upgrade Vite to 8.x      # cross-package, omit scope
```

### Base-library change process (eui / ekit / eapi)

1. **Update tests first** — add/modify cases before touching source
2. **Implement**
3. **Regression** — run scoped tests based on blast radius (single component → shared util → full package)
4. **Sync docs** — keep `TEST_CASES.md` aligned with actual tests

Never skip tests for base-library changes. Never let `TEST_CASES.md` drift from real test files.

### Documentation sync constraints

When these docs change, sync to the dwy-cli template paths:

| Source | Target sync path |
|--------|------------------|
| `docs/eui-integration-guide.md` | `dwy-cli/templates/ai-tools/skills/Vue/dwy-eui/references/eui-integration-guide.md` |
| `docs/eui-design-guide.md` | `dwy-cli/templates/ai-tools/skills/Vue/dwy-eui/references/eui-design-guide.md` |
| `docs/eui-landing-design-guide.md` | `dwy-cli/templates/ai-tools/skills/Vue/dwy-eui/references/eui-landing-design-guide.md` |
| `docs/tasks-integration-guide.md` | `dwy-cli/templates/ai-tools/skills/Python/dwy-eapi/references/tasks-integration-guide.md` |

Playground imports `docs/eui-integration-guide.md` via `?raw`; it does **not** need a separate copy.

## Entry Points

- **eui lib entry**: `frontend/eui/src/index.ts`
- **ekit lib entry**: `frontend/ekit/src/index.ts`
- **eapi lib entry**: `backend/src/dwyeapi/__init__.py`
- **eapi test root**: `backend/tests/conftest.py`
- **Playground entry**: `frontend/playground/src/main.ts`

## File Ownership

- Component source: `frontend/eui/src/components/{name}/EName.vue` + `types.ts` + `index.ts`
- eui test files: `frontend/eui/tests/components/{name}.test.ts` and `frontend/eui/tests/composables/`
- ekit test files: `frontend/ekit/tests/{module}/{module}.test.ts`
- eapi test files: `backend/tests/test_{module}.py`
- eui theme CSS: `frontend/eui/src/theme/` (tokens.css, dark.css, index.css)
- CLI templates: `dwy-cli/templates/project/{template}/`
- Distributable AI skills: `dwy-cli/templates/ai-tools/skills/`

## CLAUDE.md

See `CLAUDE.md` for full build/test/release details, design system references, and extended conventions. This `AGENTS.md` is the condensed quick-start; `CLAUDE.md` is the exhaustive source of truth.

## [自成长] 项目规则

- 现象：目录链接迁移时出现共享副本自链，或取消选择时穿透根目录链接删除外部文件。根因：只保护了写入路径，清理入口仍按词法路径直接删除。避免：迁移、更新和取消选择共用真实路径边界检查；用 lstat 区分入口与目标，写入前排除同源自链，删除入口不能遍历其目标，并分别覆盖新增和清理测试。

- 现象：独立 wheel 的 SQLite 队列验收缺少 aiosqlite，源码测试通过但发布验收失败。根因：验收脚本复用了开发环境里的数据库驱动，独立环境只安装运行时 extra。避免：发布工作流显式安装验收所需的固定测试驱动；分别检查每个 smoke 的实际导入，不为测试数据库把驱动加入基础包运行依赖。

- 现象：通知接口新增关键字参数后，旧测试替身出现 TypeError，外层错误脱敏又把它表现为普通重试，导致并发与取消测试失真。根因：只更新真实发送器，没有同步手写协议替身。避免：扩展公开调用签名时同时检查所有真实调用方与替身，补齐具名参数，并保留实际 HTTP JSON、并发和取消恢复测试，不能只看重试次数。

- 现象：本机新 Swift 测试通过，旧 CI 出现 `freed pointer was not the last allocation`。根因：同一文案不能定位具体异步帧问题，默认异步回调与显式注入的代码生成可能不同。避免：先用真实 xctest 入口在 LLDB 取栈，对照默认/注入调用和工具链；默认平台等待直接使用平台 API。发布前预验同源旧工具链完整测试及优化路径，通过后再打不可变标签，不靠更换 sleep API 或重打旧标签排障。

- 现象：增加原始字段保留后，导入、删除恢复等次要写入口仍会丢字段，或历史无效值阻止已确认墓碑投影。根因：只覆盖普通保存路径，混用了本机待发证据与当前远端状态。避免：同步持久化改动同时核对保存、导入、冲突、删除和恢复入口；分别测试 dirty/frozen 删除与已确认远端墓碑，保留原文不能改变删除语义。
- 封装第三方 SDK 的单次发送能力时，不能只设置框架的 `retry=0`；插件内部可能另有递归或硬编码重试。检查具体发送路径，并用固定 429 响应断言实际请求次数；无法关闭内部重试的协议暂不开放，避免与外层持久队列叠加重发。
- 多包版本更新后先核对包清单、源码导入位置与 `importlib.metadata.version`；editable 安装不会自动刷新发行元数据，源码 User-Agent 已升级而已安装元数据仍旧时会出现虚假的版本断言失败。刷新对应包的 editable 安装元数据后再验证，不为陈旧环境修改源码版本或放宽断言。
- 跨分支修复多行补丁时，必须读取当前签名及紧邻的文档字符串，不能按旧分支或摘要拼接上下文；类型注解和夹在签名与返回语句之间的文档字符串会使补丁连续匹配失败。匹配失败后先核对实际上下文，再缩小到单个 hunk。
- 批量审查远端日志时，每批按单项超时和并发数计算最坏耗时，并逐项保留检查结果。把所有结果留到最后输出会在整批超时后丢失已完成的证据；先验证小批量，再扩大批次，不重复重跑整批。
- 同文件多个补丁 hunk 必须按源文件位置排序，JSON 清单改动按原数组顺序生成。否则后一个 hunk 可能无法回到前面的文本，出现“原文存在却匹配失败”；先检查顺序和上下文再重试，避免反复扩大匹配范围。
- 复用 SwiftPM Git 缓存前，不能只确认锁定 commit 存在；部分克隆可能缺少 blob，导致检出或打包失败。用 `git rev-list --objects --all --missing=print` 检查可达对象是否完整，复制后确认不通过 alternates 或本地 remote 依赖待移除的来源目录。
- uv 离线安装失败时，不能根据已有虚拟环境推断缓存齐全；缓存受索引来源、版本和平台产物影响。先固定索引并确认缺失项，再选择联网安装，避免反复重试 `--offline`。
- npm 发布工作流成功或 `latest` 更新后，包文件仍可能因分发延迟或旧 404 缓存暂不可用。先核对指定版本元数据和 `dist.tarball` 的实际下载状态，再在独立目录按精确版本安装验收；不要重复发布同版本或重打标签。下载耗时较长时使用可续查的任务，避免反复因短超时中断安装。
- 文件迁移或清理时，软链接别名可能让项目入口与全局提供者实际重合；只比较 `path.resolve` 会误判并删除唯一入口。对已存在的边界用 `realpath` 判断同源，规划和执行共用这一判断，并覆盖主目录本身与其别名的回归。
- 涉及全局配置或共享缓存的测试必须注入临时用户目录，不能只隔离项目目录；否则测试会读取或登记真实用户的共享副本，且升级刷新后出现与源码无关的断言失败。验证前检查所有同步、迁移及平台适配调用的用户目录来源。故障注入不能直接删除解析函数返回的路径，因为失败时可能回退到真实包内模板；写入、删除和清理前先断言目标仍在测试临时目录内，拒绝越界后才能验证故障行为。

- 现象：SwiftPM 测试或交叉构建反复改写 `Package.resolved`，把公开依赖的 identity 换成本机缓存名。根因：项目本地镜像配置影响解析结果。避免：验证前后检查镜像配置和锁文件差异，不把本机路径或缓存 identity 提交；运行多次构建后再检查并还原仅由验证产生的变更。
