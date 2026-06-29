---
description: TDD 开发流程(新功能/bug 修复/重构的测试先行与回归策略)与测试-源码分隔(测试工程独立 tests/ 目录、镜像源码结构、各栈目录约定)
---

# TDD 开发规则

所有代码变更必须遵循测试驱动开发流程。测试不是事后补的，是开发的起点。

## 开发流程

### 新功能

1. 先写测试 — 定义预期行为，测试此时应失败
2. 再写实现 — 用最简代码让测试通过
3. 重构优化 — 在测试保护下重构，确保始终通过

### Bug 修复

1. 先写复现测试 — 写一个能暴露 bug 的测试用例，确认它失败
2. 再修代码 — 修复 bug，确认测试通过
3. 跑回归 — 确认没有引入新问题

### 重构

1. 先跑现有测试 — 确认当前全部通过
2. 再重构 — 修改代码
3. 再跑测试 — 确认行为没变

## 测试与源码分隔（硬约束）

测试工程必须与源码分隔，不混在一起。

### 核心规则

- 测试代码**禁止**与源码同目录混放；测试集中在项目根 / 包根的独立 `tests/` 目录。
- `tests/` **镜像源码结构**，测试文件与被测源码一一对应、可反查：
  - `src/foo/bar.ts` → `tests/foo/bar.test.ts`
  - `src/services/user.py` → `tests/test_user.py`
- 源码目录（`src/`）保持纯净，**只放产品代码**；打包 / 发布产物天然不含测试，CI 用一个目录通配即可圈定全部测试。
- 测试用的 fixture / mock 数据 / 测试工具，放 `tests/` 内（如 `tests/fixtures/`、`tests/conftest.py`），不散落进源码目录。

### 为什么（约束的根因）

测试混入源码目录会引发一连串问题，分隔后一次性收口：

- **被打包进发布产物**：测试随源码一起发到 npm / PyPI，污染产物、撑大体积。
- **source map / 内部细节泄露**：测试常含内部实现假设、mock 的真实数据，泄露到产物有安全风险。
- **覆盖率 / 构建统计污染**：测试文件被计入源码统计，覆盖率、行数失真。
- **CI 难圈定范围**：源码与测试交织，CI 无法用一条目录规则排除测试。
- **AI / 工具难定位**：找不到「源码↔测试」对应关系，反复把测试误写进 `src/`。

### 各栈目录与命令速查表

| 栈 | 测试目录 | 命名约定 | 运行命令 |
|----|---------|---------|---------|
| Vue / Vitest | `tests/` 镜像 `src/` | `*.test.ts` | `pnpm vitest run [路径]` |
| Python / pytest | `tests/` | `test_*.py` | `pytest tests/ -v` / `uv run pytest` |
| Android | `src/test/`（单元）+ `src/androidTest/`（仪器） | `*Test.kt` | `./gradlew test` / `./gradlew connectedAndroidTest` |
| Node / CLI | `tests/` 镜像 `src/` | `*.test.ts` | 对应 runner（vitest / jest） |

注：Android 的 `src/test` / `src/androidTest` 是 Gradle 生态**强约定**的独立测试源集（test source set），与 `src/main` 源码完全分隔，符合本规范"测试与源码分隔"理念，按其生态默认即可，**属合规分隔**，不视为"测试写进 src"。

**通用准则（表中未列的栈）**：遵循「独立测试目录 + 镜像源码结构 + 该生态主流 runner 约定」三条原则自行判断，不硬套上表布局。

## 回归测试

### 开发中：只跑受影响的测试

每次代码改动后，只运行受影响的测试文件，提高开发效率：

```bash
# 后端：只跑改动涉及的测试文件
uv run pytest tests/test_factor.py -v          # 改了 factor 相关代码
uv run pytest tests/test_tick.py tests/test_upload.py -v  # 改了多个模块

# 前端：只跑对应目录
pnpm vitest run tests/stores/               # 改了 store
pnpm vitest run tests/utils/format.test.ts   # 改了单个工具函数
```

判断"受影响的测试"的规则：
- 改了 `services/xxx.py` → 跑 `tests/test_xxx.py`
- 改了 `routers/xxx.py` → 跑 `tests/test_xxx.py`
- 改了 `schemas/` 或 `models/` → 跑引用了它们的测试
- 改了 `conftest.py` 或公共依赖 → 全量回归
- 不确定影响范围 → 全量回归

### 提交前：跑受影响的测试即可

提交前确保受影响的测试通过即可，不要求全量回归。全量测试留给 CI 或手动触发。

## TEST_CASES.md

每个包/项目维护一份 `TEST_CASES.md`，记录所有测试用例的清单。**`TEST_CASES.md` 跟测试目录走，不放项目根**：

- 有 `tests/` → 放 `tests/TEST_CASES.md`
- 测试源集分散（如 Android `src/test/`）→ 放对应测试根（`src/test/TEST_CASES.md`），与该模块测试同处
- 理念：测试清单是测试工程的一部分，归测试目录，与「测试与源码分隔」一致

内容要求：

- 人类可读，方便审查和手动编辑
- 新增/修改/删除功能时必须同步更新
- 内容与实际测试文件保持一致
- 作为版本回测基准

## 禁止事项

- **禁止**不写测试就提交功能代码
- **禁止**写完代码再补测试（先测试后代码）
- **禁止**测试不通过就提交
- **禁止** TEST_CASES.md 与实际测试不同步
- **禁止**测试文件写进 `src/` 源码目录（Android `src/test`、`src/androidTest` 例外，是 Gradle 标准测试源集）
- **禁止**测试目录结构与源码脱节（找不到「源码↔测试」对应关系）
- **禁止**把测试 fixture / mock 数据散落进源码目录
