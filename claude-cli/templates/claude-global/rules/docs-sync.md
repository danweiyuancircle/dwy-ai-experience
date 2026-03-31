# 文档同步规则

当代码发生变更时，必须同步更新所有关联文档。不允许只改代码不更新文档。

## 触发条件

**任何**以下目录的文件发生变更（新增/修改/删除 props、函数、模块、命令等）时，本规则生效。

## 依赖映射表

| 代码变更位置 | 必须同步更新的文档 |
|------------|-----------------|
| `frontend/eui/src/components/{name}/types.ts` | ① `claude-cli/templates/claude-global/skills/dwy-frontend-eui/SKILL.md` — 组件索引表中对应组件的「关键 Props」列 |
| `frontend/eui/src/components/{name}/E{Name}.vue` | ② `frontend/playground/src/views/{Name}Demo.vue` — 新增 DemoBlock 展示新功能 |
| `frontend/eui/src/composables/*.ts` | ① SKILL.md 的 Composables 表 |
| `frontend/eui/src/types/index.ts` | ① SKILL.md 的「通用类型」段 |
| `frontend/eui/src/components/` 新增组件目录 | ① SKILL.md 新增组件行 ② `frontend/eui/src/index.ts` 新增导出 ③ playground 新增 demo 页 + 路由 + 导航配置 + 搜索索引 |
| `frontend/core/src/{module}/index.ts` | ① `claude-cli/templates/claude-global/skills/dwy-frontend-core/SKILL.md` 对应模块段 ② `frontend/playground/src/views/core/{Module}Doc.vue` |
| `backend/src/danweiyuan_base/{module}.py` | ① `claude-cli/templates/claude-global/skills/dwy-backend-base/SKILL.md` 对应模块段 ② `frontend/playground/src/views/backend/{Module}Doc.vue` |
| `claude-cli/src/*.js` 或 `claude-cli/bin/*.js` | ① `frontend/playground/src/views/cli/CreateDwyDoc.vue` |
| `claude-cli/templates/claude-global/rules/*.md` | ① playground 的 Claude Code Rule 页面（通过 glob 自动读取，无需手动更新） |
| `claude-cli/templates/claude-global/skills/*/SKILL.md` | ① playground 的 Claude Code Skill 页面（通过 glob 自动读取，无需手动更新） |
| 任何包的模块结构变更（新增/删除/重命名模块） | ① `CLAUDE.md` 项目根目录的 Architecture 段 |

## 检查清单

完成代码变更后，逐项检查：

### 1. SKILL.md 是否需要更新？

```
问自己：这次改动是否新增/修改/删除了组件 props、函数签名、导出类型？
  → 是：更新对应 SKILL.md 的组件索引表或模块文档段
  → 否：跳过
```

### 2. Playground demo 是否需要更新？

```
问自己：这次改动是否新增了用户可感知的功能（新 prop、新组件、新行为）？
  → 是：在对应 Demo 页面新增 DemoBlock 演示
  → 否：跳过
```

### 3. Playground 导航/搜索是否需要更新？

```
问自己：是否新增了组件或页面？
  → 是：更新 nav-config.ts（侧边栏）+ search-index.ts（搜索索引）+ router.ts（路由）
  → 否：跳过
```

### 4. CLAUDE.md 是否需要更新？

```
问自己：是否变更了模块结构（新增/删除/重命名包或模块）、构建命令、测试命令？
  → 是：更新 CLAUDE.md 对应段落
  → 否：跳过（props 级别的变更不需要更新 CLAUDE.md）
```

### 5. 版本号是否需要更新？

```
问自己：这次改动是否对外可见（影响使用者）？
  → 是：更新 package.json / pyproject.toml 版本号
  → 否：跳过
```

## 自动同步 vs 手动同步

| 文档 | 同步方式 | 说明 |
|------|---------|------|
| playground Claude Code 页面 (rules/skills/hooks) | **自动** | 通过 `import.meta.glob` 构建时读取源文件，代码变更后自动同步 |
| 其他所有文档 | **手动** | 需要在代码变更的同一次 commit 中更新 |

## 提交规范

- 文档更新应与代码变更在**同一个 commit** 中，不要分开提交
- 如果遗漏了文档更新，在发现后立即补一个 `docs: sync xxx` 的 commit
- commit message 中用 `docs:` 前缀标记纯文档更新，用 `feat:` / `fix:` 标记代码+文档混合提交

## 违规场景示例

```
❌ 给 ESelect 加了 filterable prop，但没更新 SKILL.md 的 ESelect 行
❌ 新增了 EColorWheel 组件，但没加到 playground 路由和导航
❌ 给 backend 加了新模块 logging.py，但没更新 CLAUDE.md 的 Architecture 段
❌ 修改了 dwy sync 命令的行为，但没更新 CreateDwyDoc.vue
✅ 给 ETable 加了 virtual prop，同时更新了 SKILL.md、TableDemo.vue、search-index.ts
```
