#!/usr/bin/env bash
# 硬件规格识别 + 当前服务资源配置盘点 (只读)
#
# 输出 raw data, 由主 Claude 对照 SKILL.md 4.10 的推荐分级表生成
# "推荐 vs 当前" 对比报告。
#
# 检查范围:
#   - 宿主硬件: CPU 核数 / 总内存 / 根盘容量 / swap
#   - 当前容器: mem_limit / cpus / shm_size / 实际占用
#   - Postgres 启动参数: shared_buffers / effective_cache_size / work_mem 等
#   - Redis 启动参数:    maxmemory / maxmemory-policy / appendonly / save
#   - compose 文件中的资源声明 (供 grep 比对)

TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- 宿主硬件规格 ---"
CPU_CORES=$(nproc 2>/dev/null || echo "?")
CPU_MODEL=$(LC_ALL=C lscpu 2>/dev/null | awk -F: '/^Model name/ {gsub(/^[ \t]+/,"",$2); print $2; exit}')
[[ -z "$CPU_MODEL" ]] && CPU_MODEL=$(awk -F: '/model name/ {gsub(/^[ \t]+/,"",$2); print $2; exit}' /proc/cpuinfo 2>/dev/null)
MEM_TOTAL_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null)
MEM_AVAIL_KB=$(awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null)
SWAP_TOTAL_KB=$(awk '/SwapTotal/ {print $2}' /proc/meminfo 2>/dev/null)
MEM_TOTAL_MB=$(( ${MEM_TOTAL_KB:-0} / 1024 ))
MEM_AVAIL_MB=$(( ${MEM_AVAIL_KB:-0} / 1024 ))
SWAP_TOTAL_MB=$(( ${SWAP_TOTAL_KB:-0} / 1024 ))

# 推荐分档(对齐 SKILL.md 4.10 的 2/4/8/16 GB 表)
if   [[ $MEM_TOTAL_MB -ge 14000 ]]; then TIER="16GB"
elif [[ $MEM_TOTAL_MB -ge 7000  ]]; then TIER="8GB"
elif [[ $MEM_TOTAL_MB -ge 3500  ]]; then TIER="4GB"
elif [[ $MEM_TOTAL_MB -ge 1500  ]]; then TIER="2GB"
else                                     TIER="<2GB"
fi

echo "CPU 核数: $CPU_CORES"
echo "CPU 型号: ${CPU_MODEL:-unknown}"
echo "总内存:   ${MEM_TOTAL_MB} MB"
echo "可用内存: ${MEM_AVAIL_MB} MB"
echo "Swap:     ${SWAP_TOTAL_MB} MB"
echo "推荐分档: ${TIER} (主 Claude 据此查推荐表)"

echo ""
echo "--- 根盘容量 ---"
df -h / 2>/dev/null
ROOT_FREE_MB=$(df -BM --output=avail / 2>/dev/null | tail -1 | tr -d ' M')
echo "根盘可用: ${ROOT_FREE_MB:-?} MB"

if ! command -v docker >/dev/null 2>&1; then
  echo ""
  echo "[i] Docker 未安装,跳过容器资源检查"
  exit 0
fi

echo ""
echo "--- 当前运行容器资源限制 (raw, 0=无限制) ---"
SUM_MEM_LIMIT=0
HAS_UNLIMITED_DB=0
docker ps -q 2>/dev/null | while read c; do
  name=$(docker inspect -f '{{.Name}}'                      "$c" 2>/dev/null | sed 's|^/||')
  image=$(docker inspect -f '{{.Config.Image}}'             "$c" 2>/dev/null)
  mem=$(docker inspect -f '{{.HostConfig.Memory}}'          "$c" 2>/dev/null)
  cpu_q=$(docker inspect -f '{{.HostConfig.CpuQuota}}'      "$c" 2>/dev/null)
  cpu_p=$(docker inspect -f '{{.HostConfig.CpuPeriod}}'     "$c" 2>/dev/null)
  shm=$(docker inspect -f '{{.HostConfig.ShmSize}}'         "$c" 2>/dev/null)
  pids=$(docker inspect -f '{{.HostConfig.PidsLimit}}'      "$c" 2>/dev/null)

  mem_mb=$(( mem / 1024 / 1024 ))
  shm_mb=$(( shm / 1024 / 1024 ))
  if [[ -n "$cpu_q" && "$cpu_q" != "0" && -n "$cpu_p" && "$cpu_p" != "0" ]]; then
    cpus=$(awk -v q="$cpu_q" -v p="$cpu_p" 'BEGIN{printf "%.2f", q/p}')
  else
    cpus="unlimited"
  fi

  printf "  %-32s image=%-40s mem_limit=%s cpus=%s shm=%sm pids=%s\n" \
    "$name" "$image" \
    "$([ "$mem" = "0" ] && echo 'unlimited' || echo "${mem_mb}m")" \
    "$cpus" "$shm_mb" "${pids:-unlimited}"

  # 关键服务无 mem_limit
  if [[ "$mem" == "0" ]] && echo "$image" | grep -qiE 'redis|postgres|mysql|mariadb|mongo|clickhouse|elasticsearch'; then
    echo "    [!!] HIGH: $name (image=$image) 未设 mem_limit, 异常时可能耗尽宿主内存"
  fi
