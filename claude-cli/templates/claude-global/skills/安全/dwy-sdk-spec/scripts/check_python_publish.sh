#!/usr/bin/env bash
# Python SDK 发布前文件清单审计（不实际发布）
# 用法: check_python_publish.sh <python_sdk_root> --edition commercial|opensource

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <python_sdk_root> --edition commercial|opensource" >&2
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

if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python not found in PATH" >&2
  exit 2
fi
PY=$(command -v python || command -v python3)

# 临时构建目录
TMPDIR=$(mktemp -d -t dwy-sdk-spec-py-XXXX)
trap 'rm -rf "$TMPDIR"' EXIT

echo "[1/3] Building wheel to $TMPDIR ..."
(cd "$PKG_ROOT" && "$PY" -m build --outdir "$TMPDIR") >&2

WHEEL=$(find "$TMPDIR" -name '*.whl' -type f | head -1)
if [[ -z "$WHEEL" ]]; then
  echo "ERROR: no wheel produced" >&2
  exit 2
fi
echo "[2/3] Listing wheel contents: $(basename "$WHEEL")"

# 列文件（剥掉 .dist-info 路径前缀，便于审计）
FILES=$(unzip -Z1 "$WHEEL")

# 致命级（任何版本都禁）
declare -a CRITICAL_PATTERNS=(
  '(^|/)\.env(\..+)?$'
  '(^|/)\.npmrc$'
  '(^|/)\.pypirc$'
  '(^|/)\.git-credentials$'
  '(^|/)id_rsa$'
  '(^|/)id_ed25519$'
  '\.pem$'
  '\.key$'
  '\.p12$'
  '(^|/)secrets\.json$'
  '(^|/)credentials\.json$'
)

# 开源版黑名单
declare -a OPENSOURCE_DENY=(
  '__pycache__/'
  '\.pyc$'
  '\.pyo$'
  '\.egg-info/'
  '\.mypy_cache/'
  '\.pytest_cache/'
  '\.ruff_cache/'
  '\.pdb$'
  '(^|/)\.git/'
  '(^|/)\.gitignore$'
  '(^|/)\.DS_Store$'
  '(^|/)\.vscode/'
  '(^|/)\.idea/'
  '\.bak$'
  '\.swp$'
)

# 商业版白名单（其他视为违规）
declare -a COMMERCIAL_ALLOW=(
  '\.so$'
  '\.pyi$'
  '(^|/)py\.typed$'
  '\.dist-info/'
  '(^|/)LICEN[SC]E(\..+)?$'
  '(^|/)README(\..+)?$'
  '\.json$'
  '\.txt$'
)

violations=()
critical=()

while IFS= read -r f; do
  [[ -z "$f" ]] && continue

  # 致命级
  for pat in "${CRITICAL_PATTERNS[@]}"; do
    if [[ "$f" =~ $pat ]]; then
      critical+=("$f")
      continue 2
    fi
  done

  if [[ "$EDITION" == "opensource" ]]; then
    for pat in "${OPENSOURCE_DENY[@]}"; do
      if [[ "$f" =~ $pat ]]; then
        violations+=("$f  [denied: $pat]")
        break
      fi
    done
  else
    # commercial: 白名单检查
    # 排除目录条目（以 / 结尾）
    [[ "$f" == */ ]] && continue
    matched=0
    for pat in "${COMMERCIAL_ALLOW[@]}"; do
      if [[ "$f" =~ $pat ]]; then
        matched=1
        break
      fi
    done
    # 单独允许：包根的 __init__.py（公开入口）/ 不以 _ 开头的 .py
    if [[ $matched -eq 0 ]] && [[ "$f" =~ \.py$ ]]; then
      base=$(basename "$f")
      if [[ "$base" == "__init__.py" ]] || [[ ! "$base" =~ ^_ ]]; then
        matched=1
      fi
    fi
    if [[ $matched -eq 0 ]]; then
      violations+=("$f  [not in commercial whitelist]")
    fi
  fi
done <<< "$FILES"

echo "[3/3] Audit result (edition=$EDITION):"
echo "----------------------------------------"

if [[ ${#critical[@]} -gt 0 ]]; then
  echo "[CRITICAL] secret-like files in wheel — DO NOT PUBLISH:"
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

echo "OK: wheel passes $EDITION audit ($(echo "$FILES" | wc -l | tr -d ' ') file(s))"
