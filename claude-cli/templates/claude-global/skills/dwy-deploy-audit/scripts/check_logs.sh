#!/usr/bin/env bash
# 日志大小与防爆检查 (只读)
#
# 检查范围:
#   - Docker 单容器 json-log 大小
#   - Docker daemon log-opts 是否生效到具体容器
#   - Nginx access/error log 大小 + logrotate 覆盖
#   - systemd journal 占用 + SystemMaxUse 配置
#   - 应用日志目录 (自动探测 /var/log/<svc>、/opt/*/logs、/home/*/logs)
#   - 总日志占用 vs 根盘剩余, 估算撑天数

TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
ROOT_FREE_MB=$(df -BM --output=avail / 2>/dev/null | tail -1 | tr -d ' M')
ROOT_FREE_MB=${ROOT_FREE_MB:-0}
NOW_TS=$(date +%s)

echo "--- 根盘可用 ---"
df -h / 2>/dev/null
echo "可用: ${ROOT_FREE_MB} MB"

# ============================================================
echo ""
echo "--- Docker 容器 json-log 大小 (单文件 Top 20) ---"
if command -v docker >/dev/null 2>&1; then
  # 收集 daemon log-opts 用于关联判定
  DAEMON_JSON=$(sudo -n cat /etc/docker/daemon.json 2>/dev/null \
                || cat /etc/docker/daemon.json 2>/dev/null || echo "")
  DAEMON_MAX_SIZE=$(echo "$DAEMON_JSON" \
    | grep -oE '"max-size"[[:space:]]*:[[:space:]]*"[^"]+"' \
    | head -1 | grep -oE '"[^"]+"$' | tr -d '"')
  echo "daemon.json log-opts max-size: ${DAEMON_MAX_SIZE:-(未配置)}"
  echo ""

  # 列出所有 json-log: <size> <path>
  LOG_LIST=$(sudo -n find /var/lib/docker/containers -maxdepth 2 -name "*-json.log" \
              -printf '%s %p\n' 2>/dev/null \
              || find /var/lib/docker/containers -maxdepth 2 -name "*-json.log" \
                 -printf '%s %p\n' 2>/dev/null)

  if [[ -z "$LOG_LIST" ]]; then
    echo "[i] 无法读取 /var/lib/docker/containers (需 sudo) 或无 json-log"
  else
    DOCKER_LOG_TOTAL_BYTES=0
    # 排序+top 20, 反查容器名
    while IFS=' ' read -r size path; do
      [[ -z "$size" ]] && continue
      DOCKER_LOG_TOTAL_BYTES=$(( DOCKER_LOG_TOTAL_BYTES + size ))
      cid=$(basename "$(dirname "$path")")
      cid_short="${cid:0:12}"
      name=$(docker inspect -f '{{.Name}}' "$cid" 2>/dev/null | sed 's|^/||')
      [[ -z "$name" ]] && name="<已删除>"
      size_mb=$(( size / 1024 / 1024 ))
      printf "  %-32s %6d MB  %s\n" "$name" "$size_mb" "$path"

      # 单文件大小告警
      if [[ "$size_mb" -ge 1024 ]] && [[ -z "$DAEMON_MAX_SIZE" ]]; then
        echo "    [!!!] CRITICAL: 单容器日志 ${size_mb} MB 且 daemon 无 log-opts 大小限制"
      elif [[ "$size_mb" -ge 500 ]]; then
        echo "    [!!] HIGH: 单容器日志 ${size_mb} MB"
      fi
    done < <(echo "$LOG_LIST" | sort -rn | head -20)

    DOCKER_LOG_TOTAL_MB=$(( DOCKER_LOG_TOTAL_BYTES / 1024 / 1024 ))
    echo ""
    echo "Docker json-log 合计: ${DOCKER_LOG_TOTAL_MB} MB"
  fi

  echo ""
  echo "--- 各容器是否覆盖 logging driver (compose level 优先于 daemon level) ---"
  docker ps -q 2>/dev/null | while read c; do
    name=$(docker inspect -f '{{.Name}}'                              "$c" | sed 's|^/||')
    lt=$(docker inspect -f   '{{.HostConfig.LogConfig.Type}}'         "$c" 2>/dev/null)
    lc=$(docker inspect -f   '{{json .HostConfig.LogConfig.Config}}'  "$c" 2>/dev/null)
    [[ -z "$lc" || "$lc" == "null" ]] && lc='{}'
    printf "  %-32s driver=%-12s opts=%s\n" "$name" "${lt:-?}" "$lc"
    if [[ "$lt" == "json-file" && "$lc" == "{}" && -z "$DAEMON_MAX_SIZE" ]]; then
      echo "    [!!] HIGH: 容器无 logging.options 且 daemon 无 max-size, 日志可无限增长"
    fi
  done
