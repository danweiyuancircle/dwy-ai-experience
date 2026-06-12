---
description: git commit message 安全写法(防反引号被 shell 命令替换误执行)
---

# git commit 安全写法

## 核心风险

AI 生成的 commit message 爱用 Markdown 风格反引号包代码标识符。经 shell 执行 `git commit -m "..."` 时，**双引号内**的反引号会被当成命令替换实际执行：

```bash
# 危险：`bun install` 被 shell 当成 $(bun install) 执行
git commit -m "fix: support `bun install` on windows"
```

shell 实际跑了 `bun install`，把输出塞进 message，甚至误执行破坏性命令导致丢代码。`$(...)` 同理。

## 强制规则

commit message 含反引号 `` ` `` / `$(...)` / 多行 / emoji 等特殊字符时，**禁止** `git commit -m "..."`，必须走以下安全写法：

### 1. 文件提交（首选，多行 / 特殊字符一律用它）

```bash
git commit -F <msg-file>

# 或 stdin
printf '%s\n' "$MSG" | git commit --file=-

# 或 heredoc 写文件再提交
cat > /tmp/commit-msg.txt <<'EOF'
feat(agent): add `runConcurrent`

- support drain-all-before-throw
EOF
git commit -F /tmp/commit-msg.txt
```

### 2. 单引号包裹（单行、无单引号时可用）

```bash
# 单引号内所有字符字面，反引号原样保留
git commit -m 'fix: support `bun install` on windows'
```

### 3. 转义反引号（不推荐，易漏）

```bash
git commit -m "fix: support \`bun install\` on windows"
```

## 安全速查

| 方式 | 反引号风险 |
|---|---|
| `git commit -m "...`...`..."` | 危险（双引号内被求值） |
| `git commit -m '...`...`...'` | 安全（单引号不展开） |
| `git commit -F <file>` | 安全（Git 直读文件，不过 shell） |
| `git commit --file=-` | 安全 |

## 禁止

- **禁止**把含反引号 / `$(...)` 的 message 拼进 `git commit -m "..."` 双引号
- **禁止**为图省事忽略此约束 —— 误执行后果是丢代码，不可逆

> PreToolUse hook `pre-git-commit-backtick-check.sh` 会在双引号 message 含未转义反引号 / `$(...)` 时硬拦截（exit 2），但 hook 是兜底，写法本身就该走安全方式。
