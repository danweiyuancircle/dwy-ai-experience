#!/bin/bash
# Codex PreToolUse Hook
# 在 git commit 前检查暂存文件中是否包含敏感数据
# Codex 与 Claude Code 同样通过 stdin 传 JSON，从 .tool_input.command 取命令

# 从 stdin 读 JSON 并取出待执行命令
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

# 只拦截 git commit 命令
printf '%s' "$CMD" | grep -q 'git commit' || exit 0

# 获取暂存文件列表
STAGED=$(git diff --cached --diff-filter=ACMR --name-only 2>/dev/null)
[ -z "$STAGED" ] && exit 0

# 敏感数据匹配模式
PATTERNS=(
    # 密码/密钥
    'password'
    'passwd'
    'secret'
    'api[_-]?key'
    'access[_-]?token'
    'private[_-]?key'
    'auth[_-]?token'
    'client[_-]?secret'
    'bearer'

    # 数据库连接串
    'jdbc:'
    'mysql://'
    'postgres://'
    'mongodb://'
    'redis://'

    # 私钥文件
    '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY'

    # 平台 Token
    'sk-[a-zA-Z0-9]{20,}'        # OpenAI
    'ghp_[a-zA-Z0-9]{36}'        # GitHub
    'AKIA[0-9A-Z]{16}'           # AWS
)

# 拼接为正则
REGEX=$(IFS='|'; echo "${PATTERNS[*]}")

# 扫描暂存内容
RESULT=$(git diff --cached -U0 2>/dev/null | grep -inE "$REGEX" 2>/dev/null)

if [ -n "$RESULT" ]; then
    echo "========================================"
    echo "  WARNING: Sensitive data detected"
    echo "========================================"
    echo ""
    echo "$RESULT"
    echo ""
    echo "Please review before committing."
    echo "========================================"
    exit 2  # 暂停等待人工审批
fi

exit 0
