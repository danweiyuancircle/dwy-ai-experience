#!/usr/bin/env bash
# dwy-sdk-spec 配置缓存读写
# 用法:
#   init_config.sh get <project_path>
#   init_config.sh set <project_path> <edition> <languages_json> <sdk_paths_json>
#   init_config.sh reset <project_path>
#   init_config.sh list

set -euo pipefail

CONFIG_DIR="${HOME}/.config/dwy-sdk-spec"
CONFIG_FILE="${CONFIG_DIR}/projects.json"

ensure_config() {
  mkdir -p "$CONFIG_DIR"
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo '{"version":"1","projects":{}}' > "$CONFIG_FILE"
  fi
  # 检测损坏
  if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    echo "ERROR: $CONFIG_FILE is corrupted. Back it up and delete to reset." >&2
    exit 2
  fi
}

cmd_get() {
  local project_path="$1"
  ensure_config
  jq --arg p "$project_path" '.projects[$p] // null' "$CONFIG_FILE"
}

cmd_set() {
  local project_path="$1"
  local edition="$2"
  local languages_json="$3"
  local sdk_paths_json="$4"

  if [[ "$edition" != "commercial" && "$edition" != "opensource" ]]; then
    echo "ERROR: edition must be 'commercial' or 'opensource', got: $edition" >&2
    exit 2
  fi

  ensure_config
  local now
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local tmp
  tmp=$(mktemp)
  jq \
    --arg p "$project_path" \
    --arg e "$edition" \
    --argjson l "$languages_json" \
    --argjson s "$sdk_paths_json" \
    --arg t "$now" \
    '.projects[$p] = {edition: $e, languages: $l, sdk_paths: $s, configured_at: $t}' \
    "$CONFIG_FILE" > "$tmp"
  mv "$tmp" "$CONFIG_FILE"

  echo "OK: cached $project_path -> $edition"
}

cmd_reset() {
  local project_path="$1"
  ensure_config
  local tmp
  tmp=$(mktemp)
  jq --arg p "$project_path" 'del(.projects[$p])' "$CONFIG_FILE" > "$tmp"
  mv "$tmp" "$CONFIG_FILE"
  echo "OK: removed $project_path from cache"
}

cmd_list() {
  ensure_config
  jq '.projects | to_entries | map({path: .key, edition: .value.edition, languages: .value.languages})' "$CONFIG_FILE"
}

main() {
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {get|set|reset|list} [args...]" >&2
    exit 2
  fi
  local action="$1"
  shift

  case "$action" in
    get)   cmd_get "$@" ;;
    set)   cmd_set "$@" ;;
    reset) cmd_reset "$@" ;;
    list)  cmd_list ;;
    *)
      echo "ERROR: unknown action: $action" >&2
      exit 2
      ;;
  esac
}

main "$@"
