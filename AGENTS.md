# AGENTS.md

Compact instructions for OpenCode sessions working in `dwy-shared`.

## Monorepo Layout

| Directory | Package Manager | Package | Type |
|-----------|-----------------|---------|------|
| `frontend/eui/` | pnpm | `@dwydev/eui` | Vue 3 component library (~95 components) |
| `frontend/ekit/` | pnpm | `@dwydev/ekit` | Vue 3 utility library |
| `frontend/playground/` | pnpm | — | Docs portal (Vite SPA) |
| `claude-cli/` | pnpm | `create-dwy` | CLI scaffold + Claude config sync |
| `backend/` | uv | `dwyeapi` | FastAPI infrastructure (Python 3.11+) |

`pnpm-workspace.yaml` only covers `frontend/*` and `claude-cli`. Python backend is managed separately by uv and **not** in the pnpm workspace.

**Package manager gotcha**: root `package.json` has a stale `packageManager: yarn@1.22.22` field. The repo actually uses **pnpm** (lockfile is `pnpm-lock.yaml`). Always use `pnpm`, never `yarn`.

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
cd frontend/eui && pnpm vitest run src/components/button   # single component
cd frontend/eui && pnpm vitest run src/utils/cn.test.ts    # single file

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

### Publish order

When releasing multiple packages: **ekit → eui → eapi → cli**

```bash
pnpm build:eui && pnpm publish:eui
pnpm build:ekit && pnpm publish:ekit
source .key && pnpm publish:eapi     # PyPI token in .key (gitignored)
pnpm publish:cli
```

Tag format: `@dwydev/eui@1.3.0`, `create-dwy@0.6.0`, etc.

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
- Commands: `dwy create [name]`, `dwy sync claude`, `dwy sync project-claude`.
- Templates cached in `~/.dwy/cache/dwy/`, pulled from Gitee.

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

When these docs change, sync to the claude-cli template paths:

| Source | Target sync path |
|--------|------------------|
| `docs/eui-integration-guide.md` | `claude-cli/templates/claude-global/skills/dwy-eui/references/eui-integration-guide.md` |
| `docs/eui-design-guide.md` | `claude-cli/templates/claude-global/skills/dwy-eui/references/eui-design-guide.md` |
| `docs/eui-landing-design-guide.md` | `claude-cli/templates/claude-global/skills/dwy-eui/references/eui-landing-design-guide.md` |
| `docs/tasks-integration-guide.md` | `claude-cli/templates/claude-global/skills/dwy-eapi/references/tasks-integration-guide.md` |

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
- CLI templates: `claude-cli/templates/project/{template}/`
- Global claude skills: `claude-cli/templates/claude-global/skills/`

## CLAUDE.md

See `/Users/chances/WebstormProjects/dwy-shared/CLAUDE.md` for full build/test/release details, design system references, and extended conventions. This `AGENTS.md` is the condensed quick-start; `CLAUDE.md` is the exhaustive source of truth.
