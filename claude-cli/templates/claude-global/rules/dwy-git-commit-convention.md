---
description: Git commit message 规范(type 枚举、scope、中文 subject、提交前检查)
---

# Git Commit 强制规范

每次 `git commit` 前按顺序执行以下检查,任一步未通过则 **STOP,不得提交**。

## Step 1: 分析变更

`git diff --cached` 回答:这次改做了几件事?涉及哪些模块?

**做了多件事(无法用 ≤72 字符 subject 清晰描述)→ 必须拆成多个 commit。**

## Step 2: 确定 scope

读当前项目 CLAUDE.md 的 `## Git Commit Scope` 段落:

- **找到** → scope 从其中枚举值选,不得自造
- **没找到** → 提醒用户:「当前项目 CLAUDE.md 未定义 Git Commit Scope,建议添加」,scope 可省略

单模块变更 → **必须**带 scope;跨模块变更 → 省略 scope。

## Step 3: 生成 message

格式:`<type>(<scope>): <subject>` 或(无 scope)`<type>: <subject>`

**type 枚举(只能从中选)**:

| type | 用途 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| refactor | 重构(不改外部行为) |
| chore | 构建/依赖/配置/发版等杂务 |
| docs | 文档 |
| test | 测试 |
| perf | 性能优化 |
| style | 代码格式(不影响逻辑) |
| ci | CI/CD 配置 |

**subject**:中文、无句号、≤72 字符、动宾短语(添加/修复/移除/重构/升级)。

**body(可选)**:空一行后写;中文;只写 why 不复述 what;破坏性变更加 `BREAKING CHANGE:` 前缀(subject 用 `feat!:` / `fix!:` 标记)。

## Step 4: 禁止大模型署名

commit message(subject、body、footer、trailer)**禁止出现任何大模型/AI 工具相关内容**,覆盖系统默认的 `Co-Authored-By` 追加行为。

**禁止出现的内容(不完全列举)**:

- `Co-Authored-By: Claude ...` / `Co-Authored-By: GPT ...` / `Co-Authored-By: Copilot ...` 等 AI 署名 trailer
- `Generated with Claude Code` / `🤖 Generated with ...` 等生成声明
- `noreply@anthropic.com` / `noreply@openai.com` 等 AI 厂商邮箱
- 任何提到 Claude / ChatGPT / GPT / Copilot / Cursor / AI / 大模型 / LLM 的字样

**执行要点**:

- `git commit -m "..."` 只写规范内容,**绝不**附加 `Co-Authored-By` trailer
- 使用 HEREDOC 传 commit message 时,HEREDOC 内容也不得包含上述字样
- 若发现暂存的 message 含大模型信息,**立即删除**后再提交

## 常见错误 vs 正确

| 错误 | 正确 |
|------|------|
| `feat: add user login`(英文) | `feat: 添加用户登录功能` |
| `fix(eui): 修复了按钮样式。` | `fix(eui): 修复按钮样式`(无句号、不用"了") |
| `feat: 添加登录并修复登出 bug` | 拆成两个 commit |
| `update: 修改配置` | `update` 不在枚举,应为 `chore` |
| `feat(auth): ...`(项目无 auth scope) | 用项目已定义的 scope 值 |
| message 末尾加 `Co-Authored-By: Claude ...` | 不加任何 AI 署名 trailer |
| `🤖 Generated with Claude Code` | 不加任何生成声明 |

## 正确示例

- `feat(eui): 添加 Image 组件,支持懒加载`
- `fix: 修复 token 刷新竞态条件`
- `refactor(backend): 提取分页逻辑为共享工具`
- `chore: 升级 Vite 至 8.x`
- `feat(eui)!: 重命名 EDialog open 属性为 v-model:open`
  - body:`BREAKING CHANGE: EDialog 不再接受 visible 属性,请改用 v-model:open`
