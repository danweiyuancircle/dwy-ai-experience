#!/usr/bin/env bash
# dwy-deploy-audit: 一键全量巡检
# 用法: ./run_all.sh <user>@<host> [-p <port>] [-i <key>]
# 通过 SSH 远程执行所有只读检查,聚合输出供 Claude 分析

set -uo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <user>@<host> [-p <port>] [-i <key>]" >&2
  exit 1
fi

TARGET="$1"; shift
SSH_OPTS=(-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new)

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) SSH_OPTS+=(-p "$2"); shift 2;;
    -i) SSH_OPTS+=(-i "$2"); shift 2;;
    *)  echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo " dwy-deploy-audit | target: ${TARGET}"
echo " timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================"

run_section() {
  local name="$1"; shift
  echo ""
  echo "########## SECTION: ${name} ##########"
  bash "${SCRIPT_DIR}/$1" "${TARGET}" "${SSH_OPTS[@]}" 2>&1 || echo "[!] ${name} 部分失败,继续后续"
  echo "########## END: ${name} ##########"
}

run_section "BASE_INFO"  check_base.sh
run_section "SSH"        check_ssh.sh
run_section "NGINX"      check_nginx.sh
run_section "DB"         check_db.sh
run_section "HTTPS"      check_https.sh
run_section "ENV"        check_env.sh
run_section "DOCKER"     check_docker.sh
run_section "SERVICES"   check_services.sh

echo ""
echo "========================================"
echo " 巡检数据采集完成,请由 Claude 分析生成报告"
echo "========================================"
