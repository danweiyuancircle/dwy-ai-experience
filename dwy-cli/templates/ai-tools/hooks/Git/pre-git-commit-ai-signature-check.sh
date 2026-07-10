#!/bin/bash
# Claude Code PreToolUse Hook
# 拦截 git commit message 中的 AI 署名 / 生成声明
#
# 背景：AI agent 常在 commit message 中附加 Co-Authored-By: Claude / Generated with Claude Code 等署名。
# 本 hook 检出此类模式后硬拦截（exit 2），要求人工确认或清理后再提交。
#
# 覆盖模式（不区分大小写）：
#   Co-Authored-By: <ai-name> <noreply@...>
#   Generated with Claude Code
#   Generated with ...
#   noreply@anthropic.com / noreply@openai.com
#   Claude / ChatGPT / GPT / Copilot / Cursor / AI / LLM (在签名行上下文)

# 从 stdin 读 JSON 取待执行命令（Claude Code 与 Codex 同样通过 stdin 传 .tool_input.command）
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

# 只在含 git commit 的命令上检查
printf '%s' "$CMD" | grep -q 'git commit' || exit 0

# AI 署名匹配模式
AI_PATTERNS=(
    # Co-Authored-By trailer（任意 AI 名称 + 含 < 的邮箱）
    "Co-Authored-By:"
    # 生成声明
    "Generated with"
    # 常见 AI 署名邮箱
    "noreply@anthropic\.com"
    "noreply@openai\.com"
    # AI 产品名（在签名行上下文，前面有 Co-Authored-By 或单独出现在行尾）
    "Co-Authored-By:.*[Cc]laude"
    "Co-Authored-By:.*[Cc]hatGPT"
    "Co-Authored-By:.*GPT"
    "Co-Authored-By:.*[Cc]opilot"
    "Co-Authored-By:.*[Cc]ursor"
)

REGEX=$(IFS='|'; echo "${AI_PATTERNS[*]}")

HIT=$(printf '%s' "$CMD" | grep -inE "$REGEX" 2>/dev/null)

if [ -n "$HIT" ]; then
    echo "========================================"
    echo "  WARNING: AI 署名 detected"
    echo "========================================"
    echo ""
    echo "$HIT"
    echo ""
    echo "commit message 中禁止出现 Co-Authored-By / Generated with 等 AI 署名。"
    echo "请清理 AI 署名后再提交。"
    echo ""
    echo "如果要强制提交，请手动执行 git commit（绕过 hook）。"
    echo "========================================"
    exit 2  # 暂停等待人工审批
fi

exit 0