else
  echo "[i] Docker 未安装,跳过容器日志检查"
  DOCKER_LOG_TOTAL_MB=0
fi

# ============================================================
echo ""
echo "--- Nginx 日志 ---"
if [[ -d /var/log/nginx ]]; then
  ls -lh /var/log/nginx/ 2>/dev/null | head -20
  NGINX_LOG_BYTES=$(sudo -n du -sb /var/log/nginx 2>/dev/null | awk '{print $1}' \
                    || du -sb /var/log/nginx 2>/dev/null | awk '{print $1}')
  NGINX_LOG_MB=$(( ${NGINX_LOG_BYTES:-0} / 1024 / 1024 ))
  echo "合计: ${NGINX_LOG_MB} MB"

  # access.log / error.log 单文件大小
  for f in /var/log/nginx/access.log /var/log/nginx/error.log; do
    [[ -f "$f" ]] || continue
    sz_mb=$(( $(stat -c %s "$f" 2>/dev/null || echo 0) / 1024 / 1024 ))
    if [[ "$sz_mb" -ge 500 ]]; then
      echo "[!!] HIGH: $f 单文件 ${sz_mb} MB"
    fi
  done

  # logrotate 覆盖
  if [[ -f /etc/logrotate.d/nginx ]]; then
    echo "[OK] /etc/logrotate.d/nginx 存在"
  else
    echo "[!!] HIGH: nginx 已部署但无 /etc/logrotate.d/nginx, 日志可能无限增长"
  fi
else
  echo "[i] /var/log/nginx 不存在, 跳过"
  NGINX_LOG_MB=0
fi

# ============================================================
echo ""
echo "--- systemd journal 占用 ---"
if command -v journalctl >/dev/null 2>&1; then
  JOURNAL_USAGE=$(journalctl --disk-usage 2>/dev/null | grep -oE '[0-9.]+[KMG]B?' | tail -1)
  echo "journalctl --disk-usage: ${JOURNAL_USAGE:-?}"
  # 转 MB (粗略)
  case "$JOURNAL_USAGE" in
    *G*) JOURNAL_MB=$(echo "$JOURNAL_USAGE" | sed 's/[GBb]//g' | awk '{print int($1*1024)}') ;;
    *M*) JOURNAL_MB=$(echo "$JOURNAL_USAGE" | sed 's/[MBb]//g' | awk '{print int($1)}') ;;
    *K*) JOURNAL_MB=0 ;;
    *)   JOURNAL_MB=0 ;;
  esac

  # SystemMaxUse 配置
  SMU=$(grep -E "^[[:space:]]*SystemMaxUse" /etc/systemd/journald.conf 2>/dev/null \
        | head -1 | awk -F= '{gsub(/[ \t]/,"",$2); print $2}')
  echo "SystemMaxUse: ${SMU:-(未配置, 默认按磁盘 10% 自动控)}"

  if [[ "$JOURNAL_MB" -ge 2048 && -z "$SMU" ]]; then
    echo "[!!] HIGH: journal 已 ${JOURNAL_MB} MB 且未配 SystemMaxUse"
  fi
else
  JOURNAL_MB=0
fi

