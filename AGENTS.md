<!-- DWY-BASELINE:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->

所有回答必须使用中文。

## 输出完整性要求

- **文件路径**：写出从仓库根开始的完整相对路径（如 `frontend/eui/src/components/input/EInput.vue`）。不要只写文件名。不要把本机绝对路径写进规则、代码、文档或提交说明。
- **服务地址**：写出完整 URL，包含协议、主机、端口和路径（如 `http://localhost:8000/api/users`）。
- **数据库连接串**：说明它来自哪个环境变量或配置项。回复、日志、示例里不写密码和 token。需要示意时用占位符，如 `postgresql+asyncpg://USER:PASSWORD@localhost:5432/DBNAME`。

## 代码注释

- 导出的类、函数、组件 props 写清用途和调用约束。
- 不看代码就看不出的约束要写：线程、生命周期、为什么不用更直的写法。
- 私有方法、getter、一行就能看懂的语句不写注释。
- 注释写「为什么」和「约束」，不复述代码在做什么。

## 图标规范

- 图标优先使用成熟稳定的图标库，不使用 emoji 作为功能性图标。
- 优先选择项目已有成熟依赖；无可用依赖时再补充稳定方案。

## 发布与打包基础准则

- PyPI 与 npm 的发布必须走 GitHub Actions，使用 OIDC 完成鉴权，禁止使用长期静态发布凭据。
- 多平台打包必须走 GitHub Actions 工作流执行，不使用本地手工打包作为唯一流程。

## 减少常见 LLM 编码错误的行为指南

与项目特定指令合并使用。

权衡：这些指南偏向谨慎而非速度。对于琐碎任务，自行判断。

### 1. 先思考再编码

不要假设。不要隐藏困惑。把权衡摊开。

在实现之前：
- 明确陈述你的假设。如果不确定，就问。
- 如果存在多种解读，提出来——不要默默选择。
- 如果有更简单的方案，说出来。在必要时提出异议。
- 如果有什么不清晰，停下来。说出困惑是什么。然后提问。

### 2. 简单优先

解决问题的最小代码。没有推测性代码。

- 不做需求之外的功能。
- 不为一次性使用的代码做抽象。
- 不做未被要求的"灵活性"或"可配置性"。
- 不为不可能发生的场景做错误处理。
- 如果你写了 200 行但可以写成 50 行，重写它。
- 问自己："一个资深工程师会说这过于复杂吗？"如果是，简化。

### 写代码前走决策阶梯

写任何新代码前，从上往下逐级问，命中即停：

1. 这任务真需要存在吗？（YAGNI——能不做就不做）
2. 代码库里已有现成的吗？
3. 标准库覆盖吗？
4. 平台 / 框架原生特性有吗？
5. 已安装的依赖能做吗？
6. 能一行解决吗？
7. 以上都不行 → 才写最小代码。

刻意的简化用注释标注：跳过了什么、何时该加回。
红线——以下永不简化掉：输入校验、错误处理、安全、可访问性。先理解问题，再谈优化。

### 3. 精准改动

只动必须动的代码。只清理自己造成的混乱。

在编辑现有代码时：
- 不要"改进"相邻的代码、注释或格式。
- 不要重构没有问题的东西。
- 匹配现有的风格，即使你会用不同的写法。
- 如果发现不相关的死代码，提一下——但不要删除。

当你的改动产生孤儿代码时：
- 移除你的改动导致的未使用的 import/变量/函数。
- 除非被要求，不要移除已有的死代码。

检验标准：每一行改动的代码都应能直接追溯到用户的需求。

### 4. 目标驱动执行

定义成功标准。循环直到验证通过。

将任务转化为可验证的目标：
- "添加校验" → "编写无效输入的测试，然后让它们通过"
- "修复 bug" → "编写重现 bug 的测试，然后让它通过"
- "重构 X" → "确保测试在重构前后都通过"

对于多步骤任务，陈述一个简要计划：
1. [步骤] → 验证：[检查项]
2. [步骤] → 验证：[检查项]
3. [步骤] → 验证：[检查项]

强成功标准让你能独立循环。弱标准（"让它工作"）需要不断澄清。

这些指南在生效的标志是：diff 中不必要的改动变少，因过度复杂而重写的情况减少，澄清性问题出现在实现之前而非错误之后。

