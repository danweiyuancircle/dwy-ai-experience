#!/usr/bin/env bash
# dwy-sdk-spec 配置缓存读写
# 缓存写项目内 <project_root>/.dwy/sdk-spec/config.json，扁平结构、不存绝对路径
# 用法:
#   init_config.sh get   <project_root>
#   init_config.sh set   <project_root> <edition> <languages_json> <sdk_paths_json>
#   init_config.sh reset <project_root>

set -euo pipefail

config_file() {
  echo "${1%/}/.dwy/sdk-spec/config.json"
}

ensure_config() {
  local root="$1"
  local dir="${root%/}/.dwy/sdk-spec"
  local file
  file="$(config_file "$root")"
  mkdir -p "$dir"
  if [[ ! -f "$file" ]]; then
    echo '{"version":"1"}' > "$file"
  fi
  # 检测损坏
  if ! jq empty "$file" 2>/dev/null; then
    echo "ERROR: $file is corrupted. Back it up and delete to reset." >&2
    exit 2
  fi
}

cmd_get() {
  local root="$1"
  ensure_config "$root"
  # 无 edition 视为未配置，返回 null
  jq 'if has("edition") then . else null end' "$(config_file "$root")"
}

cmd_set() {
  local root="$1" edition="$2" languages_json="$3" sdk_paths_json="$4"

  if [[ "$edition" != "commercial" && "$edition" != "opensource" ]]; then
    echo "ERROR: edition must be 'commercial' or 'opensource', got: $edition" >&2
    exit 2
  fi

  ensure_config "$root"
  local now file tmp
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  file="$(config_file "$root")"
  tmp=$(mktemp)
  jq -n \
    --arg e "$edition" \
    --argjson l "$languages_json" \
    --argjson s "$sdk_paths_json" \
    --arg t "$now" \
    '{version:"1", edition:$e, languages:$l, sdk_paths:$s, configured_at:$t}' \
    > "$tmp"
  mv "$tmp" "$file"

  echo "OK: cached $root -> $edition"
  echo "Remember to add .dwy/ to .gitignore (本机判断缓存，不入版本库)"
}

cmd_reset() {
  local root="$1"
  local file
  file="$(config_file "$root")"
  rm -f "$file"
  echo "OK: removed $file"
}

main() {
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {get|set|reset} <project_root> [args...]" >&2
    exit 2
  fi
  local action="$1"
  shift

  case "$action" in
    get)   cmd_get "$@" ;;
    set)   cmd_set "$@" ;;
    reset) cmd_reset "$@" ;;
    *)
      echo "ERROR: unknown action: $action" >&2
      exit 2
      ;;
  esac
}

main "$@"
