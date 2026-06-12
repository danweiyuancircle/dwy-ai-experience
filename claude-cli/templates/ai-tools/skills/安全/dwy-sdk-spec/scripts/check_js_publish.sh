#!/usr/bin/env bash
# JS/TS SDK 发布前文件清单审计（npm pack --dry-run）
# 用法: check_js_publish.sh <js_sdk_root> --edition commercial|opensource

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <js_sdk_root> --edition commercial|opensource" >&2
  exit 2
fi

PKG_ROOT="$1"
shift

EDITION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --edition) EDITION="$2"; shift 2 ;;
    *) echo "ERROR: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ "$EDITION" != "commercial" && "$EDITION" != "opensource" ]]; then
  echo "ERROR: --edition must be 'commercial' or 'opensource'" >&2
  exit 2
fi

if [[ ! -d "$PKG_ROOT" ]]; then
  echo "ERROR: not a directory: $PKG_ROOT" >&2
  exit 2
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm not found in PATH" >&2
  exit 2
fi

echo "[1/2] Running npm pack --dry-run in $PKG_ROOT ..."

# npm pack --dry-run --json 输出包内文件列表
# 注：某些 npm 版本 --json 输出到 stderr，--silent 抑制非 JSON 输出
PACK_OUTPUT=$(cd "$PKG_ROOT" && npm pack --dry-run --json 2>/dev/null) || {
  echo "ERROR: npm pack --dry-run failed; run 'npm install' first?" >&2
  exit 2
}

# 提取文件路径列表
FILES=$(echo "$PACK_OUTPUT" | jq -r '.[0].files[].path' 2>/dev/null) || {
  echo "ERROR: failed to parse npm pack output:" >&2
  echo "$PACK_OUTPUT" | head -20 >&2
  exit 2
}

echo "[2/2] Audit result (edition=$EDITION):"
echo "----------------------------------------"

# 致命级（任何版本都禁）
CRITICAL_REGEX='(^|/)(\.env(\..+)?|\.npmrc|\.pypirc|\.git-credentials|id_rsa|id_ed25519|secrets\.json|credentials\.json)$|\.(pem|key|p12)$|(^|/)\.aws/credentials$'

# 开源版黑名单
OPENSOURCE_DENY_REGEX='(^|/)(src|tests|__tests__|\.git|\.github|\.gitlab-ci\.yml|\.travis\.yml|\.circleci|\.vscode|\.idea|node_modules|\.husky)/|(^|/)(tsconfig.*\.json|vite\.config\.|vitest\.config\.|tsup\.config\.|rollup\.config\.|webpack\.config\.|jest\.config\.|\.eslintrc.*|\.prettierrc.*|eslint\.config\.|prettier\.config\.|commitlint\.config\.|\.gitignore|\.gitattributes|\.DS_Store|Thumbs\.db|pnpm-lock\.yaml|package-lock\.json|yarn\.lock)|\.(map|tsbuildinfo|swp|swo)$|\.(test|spec)\.(ts|tsx|js|jsx)$'

# 商业版白名单（其他视为违规）
COMMERCIAL_ALLOW_REGEX='^(dist/|bin/|package\.json$|README(\..+)?$|LICEN[SC]E(\..+)?$|CHANGELOG(\..+)?$)'

violations=()
critical=()

while IFS= read -r f; do
  [[ -z "$f" ]] && continue

  if [[ "$f" =~ $CRITICAL_REGEX ]]; then
    critical+=("$f")
    continue
  fi

  if [[ "$EDITION" == "opensource" ]]; then
    if [[ "$f" =~ $OPENSOURCE_DENY_REGEX ]]; then
      violations+=("$f  [denied by opensource rules]")
    fi
  else
    if [[ ! "$f" =~ $COMMERCIAL_ALLOW_REGEX ]]; then
      violations+=("$f  [not in commercial whitelist]")
    fi
  fi
done <<< "$FILES"

if [[ ${#critical[@]} -gt 0 ]]; then
  echo "[CRITICAL] secret-like files in package — DO NOT PUBLISH:"
  for f in "${critical[@]}"; do
    echo "  $f"
  done
  echo ""
fi

if [[ ${#violations[@]} -gt 0 ]]; then
  echo "[VIOLATION] ${#violations[@]} file(s) violate $EDITION rules:"
  for v in "${violations[@]}"; do
    echo "  $v"
  done
  echo ""
  exit 1
fi

if [[ ${#critical[@]} -gt 0 ]]; then
  exit 1
fi

count=$(echo "$FILES" | grep -c .)
echo "OK: package passes $EDITION audit ($count file(s))"
