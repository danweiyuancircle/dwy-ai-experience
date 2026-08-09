#!/usr/bin/env bash
# App Store Connect 用户级配置管理：只保存非秘密标识与私钥文件，禁止向 Skill 或项目目录写入凭据。

set -euo pipefail

default_root="/Users/$(id -un)/.dwy/app-store-connect"

# 输出用法，避免调用者猜测参数格式而误把私钥内容传入命令行。
usage() {
  cat <<'EOF'
Usage:
  appstore_config.sh init [--root <directory>]
  appstore_config.sh get [--root <directory>]
  appstore_config.sh set --issuer-id <id> --key-id <id> [--team-id <id>] [--root <directory>]
  appstore_config.sh import-key --path <AuthKey.p8> [--root <directory>]
  appstore_config.sh reset [--root <directory>]
EOF
}

# 创建私有目录并收紧权限，防止同机其他用户读取配置或私钥。
ensure_root() {
  mkdir -p "$root/private_keys" "$root/sessions" "$root/submissions"
  chmod 700 "$root" "$root/private_keys" "$root/sessions" "$root/submissions"
}

# 将非秘密配置初始化为 JSON；私钥单独存放，避免在 get 输出中泄漏。
ensure_config() {
  ensure_root
  if [[ ! -f "$config_file" ]]; then
    jq -n '{version: 1}' > "$config_file"
    chmod 600 "$config_file"
  fi
  if ! jq empty "$config_file" >/dev/null 2>&1; then
    echo "ERROR: configuration is not valid JSON: $config_file" >&2
    exit 2
  fi
}

# 校验受外部输入控制的标识长度，避免错误或过大的配置写入本地缓存。
validate_id() {
  local label="$1" value="$2" limit="$3"
  if [[ -z "$value" || ${#value} -gt "$limit" ]]; then
    echo "ERROR: $label must contain 1-$limit characters" >&2
    exit 2
  fi
}

# 解析共享根目录参数；其他参数由具体子命令处理。
parse_root() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --root)
        root="$2"
        shift 2
        ;;
      *)
        remaining+=("$1")
        remaining_count=$((remaining_count + 1))
        shift
        ;;
    esac
  done
}

action="${1:-}"
if [[ -z "$action" ]]; then
  usage >&2
  exit 2
fi
shift

root="$default_root"
remaining=()
remaining_count=0
parse_root "$@"
# macOS 自带 Bash 在 `nounset` 下会将空数组视为未绑定，因此空参数必须避免展开数组。
if [[ "$remaining_count" -eq 0 ]]; then
  set --
else
  set -- "${remaining[@]}"
fi
config_file="$root/config.json"

case "$action" in
  init)
    [[ $# -eq 0 ]] || { usage >&2; exit 2; }
    ensure_config
    echo "OK: initialized $root"
    ;;
  get)
    [[ $# -eq 0 ]] || { usage >&2; exit 2; }
    ensure_config
    cat "$config_file"
    ;;
  set)
    issuer_id=""
    key_id=""
    team_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --issuer-id) issuer_id="$2"; shift 2 ;;
        --key-id) key_id="$2"; shift 2 ;;
        --team-id) team_id="$2"; shift 2 ;;
        *) usage >&2; exit 2 ;;
      esac
    done
    validate_id "issuer id" "$issuer_id" 128
    validate_id "key id" "$key_id" 64
    if [[ -n "$team_id" ]]; then validate_id "team id" "$team_id" 64; fi
    ensure_config
    jq -n --arg issuer "$issuer_id" --arg key "$key_id" --arg team "$team_id" \
      '{version: 1, issuer_id: $issuer, key_id: $key, team_id: $team}' > "$config_file"
    chmod 600 "$config_file"
    echo "OK: stored non-secret API identifiers in $config_file"
    ;;
  import-key)
    [[ $# -eq 2 && "$1" == "--path" ]] || { usage >&2; exit 2; }
    source_key="$2"
    [[ -f "$source_key" && "${source_key##*.}" == "p8" ]] || {
      echo "ERROR: --path must reference an existing .p8 file" >&2
      exit 2
    }
    ensure_config
    target_key="$root/private_keys/$(basename "$source_key")"
    cp "$source_key" "$target_key"
    chmod 600 "$target_key"
    echo "OK: imported private key to $target_key"
    ;;
  reset)
    [[ $# -eq 0 ]] || { usage >&2; exit 2; }
    if [[ -f "$config_file" ]]; then
      rm "$config_file"
    fi
    echo "OK: removed non-secret configuration; private keys and submissions were preserved"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
