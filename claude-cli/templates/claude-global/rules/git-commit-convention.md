# Git 提交信息规范

每次执行 `git commit` 时必须遵循以下规范。

## 格式

```
<type>(<scope>): <subject>

<body>（可选）
```

## Type 枚举

| type     | 用途                         |
|----------|------------------------------|
| feat     | 新功能                       |
| fix      | 修复 bug                     |
| refactor | 重构（不改变外部行为）       |
| chore    | 构建/依赖/配置/发版等杂务    |
| docs     | 文档变更                     |
| test     | 测试新增或修改               |
| perf     | 性能优化                     |
| style    | 代码格式调整（不影响逻辑）   |
| ci       | CI/CD 配置变更               |

## Subject 规则

- 英文，小写字母开头，不加句号
- ≤ 72 字符
- 用祈使语气：`add`、`fix`、`remove`，不用 `added`、`fixes`

## Scope 规则

- scope 可选，由各项目的 CLAUDE.md 定义枚举值
- 单模块变更带 scope：`feat(auth): add JWT refresh`
- 跨模块变更省略 scope：`chore: upgrade TypeScript to 5.x`
- 没有定义 scope 枚举的项目可省略 scope

## 提交粒度

- **一个 commit 只做一件事**——不混合 feat + fix、不混合多个不相关变更
- 跨多个 scope 的独立变更拆成多个 commit
- 判断标准：能否用一个 ≤ 72 字符的 subject 清晰描述？不能就该拆

## Body（可选）

- 空一行后写 body
- 解释 **why**（动机、背景），不复述 what（diff 能看到的不写）
- 破坏性变更加 `BREAKING CHANGE:` 前缀说明影响和迁移方式

## 提交前 Scope 检查

每次准备 `git commit` 时，检查当前项目的 CLAUDE.md 是否包含 `## Git Commit Scope` 段落：

- **有** → 按其中定义的 scope 枚举值写 commit message
- **没有** → 提交前**提醒用户**：「当前项目 CLAUDE.md 未定义 Git Commit Scope，建议添加以规范 scope 使用。需要我帮你加吗？」，然后继续提交（scope 可省略）

参考格式：
```markdown
## Git Commit Scope

本项目的 scope 枚举：`模块A` | `模块B` | `模块C`

- 单模块变更必须带 scope：`feat(模块A): add xxx`
- 跨模块变更省略 scope：`chore: upgrade xxx`
- 仅改一个模块的文件时拆成单独 commit，不混模块提交
```

## 示例

```
feat(eui): add Image component with lazy loading

fix: correct token refresh race condition

refactor(backend): extract pagination into shared utility

chore: upgrade Vite to 8.x across all packages

feat(core): add useClickOutside composable

BREAKING CHANGE example:
feat(eui)!: rename EDialog open prop to v-model:open

BREAKING CHANGE: EDialog no longer accepts `visible` prop.
Use `v-model:open` instead.
```