# ============================================================
echo ""
echo "--- 应用日志目录 (自动探测 Top 5) ---"
APP_LOG_TOTAL_MB=0
# 优先 sudo, 失败再退化; 不要用 OR fallback (du 退出码可能因部分不可读而非零, 会被双重执行)
APP_LOG_LIST=$(sudo -n du -smc /var/log/*/ /opt/*/logs /opt/*/log /home/*/logs /srv/*/logs 2>/dev/null \
  | grep -v 'total$' | sort -rn | head -10)
if [[ -z "$APP_LOG_LIST" ]]; then
  APP_LOG_LIST=$(du -smc /var/log/*/ /opt/*/logs /opt/*/log /home/*/logs /srv/*/logs 2>/dev/null \
    | grep -v 'total$' | sort -rn | head -10)
fi
echo "$APP_LOG_LIST"
APP_LOG_TOTAL_MB=$(echo "$APP_LOG_LIST" | awk '{s+=$1} END{print s+0}')

# ============================================================
echo ""
echo "--- 日志总占用 vs 根盘剩余 (撑天数粗估) ---"
TOTAL_LOG_MB=$(( DOCKER_LOG_TOTAL_MB + NGINX_LOG_MB + JOURNAL_MB + APP_LOG_TOTAL_MB ))
echo "Docker json-log: ${DOCKER_LOG_TOTAL_MB} MB"
echo "Nginx 日志:      ${NGINX_LOG_MB} MB"
echo "systemd journal: ${JOURNAL_MB} MB"
echo "应用日志合计:    ${APP_LOG_TOTAL_MB} MB"
echo "日志合计:        ${TOTAL_LOG_MB} MB"
echo "根盘可用:        ${ROOT_FREE_MB} MB"

# 撑天数估算: 取所有 docker json-log 的 (size / 容器存活天数) 加总作为 daily growth
GROWTH_MB=0
if command -v docker >/dev/null 2>&1; then
  for c in $(docker ps -q 2>/dev/null); do
    cid_full=$(docker inspect -f '{{.Id}}' "$c" 2>/dev/null)
    log_path="/var/lib/docker/containers/${cid_full}/${cid_full}-json.log"
    sz=$(sudo -n stat -c %s "$log_path" 2>/dev/null || stat -c %s "$log_path" 2>/dev/null || echo 0)
    started=$(docker inspect -f '{{.State.StartedAt}}' "$c" 2>/dev/null)
    started_ts=$(date -d "$started" +%s 2>/dev/null || echo 0)
    if [[ "$started_ts" -gt 0 && "$sz" -gt 0 ]]; then
      age_sec=$(( NOW_TS - started_ts ))
      [[ "$age_sec" -lt 60 ]] && age_sec=60   # 防除零, 至少按 1 分钟算
      daily_bytes=$(( sz * 86400 / age_sec ))
      daily_mb=$(( daily_bytes / 1024 / 1024 ))
      GROWTH_MB=$(( GROWTH_MB + daily_mb ))
    fi
  done
fi

echo "估算 Docker 日志日均增量: ${GROWTH_MB} MB/day (基于容器存活时长)"

if [[ "$GROWTH_MB" -gt 0 && "$ROOT_FREE_MB" -gt 0 ]]; then
  DAYS=$(( ROOT_FREE_MB / GROWTH_MB ))
  echo "按当前增速预计可撑: ${DAYS} 天 (粗估, 仅算 docker json-log)"
  if   [[ "$DAYS" -lt 30 ]]; then echo "[!!!] CRITICAL: 不足 30 天, 必须立即配 log-opts 或扩盘"
  elif [[ "$DAYS" -lt 90 ]]; then echo "[!!] HIGH: 不足 90 天, 建议尽快补 log-opts max-size"
  else echo "[OK] 撑天数 >= 90 天"
  fi
else
  echo "[i] 无法估算日均增量 (容器刚起或无日志)"
fi

# ============================================================
echo ""
echo "--- 关键服务 logrotate 规则一览 (只读复述) ---"
for app in nginx postgresql redis docker rsyslog; do
  if [[ -f "/etc/logrotate.d/$app" ]]; then
    echo "  [OK] /etc/logrotate.d/$app"
  fi
done
REMOTE
