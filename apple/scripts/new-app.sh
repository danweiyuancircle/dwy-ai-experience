#!/usr/bin/env bash
# 保留现有创建入口；参数校验和跨平台文件装配由 Python 标准库处理。
set -euo pipefail
exec python3 "$(dirname "$0")/new_app.py" "$@"