## 输出精简规则

输出保持精简，去掉冗余，保留技术精确性。句子要能读通。

### 核心规则

- **去掉口头填充**：不用「你好 / 请 / 谢谢」。不用「我认为」这类没有信息的空话。
- **不确定就直说**：哪一点不确定，直接写出来。可以用「可能 / 也许」。
- 「了 / 的 / 吗」该用就用。不要为了短把中文写成残句。
- **短优先**：能用短词就不用长词，能用一句话就不用两句话。
- **技术术语精确**：变量名、函数名、错误信息、代码块保持原样，不缩写。
- **代码块完整**：代码必须完整可运行，不受精简规则影响。

### 例外场景（写清楚，不省略风险）

以下场景必须清晰明确：
- 安全警告和风险提示
- 不可逆操作确认（删除、强制推送等）
- 需要用户决策的复杂多步骤流程
- 用户明确要求详细解释时

## 新增依赖才做开源选型

修 bug、改已有功能、用仓库里已有的依赖或标准库，直接做。不要为了选型停下来。

只有这次改动要**新增运行时依赖**（新的 npm / PyPI / Gradle / SPM 等包）时才走下面的流程：

1. 先看项目已有依赖和标准库能不能做。能做就用已有的。
2. 不能做：列出 3 到 5 个当前技术栈里的成熟开源方案，写明维护情况、许可证、是否和已有依赖重复，给出推荐，等用户选定再加依赖。
3. 候选不足 3 个：说明找过什么，问用户是否允许自研。不要为了凑数改去列别的语言生态。

禁止手写已经有成熟库、并且项目允许引入该库的能力。选型优先级：项目已在用的依赖 > 当前生态的主流库 > 小众但匹配的库。

## 代码简约原则

只写**必要的逻辑**，不写"以防万一"的冗余代码。信任内部代码和框架保证，只在系统**外边界**（用户输入、外部 API、文件 / 网络读入）做校验。

### 禁止的冗余模式

- **多余 fallback**：值已有明确来源时，不再 `value or default` / `value ?? default`
- **多余类型转换**：上游已是目标类型时，不再 `int(x)` / `Number(x)` / `String(x)`
- **多余 else**：上面已 return，下面不再写 else 分支（用 early return）
- **多余默认值**：调用方都传值时，不写形参默认值 + 空值检查
- **多余异常兜底**：`try { ... } catch { /* swallow */ }` 掩盖 bug；只捕获**预期**的具体异常，其余让它自然抛出
- **多余空集合检查**：能直接 `for ... in collection` 时，不要 `if len(x) > 0` 再循环

### 判断标准

写每一行防御代码前问自己：**这个情况在当前上下文真的会发生吗？**

- 会 → 写防御，注释说明触发条件
- 不会 → 不写，信任上游
- 不确定 → 查调用链确认，不要"以防万一"

| 位置 | 是否校验 |
|---|---|
| 用户输入、外部 API 响应、文件 / 网络读入 | 必须校验 |
| 内部模块调用（已有类型签名） | 信任，不重复校验 |

## 团队基础库缺口回流

自己的基础库 = 用户自己开发的库。AI **读当前项目上下文**识别，禁止把库名写死进本规则。社区库不是。读不出 → 当没有。已经在该基础库源码上改 → 本节不适用。

落点**按当场情况动态判断**，不要写死「一律改业务」或「一律改基础库」。结合本轮时间与难度、改基础库的成本、复用收益、是不是一次性业务，选更合适的一侧动手。

本轮落在业务侧、且能力其实通用时，**事后**再总结提问：

```
【基础库抽取候选】
- 识别到的基础库：…（读到的依据）
- 本轮业务侧做了：…
- 建议抽到：哪个库的哪个模块
- 本轮为何没直接改基础库：…
要不要抽？抽了之后这处业务补丁可以删。
```

用户说抽才回头改基础库；说不抽 → 停。

## 自成长项目规则（project-rules）

写项目要自成长：同一类问题反复踩坑，主动沉淀成可复用规则，下次自动生效，不靠人事后总结。