done

echo ""
echo "--- 容器实际内存占用 (docker stats 单帧) ---"
timeout 8 docker stats --no-stream --format \
  'table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}' 2>/dev/null \
  || echo "[i] docker stats 超时或不可用"

echo ""
echo "--- Postgres 启动参数 (从 docker inspect Args 提取) ---"
PG_FOUND=0
for c in $(docker ps -q 2>/dev/null); do
  image=$(docker inspect -f '{{.Config.Image}}' "$c" 2>/dev/null)
  if echo "$image" | grep -qi "postgres"; then
    PG_FOUND=1
    name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
    # Cmd / Args 拼成空格分隔字符串
    cmd_str=$(docker inspect -f '{{range .Config.Cmd}}{{.}} {{end}}' "$c" 2>/dev/null)
    args_str=$(docker inspect -f '{{range .Args}}{{.}} {{end}}' "$c" 2>/dev/null)
    full="$cmd_str $args_str"

    echo ""
    echo "[$name] image=$image"
    # 从 -c key=value 提取 Postgres 调优参数
    for key in shared_buffers effective_cache_size work_mem maintenance_work_mem max_connections \
               wal_buffers max_wal_size random_page_cost log_min_duration_statement; do
      val=$(echo "$full" | grep -oE "${key}=[^ ]+" | head -1)
      printf "  %-30s %s\n" "$key" "${val:-(默认)}"
    done

    # 从 docker inspect 取 shm_size (Postgres 关键)
    shm=$(docker inspect -f '{{.HostConfig.ShmSize}}' "$c" 2>/dev/null)
    shm_mb=$(( shm / 1024 / 1024 ))
    if [[ "$shm_mb" -lt 128 ]]; then
      echo "  [!] MEDIUM: shm_size=${shm_mb}m 偏低 (大查询可能 'no space left on /dev/shm', 推荐 >=256m)"
    else
      echo "  [OK] shm_size=${shm_mb}m"
    fi

    # 校验 shared_buffers 是否过大
    sb_val=$(echo "$full" | grep -oE 'shared_buffers=[^ ]+' | head -1 | cut -d= -f2)
    if [[ -n "$sb_val" && -n "$MEM_TOTAL_MB" ]]; then
      sb_mb=$(echo "$sb_val" | awk '
        /[Gg][Bb]?$/ { sub(/[Gg][Bb]?$/,""); print $0*1024; next }
        /[Mm][Bb]?$/ { sub(/[Mm][Bb]?$/,""); print $0;      next }
        /[Kk][Bb]?$/ { sub(/[Kk][Bb]?$/,""); print $0/1024; next }
                     { print $0/1024/1024 }
      ')
      sb_mb=${sb_mb%.*}
      if [[ -n "$sb_mb" && "$sb_mb" -gt $((MEM_TOTAL_MB / 2)) ]]; then
        echo "  [!!] HIGH: shared_buffers=${sb_val} 已超过宿主总内存 50%, 易触发 OOM"
      fi
    fi
  fi
done
[[ "$PG_FOUND" == "0" ]] && echo "[i] 未发现 Postgres 容器"

echo ""
echo "--- Redis 启动参数 (从 docker inspect Args 提取) ---"
REDIS_FOUND=0
for c in $(docker ps -q 2>/dev/null); do
  image=$(docker inspect -f '{{.Config.Image}}' "$c" 2>/dev/null)
  if echo "$image" | grep -qi "redis"; then
    REDIS_FOUND=1
    name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
    cmd_str=$(docker inspect -f '{{range .Config.Cmd}}{{.}} {{end}}' "$c" 2>/dev/null)
    args_str=$(docker inspect -f '{{range .Args}}{{.}} {{end}}' "$c" 2>/dev/null)
    full="$cmd_str $args_str"

    echo ""
    echo "[$name] image=$image"
    # Redis 启动参数格式: --key value
    for key in maxmemory maxmemory-policy appendonly appendfsync save tcp-keepalive timeout; do
      # 把密码字段脱敏
      val=$(echo "$full" | grep -oE -- "--${key} [^ ]+" | head -1 | sed "s/^--${key} //")
      printf "  %-25s %s\n" "$key" "${val:-(默认/未设)}"
    done

    # 是否设了密码 (脱敏只看是否存在)
    if echo "$full" | grep -qE -- '--requirepass [^ ]+'; then
      echo "  requirepass               <REDACTED, 已设>"
    else
      echo "  requirepass               (未设, 见 check_db.sh CRITICAL)"
    fi

    # maxmemory 二元判定
    mm=$(echo "$full" | grep -oE -- '--maxmemory [^ ]+' | head -1 | awk '{print $2}')
    if [[ -z "$mm" || "$mm" == "0" ]]; then
      echo "  [!!!] CRITICAL: maxmemory 未设置或为 0, Redis 可能耗尽宿主内存"
    fi

    # appendonly + 检查 volume 是否挂载
    if ! echo "$full" | grep -qE -- '--appendonly +yes'; then
      echo "  [!] MEDIUM: 未启用 AOF, 重启会丢最近 RDB save 间隔内的数据"
    fi
  fi
done
[[ "$REDIS_FOUND" == "0" ]] && echo "[i] 未发现 Redis 容器"

echo ""
echo "--- compose 文件中的资源声明 (供人工核对) ---"
COMPOSE_FILES=$(sudo -n find /home /opt /srv /root -maxdepth 5 \
  \( -name "docker-compose*.yml" -o -name "compose*.yml" \) 2>/dev/null \
  | grep -vE '\.bak|\.old' | head -10)
[[ -z "$COMPOSE_FILES" ]] && COMPOSE_FILES=$(find /home /opt /srv /root -maxdepth 5 \
  \( -name "docker-compose*.yml" -o -name "compose*.yml" \) 2>/dev/null \
  | grep -vE '\.bak|\.old' | head -10)

for f in $COMPOSE_FILES; do
  echo ""
  echo "[$f]"
  grep -nE '^[[:space:]]+(mem_limit|mem_reservation|cpus|shm_size|memory|cpu_quota|--maxmemory|--maxmemory-policy|--appendonly|shared_buffers|effective_cache_size|work_mem)[[:space:]:]' \
    "$f" 2>/dev/null | head -30 \
    || echo "  (无资源声明)"
done

echo ""
echo "--- 日志兜底推荐档 (基于根盘 + 容器规模, 对照 SKILL.md 4.10) ---"
ROOT_TOTAL_MB=$(df -BM --output=size / 2>/dev/null | tail -1 | tr -d ' M')
ROOT_TOTAL_GB=$(( ${ROOT_TOTAL_MB:-0} / 1024 ))
RUNNING_COUNT=$(docker ps -q 2>/dev/null | wc -l | tr -d ' ')
echo "根盘容量: ${ROOT_TOTAL_GB} GB"
echo "运行容器数: ${RUNNING_COUNT}"

# 推荐档分级
if   [[ $ROOT_TOTAL_GB -lt 50 ]];   then REC_TIER="入门"; REC_SIZE="10m"; REC_FILE="3"
elif [[ $ROOT_TOTAL_GB -lt 150 ]]; then
  REC_TIER="标准"
  if [[ $RUNNING_COUNT -gt 5 ]]; then REC_SIZE="20m"; REC_FILE="5"
  else                                REC_SIZE="50m"; REC_FILE="5"; fi
else REC_TIER="大型"; REC_SIZE="100m"; REC_FILE="5"
fi
echo "推荐档: ${REC_TIER}"
echo "推荐 daemon log-opts: max-size=${REC_SIZE}, max-file=${REC_FILE}, compress=true"

# 拿当前 daemon.json log-opts (复用 check_docker.sh 的逻辑)
DAEMON_JSON=$(sudo -n cat /etc/docker/daemon.json 2>/dev/null \
              || cat /etc/docker/daemon.json 2>/dev/null || echo "")
CUR_SIZE=$(echo "$DAEMON_JSON" | grep -oE '"max-size"[[:space:]]*:[[:space:]]*"[^"]+"' \
            | head -1 | grep -oE '"[^"]+"$' | tr -d '"')
CUR_FILE=$(echo "$DAEMON_JSON" | grep -oE '"max-file"[[:space:]]*:[[:space:]]*"[^"]+"' \
            | head -1 | grep -oE '"[^"]+"$' | tr -d '"')
echo "当前 daemon.json: max-size=${CUR_SIZE:-(未配置)}, max-file=${CUR_FILE:-(未配置)}"

# 简单对比标记
if [[ -z "$CUR_SIZE" ]]; then
  echo "[!!!] CRITICAL: daemon 无 log-opts.max-size, 长跑容器日志会无限增长"
elif [[ "$CUR_SIZE" == "$REC_SIZE" ]]; then
  echo "[OK] max-size 与推荐档一致"
else
  echo "[i] 当前 max-size=${CUR_SIZE} 与推荐档 ${REC_SIZE} 不同 (主 Claude 据 SKILL.md 4.10 判定是否偏离 50%)"
fi

# 估算所有容器日志合计 quota = max-size × max-file × 容器数, 看占根盘比
# 不依赖 bc(部分镜像/最小系统不带), 用 awk 解析单位
if [[ -n "$CUR_SIZE" ]]; then
  size_mb=$(echo "$CUR_SIZE" | awk '
    BEGIN{IGNORECASE=1}
    /[gG]$/ { sub(/[gG]$/,""); print int($0*1024); exit }
    /[mM]$/ { sub(/[mM]$/,""); print int($0);      exit }
    /[kK]$/ { sub(/[kK]$/,""); print int($0/1024); exit }
            { print int($0); exit }
  ')
  file_n=${CUR_FILE:-1}
  total_quota_mb=$(( ${size_mb:-0} * file_n * RUNNING_COUNT ))
  if [[ "$ROOT_TOTAL_MB" -gt 0 ]]; then
    pct=$(( total_quota_mb * 100 / ROOT_TOTAL_MB ))
    echo "所有容器最大日志 quota 合计: ${total_quota_mb} MB (占根盘 ${pct}%, 期望 < 5%)"
    if [[ "$pct" -gt 5 ]]; then
      echo "[!!] HIGH: 日志 quota 合计 ${pct}% 已超根盘 5% 上限"
    fi
  fi
fi

echo ""
echo "--- 资源占比汇总 (供 Claude 校验 65% 上限规则) ---"
echo "宿主总内存: ${MEM_TOTAL_MB} MB"
TOTAL_LIMIT_MB=$(docker ps -q 2>/dev/null \
  | xargs -I{} docker inspect -f '{{.HostConfig.Memory}}' {} 2>/dev/null \
  | awk 'BEGIN{s=0} {s+=$1} END{print int(s/1024/1024)}')
echo "所有容器 mem_limit 合计: ${TOTAL_LIMIT_MB} MB"
if [[ "$MEM_TOTAL_MB" -gt 0 ]]; then
  pct=$(( TOTAL_LIMIT_MB * 100 / MEM_TOTAL_MB ))
  echo "占宿主总内存: ${pct}%"
  if [[ "$pct" -gt 75 ]]; then
    echo "[!!] HIGH: 容器硬限合计 > 75% 宿主内存, OS/nginx/监控 留 buffer 不足"
  elif [[ "$pct" -lt 30 ]]; then
    echo "[i] INFO: 容器硬限合计 < 30%, 可能资源利用不足"
  else
    echo "[OK] 容器硬限合计在 30%-75% 区间"
  fi
fi
REMOTE
