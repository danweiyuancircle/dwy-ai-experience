#!/usr/bin/env bash
# dwy-deploy-audit: 一键全量巡检（subagent 不可用时的串行/并行退化方案）
#
# 优先做法是让 Claude 用 subagent 并行派遣多个 Agent 跑各类 check_xxx.sh
# (见 SKILL.md Step 4)。本脚本仅作为本地一键回退使用。
#
# 用法:
#   ./run_all.sh <user>@<host> [-p <port>] [-i <key>] [--serial]
#
# 默认 8 路并行。--serial 强制串行。

set -uo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <user>@<host> [-p <port>] [-i <key>] [--serial]" >&2
  exit 1
fi

TARGET="$1"; shift
SSH_OPTS=(-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
PARALLEL=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) SSH_OPTS+=(-p "$2"); shift 2;;
    -i) SSH_OPTS+=(-i "$2"); shift 2;;
    --serial) PARALLEL=false; shift;;
    *)  echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR=$(mktemp -d -t dwy-audit-XXXXXX)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "========================================"
echo " dwy-deploy-audit | target: ${TARGET}"
echo " timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo " mode: $([ "$PARALLEL" = true ] && echo 'parallel (8 workers)' || echo 'serial')"
echo "========================================"

# 检查项: <section_name>:<script_name>
SECTIONS=(
  "BASE_INFO:check_base.sh"
  "SSH:check_ssh.sh"
  "NGINX:check_nginx.sh"
  "DB:check_db.sh"
  "HTTPS:check_https.sh"
  "ENV:check_env.sh"
  "DOCKER:check_docker.sh"
  "SERVICES:check_services.sh"
  "RESILIENCE:check_resilience.sh"
)

run_section() {
  local name="$1"
  local script="$2"
  local out_file="${TMP_DIR}/${name}.out"
  {
    echo "########## SECTION: ${name} ##########"
    bash "${SCRIPT_DIR}/${script}" "${TARGET}" "${SSH_OPTS[@]}" 2>&1 \
      || echo "[!] ${name} 部分失败"
    echo "########## END: ${name} ##########"
  } > "$out_file" 2>&1
}

if [[ "$PARALLEL" == "true" ]]; then
  # 并行：所有 section 后台启动
  pids=()
  for entry in "${SECTIONS[@]}"; do
    name="${entry%%:*}"
    script="${entry##*:}"
    run_section "$name" "$script" &
    pids+=($!)
  done

  # 等所有完成
  for pid in "${pids[@]}"; do
    wait "$pid"
  done

  # 按顺序输出结果（保证报告分类有序）
  for entry in "${SECTIONS[@]}"; do
    name="${entry%%:*}"
    echo ""
    cat "${TMP_DIR}/${name}.out"
  done
else
  # 串行
  for entry in "${SECTIONS[@]}"; do
    name="${entry%%:*}"
    script="${entry##*:}"
    echo ""
    run_section "$name" "$script"
    cat "${TMP_DIR}/${name}.out"
  done
fi

echo ""
echo "========================================"
echo " 巡检数据采集完成,请由 Claude 分析生成报告"
echo "========================================"
