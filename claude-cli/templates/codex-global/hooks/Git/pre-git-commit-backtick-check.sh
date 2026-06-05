#!/bin/bash
# Codex PreToolUse Hook
# 拦截 git commit message 中会被 shell 命令替换的反引号 / $(...)
#
# 背景：AI 生成的 commit message 爱用 Markdown 风格反引号包代码标识符，
#   git commit -m "fix: support `bun install` on windows"
# 经 shell 执行时，双引号内的 `bun install` 会被当成命令替换 $(bun install) 实际执行，
# 输出塞进 message，甚至误执行破坏性命令导致丢代码。
# 单引号内 '...`...`...' 不展开，安全。
# 安全写法：git commit -F <file> / --file=- / 单引号。
# Codex 与 Claude Code 同样通过 stdin 传 JSON，从 .tool_input.command 取命令

# 从 stdin 读 JSON 取待执行命令
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')

# 只在含 git commit 的命令上检查
printf '%s' "$CMD" | grep -q 'git commit' || exit 0

# 逐字符做轻量 shell 词法扫描：跟踪引号状态，
# 只在「非单引号上下文」里出现裸反引号或 $( 时判危险（这些会被 shell 求值）。
# 命令经环境变量传入（stdin 已被 heredoc 脚本占用，不能再走管道）。
DANGER=$(CMD="$CMD" python3 <<'PY'
import os

s = os.environ.get("CMD", "")
in_single = False   # 单引号内：所有字符字面，反引号安全
in_double = False   # 双引号内：反引号 / $() 仍会命令替换
i, n = 0, len(s)
danger = False

while i < n:
    c = s[i]
    if c == '\\' and not in_single:
        i += 2
        continue
    if c == "'" and not in_double:
        in_single = not in_single
        i += 1
        continue
    if c == '"' and not in_single:
        in_double = not in_double
        i += 1
        continue
    if not in_single:
        if c == '`':
            danger = True
            break
        if c == '$' and i + 1 < n and s[i + 1] == '(':
            danger = True
            break
    i += 1

print("DANGER" if danger else "OK")
PY
)

[ "$DANGER" = "DANGER" ] || exit 0

echo "========================================"
echo "  WARNING: 危险的 commit message 写法"
echo "========================================"
echo ""
echo "检测到 git commit message 中含会被 shell 命令替换的反引号 \` 或 \$(...)。"
echo "双引号内的 \`...\` 会被当成命令替换实际执行，可能误执行命令甚至丢代码。"
echo ""
echo "改用以下任一安全写法："
echo "  1. 文件提交（推荐多行 / 含特殊字符）："
echo "       git commit -F <msg-file>"
echo "       printf '%s\\n' \"\$MSG\" | git commit --file=-"
echo "  2. 单引号包裹（单引号内反引号不展开）："
echo "       git commit -m 'fix: support \`bun install\` on windows'"
echo "  3. 转义反引号："
echo "       git commit -m \"fix: support \\\`bun install\\\` on windows\""
echo "========================================"
exit 2  # 暂停等待人工审批
