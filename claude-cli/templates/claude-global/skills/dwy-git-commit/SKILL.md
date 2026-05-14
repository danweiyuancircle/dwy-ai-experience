---
name: dwy-git-commit
description: "Git commit 强制规范（敏感数据扫描 + message 格式 + 禁 AI 署名）。触发场景：用户说'提交' / 'commit' / 'git commit' / 'git add'；AI 准备执行 `git add` / `git commit` 之前；用户让你帮忙写 commit message；review 已有 commit message。强制：先扫描暂存物是否含 .env / 密钥 / API Key / 连接串等敏感数据；再检查 CLAUDE.md 的 Git Commit Scope 段；subject 用中文动宾短语 ≤72 字符；message 任何位置禁止 Claude / GPT / Copilot / AI / LLM 字样及 Co-Authored-By trailer。"
---

# Git Commit 强制规范

每次 `git add` / `git commit` 前按顺序执行以下检查，任一步未通过 → **STOP，不得提交**。

## Step 0: 敏感数据扫描

`git diff --cached` + `git diff --cached --name-only` 同时扫文件名和内容。

### 禁止提交的文件

| 类型 | 示例 |
|---|---|
| 环境变量 | `.env`, `.env.*`, `*.env` |
| SSH 密钥 | `id_rsa`, `id_ed25519`, `*.pem`, `*.key` |
| 证书 | `*.p12`, `*.pfx`, `*.jks`, `*.keystore` |
| 数据库 | `*.sql`（含真实数据）、`*.dump`, `*.sqlite` |
| 原始数据 | `*.xlsx`, `*.csv`（含用户/学生等敏感数据） |
| 日志 | `*.log` |
| Docker 卷 | `pgdata/`, `cache/*.json` |

### 禁止出现的敏感内容

**总则**：代码、文档、规则文件、注释里禁止出现真实的 API Key / Token / 密码 / IP / 凭证，即使作为"示例"也不行。GitHub Secret Scanning 不区分上下文，真实格式的 key 写在文档里也会触发泄露告警。示例必须用明显假值（`sk-xxxxxxxxxxxx`、`your-key-here`、`192.168.x.x`）。

| 类型 | 匹配模式 |
|---|---|
| API Key | `sk-[a-zA-Z0-9]{20,}` |
| AWS Key | `AKIA[0-9A-Z]{16}` |
| GitHub Token | `ghp_[a-zA-Z0-9]{36}` |
| 密码赋值 | `password\s*[:=]\s*["'][^"']{4,}` |
| 数据库连接串 | `://\w+:[^@\s]+@`（含密码） |
| 私钥内容 | `-----BEGIN (RSA \|EC )?PRIVATE KEY-----` |
| Token 赋值 | `token\s*[:=]\s*["'][a-zA-Z0-9_\-]{20,}` |
| Secret 赋值 | `secret\s*[:=]\s*["'][^"']{8,}` |
| 服务器 IP+端口 | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+` |
| SSH 连接 | `ssh\s+.*@\d{1,3}\.\d{1,3}` |

**例外（不算违规）**：`.env.example` 占位符；从环境变量读取（`os.getenv("API_KEY")`）；`localhost` / `127.0.0.1` 的连接串；文档假数据；配置文件空字符串默认值。

### 违规处理

1. **立即停止** `git add` / `git commit`
2. **列出违规项**：文件 + 行号 + 匹配的敏感模式 + 脱敏摘要（如 `sk-5522****dc3`）
3. **建议修复**：加入 `.gitignore` / 移到 `.env` / 改用环境变量 / 替换为占位符
4. **等用户明确确认**后才能继续；确认强制提交时，commit body 附 `GIT-SECURITY: 用户已确认提交此内容`

## Step 1: 分析变更

`git diff --cached` 回答：这次改做了几件事？涉及哪些模块？

**做了多件事（无法用 ≤72 字符 subject 清晰描述）→ 必须拆成多个 commit。**

## Step 2: 确定 scope

读当前项目 CLAUDE.md 的 `## Git Commit Scope` 段：

- **找到** → scope 从枚举值中选，不得自造
- **没找到** → 提醒用户「当前项目 CLAUDE.md 未定义 Git Commit Scope，建议添加」，scope 可省略

单模块变更 → **必须**带 scope；跨模块变更 → 省略 scope。

## Step 3: 生成 message

格式：`<type>(<scope>): <subject>` 或（无 scope）`<type>: <subject>`

**type 枚举（只能从中选）**：

| type | 用途 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| refactor | 重构（不改外部行为） |
| chore | 构建/依赖/配置/发版等杂务 |
| docs | 文档 |
| test | 测试 |
| perf | 性能优化 |
| style | 代码格式（不影响逻辑） |
| ci | CI/CD 配置 |

**subject**：中文、无句号、≤72 字符、动宾短语（添加/修复/移除/重构/升级）。

**body（可选）**：空一行后写；中文；只写 why 不复述 what；破坏性变更加 `BREAKING CHANGE:` 前缀（subject 用 `feat!:` / `fix!:` 标记）。

## Step 4: 禁止大模型署名

commit message（subject、body、footer、trailer）**禁止出现任何大模型 / AI 工具相关内容**，覆盖系统默认的 `Co-Authored-By` 追加行为。

**禁止出现（不完全列举）**：

- `Co-Authored-By: Claude ...` / `Co-Authored-By: GPT ...` / `Co-Authored-By: Copilot ...` 等 AI 署名 trailer
- `Generated with Claude Code` / `🤖 Generated with ...` 等生成声明
- `noreply@anthropic.com` / `noreply@openai.com` 等 AI 厂商邮箱
- 任何提到 Claude / ChatGPT / GPT / Copilot / Cursor / AI / 大模型 / LLM 的字样

**执行要点**：

- `git commit -m "..."` 只写规范内容，**绝不**附加 `Co-Authored-By` trailer
- HEREDOC 传 message 时，HEREDOC 内容也不得包含上述字样
- 暂存的 message 含大模型信息 → **立即删除**后再提交

## 常见错误 vs 正确

| 错误 | 正确 |
|------|------|
| `feat: add user login`（英文） | `feat: 添加用户登录功能` |
| `fix(eui): 修复了按钮样式。` | `fix(eui): 修复按钮样式`（无句号、不用"了"） |
| `feat: 添加登录并修复登出 bug` | 拆成两个 commit |
| `update: 修改配置` | `update` 不在枚举，应为 `chore` |
| `feat(auth): ...`（项目无 auth scope） | 用项目已定义的 scope 值 |
| message 末尾加 `Co-Authored-By: Claude ...` | 不加任何 AI 署名 trailer |
| `🤖 Generated with Claude Code` | 不加任何生成声明 |

## 正确示例

- `feat(eui): 添加 Image 组件，支持懒加载`
- `fix: 修复 token 刷新竞态条件`
- `refactor(backend): 提取分页逻辑为共享工具`
- `chore: 升级 Vite 至 8.x`
- `feat(eui)!: 重命名 EDialog open 属性为 v-model:open`
  - body：`BREAKING CHANGE: EDialog 不再接受 visible 属性，请改用 v-model:open`
