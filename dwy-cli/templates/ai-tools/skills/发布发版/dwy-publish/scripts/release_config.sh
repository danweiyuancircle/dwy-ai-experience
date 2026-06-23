#!/usr/bin/env bash
# dwy-publish 发布方式缓存读写
# 缓存写项目内 <project_root>/.dwy/publish/config.json，key 用相对项目根的相对目录
# 用法:
#   release_config.sh get   <project_root> <rel_dir>
#   release_config.sh set   <project_root> <rel_dir> <platform> <method> <channel> <configured> [build_cmd] [publish_cmd] [verify_cmd] [cmd_source]
#   release_config.sh reset <project_root> <rel_dir>
#   release_config.sh list  <project_root>
#
# 设计要点（与发布编排配套）:
#   - 通用步(定版本/changelog/安全检查)不进缓存,走固化流程
#   - 项目步(build/publish/verify)命令因项目而异,探测/确认后存这里复用
#   - cmd_source 是命令来源指纹,编排器 get 后比对,变更则重新问用户更新

set -euo pipefail

config_file() {
  echo "${1%/}/.dwy/publish/config.json"
}

ensure_config() {
  local root="$1"
  local dir="${root%/}/.dwy/publish"
  local file
  file="$(config_file "$root")"
  mkdir -p "$dir"
  if [[ ! -f "$file" ]]; then
    echo '{"version":"1","apps":{}}' > "$file"
  fi
  # 检测损坏
  if ! jq empty "$file" 2>/dev/null; then
    echo "ERROR: $file is corrupted. Back it up and delete to reset." >&2
    exit 2
  fi
}

cmd_get() {
  local root="$1" rel="$2"
  ensure_config "$root"
  jq --arg p "$rel" '.apps[$p] // null' "$(config_file "$root")"
}

cmd_set() {
  local root="$1" rel="$2" platform="$3" method="$4" channel="$5" configured="$6"
  local build_cmd="${7:-}" publish_cmd="${8:-}" verify_cmd="${9:-}" cmd_source="${10:-}"

  case "$platform" in
    frontend|backend|ios|android|harmony|generic) ;;
    *) echo "ERROR: platform must be one of frontend|backend|ios|android|harmony|generic, got: $platform" >&2; exit 2 ;;
  esac
  case "$configured" in
    true|false) ;;
    *) echo "ERROR: configured must be 'true' or 'false', got: $configured" >&2; exit 2 ;;
  esac
  if [[ -z "$method" ]]; then
    echo "ERROR: method must not be empty" >&2; exit 2
  fi

  ensure_config "$root"
  local now file tmp
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  file="$(config_file "$root")"
  tmp=$(mktemp)
  jq \
    --arg p "$rel" \
    --arg pl "$platform" \
    --arg m "$method" \
    --arg c "$channel" \
    --arg b "$build_cmd" \
    --arg pub "$publish_cmd" \
    --arg v "$verify_cmd" \
    --arg cs "$cmd_source" \
    --argjson cfg "$configured" \
    --arg t "$now" \
    '.apps[$p] = {platform:$pl, method:$m, channel:$c, build_cmd:$b, publish_cmd:$pub, verify_cmd:$v, cmd_source:$cs, configured:$cfg, configured_at:$t}' \
    "$file" > "$tmp"
  mv "$tmp" "$file"

  echo "OK: cached $rel -> $platform/$method"
  echo "Remember to add .dwy/ to .gitignore (本机判断缓存，不入版本库)"
}

cmd_reset() {
  local root="$1" rel="$2"
  ensure_config "$root"
  local file tmp
  file="$(config_file "$root")"
  tmp=$(mktemp)
  jq --arg p "$rel" 'del(.apps[$p])' "$file" > "$tmp"
  mv "$tmp" "$file"
  echo "OK: removed $rel from cache"
}

cmd_list() {
  local root="$1"
  ensure_config "$root"
  jq '.apps | to_entries | map({dir: .key, platform: .value.platform, method: .value.method, configured: .value.configured})' "$(config_file "$root")"
}

main() {
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {get|set|reset|list} <project_root> [args...]" >&2
    exit 2
  fi
  local action="$1"; shift
  case "$action" in
    get)   cmd_get "$@" ;;
    set)   cmd_set "$@" ;;
    reset) cmd_reset "$@" ;;
    list)  cmd_list "$@" ;;
    *) echo "ERROR: unknown action: $action" >&2; exit 2 ;;
  esac
}

main "$@"
