

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
- Commands: `dwy` / `dwy sync`（范围 → Skills → 项目 Rules → 通用规范 → Hooks → CLI → 确认）；`dwy refresh`（更新全部模板共享 Skills；项目交互终端可选择并确认增删项目 Skills，非交互环境只刷新已有配置）；`dwy migrate`（迁移老项目入口）；`dwy upgrade`（更新到 npm 正式版 latest）；`dwy --help` / `dwy --version`。
- Skills / Rules 按分类显示 Tab；通用规范和 Hooks 默认启用，项目已有有效全局提供者时跳过对应选择且不重复写入。CLI 最后选择，Codex 默认选中，并恢复当前范围已同步的其他 CLI。Commands 停用并保留本地文件，启动时展示 dwy 品牌。
- 不存在 `dwy claude sync` / `dwy codex sync` / `dwy sync md` / `dwy skills install`（平台选择与刷新外部 skill 都在 `dwy` 交互里完成）。
- AI 模板目录为 `dwy-cli/templates/ai-tools`；优先使用显式开发覆盖或本地来源，否则检查远端 `develop`，离线使用有效缓存或随包模板。模板内容变更不必单独发布 CLI。`dwy sync` 确认后修改目标配置和所选共享内容；`dwy refresh` 先更新全部共享内容，项目入口增删仍须确认。项目已被有效全局入口完整覆盖的 Skills 禁止重复勾选。详见 `docs/cli-sync.md`。

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

## 项目经验

开发或排查前查阅 `.dwy/dwy-project-learning/lessons.md` 中与任务相关的经验，并按 `dwy-project-learning` Skill 沉淀新的可复用教训。
