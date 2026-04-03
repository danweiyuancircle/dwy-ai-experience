# Git Commit 强制规范

**每次 `git commit` 前必须完整执行以下检查流程，不可跳过任何步骤。**

## 提交前强制检查流程

执行 `git commit` 前，按顺序完成以下 4 步。任何一步未通过则 **STOP，不得提交**。

### Step 1: 分析变更内容

运行 `git diff --cached` 查看暂存区，回答以下问题：

- 这次变更做了几件事？
- 涉及哪些模块/目录？

**如果做了多件事** → STOP，必须拆成多个 commit。判断标准：能否用一个 ≤ 72 字符的 subject 清晰描述？不能就必须拆。

### Step 2: 确定 scope

读取当前项目 CLAUDE.md，查找 `## Git Commit Scope` 段落：

- **找到了** → scope 必须从其中定义的枚举值中选取，不得自造
- **没找到** → 提醒用户：「当前项目 CLAUDE.md 未定义 Git Commit Scope，建议添加。需要我帮你加吗？」，然后 scope 可省略

scope 使用规则：
- 变更仅涉及单个模块 → **必须**带 scope
- 变更跨多个模块 → 省略 scope

### Step 3: 生成 commit message

格式必须严格匹配：

```
<type>(<scope>): <subject>
```

或（无 scope 时）：

```
<type>: <subject>
```

**type 只能从以下枚举中选取：**

| type | 用途 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| refactor | 重构（不改变外部行为） |
| chore | 构建/依赖/配置/发版等杂务 |
| docs | 文档变更 |
| test | 测试新增或修改 |
| perf | 性能优化 |
| style | 代码格式调整（不影响逻辑） |
| ci | CI/CD 配置变更 |

**subject 强制要求：**

- **中文**描述
- 不加句号
- ≤ 72 字符
- 用简洁的动宾短语：`添加`、`修复`、`移除`、`重构`、`升级`

**body（可选）：**

- 空一行后写
- 中文，只写 why（动机、背景），不复述 what
- 破坏性变更加 `BREAKING CHANGE:` 前缀

### Step 4: 自检验证

生成 commit message 后，逐条验证：

- [ ] type 在枚举表中？
- [ ] scope 符合项目 CLAUDE.md 定义（或正确省略）？
- [ ] subject 是中文、无句号、≤ 72 字符、简洁动宾短语？
- [ ] 一个 commit 只做一件事，没有混合不同 type 的变更？
- [ ] 没有混合不同 scope 的独立变更？

**全部通过 → 执行 commit。任何一条未通过 → 修正后重新验证。**

## 常见错误（必须避免）

| 错误 | 正确 |
|------|------|
| `feat: add user login`（英文） | `feat: 添加用户登录功能`（中文） |
| `fix(eui): 修复了按钮样式。` | `fix(eui): 修复按钮样式`（无句号、不用「了」） |
| `feat: 添加登录功能并修复登出 bug` | 拆成两个 commit |
| `update: 修改配置` | `update` 不在 type 枚举中，应为 `chore` |
| `feat(auth): 添加 JWT 刷新`（项目 scope 枚举无 auth） | 使用项目定义的 scope 值 |

## 正确示例

```
feat(eui): 添加 Image 组件，支持懒加载

fix: 修复 token 刷新竞态条件

refactor(backend): 提取分页逻辑为共享工具

chore: 升级 Vite 至 8.x

feat(eui)!: 重命名 EDialog open 属性为 v-model:open

BREAKING CHANGE: EDialog 不再接受 `visible` 属性，请改用 `v-model:open`。
```
