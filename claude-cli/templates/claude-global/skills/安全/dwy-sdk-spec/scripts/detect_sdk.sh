#!/usr/bin/env bash
# 探测项目内的 Python / JS SDK 子包
# 用法: detect_sdk.sh <project_root>
# 输出: JSON {"python": [...], "js": [...]}  路径相对项目根

set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "ERROR: not a directory: $PROJECT_ROOT" >&2
  exit 2
fi

# 找 Python SDK：pyproject.toml 含 [project] 段，或 setup.py
find_python_sdks() {
  local results=()
  # 项目根
  if [[ -f "$PROJECT_ROOT/pyproject.toml" ]] && grep -q '^\[project\]' "$PROJECT_ROOT/pyproject.toml" 2>/dev/null; then
    results+=(".")
  elif [[ -f "$PROJECT_ROOT/setup.py" ]]; then
    results+=(".")
  fi
  # 子目录（限 2 层深度，排除 node_modules / .venv / venv / dist / build / .git）
  while IFS= read -r f; do
    local d
    d=$(dirname "$f")
    local rel="${d#"$PROJECT_ROOT"/}"
    # 验证含 [project] 段
    if grep -q '^\[project\]' "$f" 2>/dev/null; then
      results+=("$rel")
    fi
  done < <(find "$PROJECT_ROOT" -mindepth 2 -maxdepth 3 -name pyproject.toml -type f \
           -not -path "*/node_modules/*" \
           -not -path "*/.venv/*" \
           -not -path "*/venv/*" \
           -not -path "*/dist/*" \
           -not -path "*/build/*" \
           -not -path "*/.git/*" 2>/dev/null)

  # 去重(空数组下 ${arr[@]} 在 set -u 会 unbound,用 ${arr[@]+...} 安全展开)
  printf '%s\n' "${results[@]+"${results[@]}"}" | awk 'NF && !seen[$0]++'
}

# 找 JS SDK：package.json 含 main / exports / module 字段
find_js_sdks() {
  local results=()
  if [[ -f "$PROJECT_ROOT/package.json" ]] && jq -e '.main // .exports // .module' "$PROJECT_ROOT/package.json" >/dev/null 2>&1; then
    results+=(".")
  fi
  while IFS= read -r f; do
    local d
    d=$(dirname "$f")
    local rel="${d#"$PROJECT_ROOT"/}"
    if jq -e '.main // .exports // .module' "$f" >/dev/null 2>&1; then
      results+=("$rel")
    fi
  done < <(find "$PROJECT_ROOT" -mindepth 2 -maxdepth 3 -name package.json -type f \
           -not -path "*/node_modules/*" \
           -not -path "*/.venv/*" \
           -not -path "*/dist/*" \
           -not -path "*/build/*" \
           -not -path "*/.git/*" 2>/dev/null)

  printf '%s\n' "${results[@]+"${results[@]}"}" | awk 'NF && !seen[$0]++'
}

python_list=$(find_python_sdks | jq -R . | jq -s .)
js_list=$(find_js_sdks | jq -R . | jq -s .)

jq -n --argjson py "$python_list" --argjson js "$js_list" '{python: $py, js: $js}'