- **触发**：写代码 / 排查问题时，同一类问题踩坑 **≥2 次**（重复的报错根因、踩同一个坑、被反复纠正同一处写法）。
- **动作**：把教训沉淀成一条可复用规则（写清「现象 / 根因 / 怎么避免」），追加到 `project-rules.md`；已有同类规则补充进去，不重复立条。
- **落盘位置**（按当前工具自动选）：
  - **Claude Code 与 Grok** → 项目 `.claude/rules/project-rules.md`（两边都会加载这个目录）。
  - **Codex** → 项目根 `AGENTS.md` 里 DWY-RULES 托管块之外的 `## [自成长] 项目规则`。托管块会被 `dwy sync` 整块覆盖，自成长内容必须写在块外。
- **方式**：自动沉淀，事后输出一行告知「已沉淀 <规则> 到 project-rules」，不打断当前任务、不逐条问用户。
- **边界**：只沉淀**可复用、跨任务**的教训；一次性 / 本任务特有的问题不立规则，避免噪音堆积。
- **不要**在基线正文里写 DWY-BASELINE 或 DWY-RULES 的 HTML 注释标记。同步用这两个标记切块，写进正文会把托管块截断。

<!-- DWY-BASELINE:END -->

# AGENTS.md

Compact instructions for OpenCode sessions working in `dwy-shared`.

## Monorepo Layout

| Directory | Package Manager | Package | Type |
|-----------|-----------------|---------|------|
| `frontend/eui/` | pnpm | `@dwydev/eui` | Vue 3 component library (~95 components) |
| `frontend/ekit/` | pnpm | `@dwydev/ekit` | Vue 3 utility library |
| `frontend/playground/` | pnpm | — | Docs portal (Vite SPA) |
| `dwy-cli/` | pnpm | `create-dwy` | CLI scaffold + Claude config sync |
| `backend/` | uv | `dwyeapi` | FastAPI infrastructure (Python 3.11+) |

`pnpm-workspace.yaml` only covers `frontend/*` and `dwy-cli`. Python backend is managed separately by uv and **not** in the pnpm workspace.

**Package manager gotcha**: root `package.json` has a stale `packageManager: yarn@1.22.22` field. The repo actually uses **pnpm** (lockfile is `pnpm-lock.yaml`). Always use `pnpm`, never `yarn`.

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

### Publish order

When releasing multiple packages: **ekit → eui → eapi → cli**

```bash
# 打 tag 后 git push origin <tag>，由 GitHub Actions OIDC 发布
# @dwydev/ekit@x.y.z  @dwydev/eui@x.y.z  dwyeapi@x.y.z  create-dwy@x.y.z
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
- 已实现入口必须出现在 `dwy --help`；禁止把可用命令藏成「隐藏命令」。
- Commands: `dwy` / `dwy sync`（Skills → Rules → 全局／项目 → 平台 → 确认）；`dwy upgrade`（自升级到 npm latest）；`dwy --help` / `dwy --version`。
- 项目同步依次选择 Skills / Rules，各步按实际分类显示 Tab，无回退或重选；Hooks 自动同步到支持的平台。Commands 停用并保留本地文件，启动时展示 dwy 品牌。
- 不存在 `dwy claude sync` / `dwy codex sync` / `dwy sync md` / `dwy skills install`（平台选择与刷新外部 skill 都在 `dwy` 交互里完成）。
- Templates are bundled with the `create-dwy` package under `dwy-cli/templates`; `dwy` 运行时不再读取或刷新外部缓存仓库。

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
| `docs/eui-integration-guide.md` | `dwy-cli/templates/claude-global/skills/dwy-eui/references/eui-integration-guide.md` |
| `docs/eui-design-guide.md` | `dwy-cli/templates/claude-global/skills/dwy-eui/references/eui-design-guide.md` |
| `docs/eui-landing-design-guide.md` | `dwy-cli/templates/claude-global/skills/dwy-eui/references/eui-landing-design-guide.md` |
| `docs/tasks-integration-guide.md` | `dwy-cli/templates/claude-global/skills/dwy-eapi/references/tasks-integration-guide.md` |

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
- Global claude skills: `dwy-cli/templates/claude-global/skills/`

## CLAUDE.md

See `/Users/chances/WebstormProjects/dwy-shared/CLAUDE.md` for full build/test/release details, design system references, and extended conventions. This `AGENTS.md` is the condensed quick-start; `CLAUDE.md` is the exhaustive source of truth.
