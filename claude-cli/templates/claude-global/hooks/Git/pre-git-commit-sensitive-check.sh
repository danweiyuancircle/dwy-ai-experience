#!/bin/bash
# Claude Code PreToolUse Hook
# 在 git commit 前检查暂存文件中是否包含敏感数据

# 从 stdin 读 JSON 并取出待执行命令（Claude Code 与 Codex 同样通过 stdin 传 .tool_input.command）
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

# 只拦截 git commit 命令
printf '%s' "$CMD" | grep -q 'git commit' || exit 0

# 获取暂存文件列表
STAGED=$(git diff --cached --diff-filter=ACMR --name-only 2>/dev/null)
[ -z "$STAGED" ] && exit 0

# 敏感数据匹配模式（赋值/上下文形式，避免类名/变量名裸词误报）
PATTERNS=(
    # 口令/密钥/令牌赋值（词 + :或= + 引号值；PairingSecret / clientSecret 等标识符不命中）
    "(password|passwd)[[:space:]]*[:=][[:space:]]*[\"'][^\"']{4,}"
    "secret[[:space:]]*[:=][[:space:]]*[\"'][^\"']{8,}"
    "api[_-]?key[[:space:]]*[:=][[:space:]]*[\"'][^\"']{8,}"
    "(access|auth)[_-]?token[[:space:]]*[:=][[:space:]]*[\"'][^\"']{8,}"
    "client[_-]?secret[[:space:]]*[:=][[:space:]]*[\"'][^\"']{8,}"
    "[Bb]earer[[:space:]]+[a-zA-Z0-9._-]{20,}"

    # 含凭证的连接串（scheme://user:pass@host）
    "://[a-zA-Z0-9_.-]+:[^@[:space:]/]{3,}@"

    # 私钥文件块
    "-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY"

    # 平台 Token（格式高特异，裸匹配）
    "sk-[a-zA-Z0-9]{20,}"        # OpenAI
    "ghp_[a-zA-Z0-9]{36}"        # GitHub
    "AKIA[0-9A-Z]{16}"           # AWS
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
