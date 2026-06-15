#!/usr/bin/env bash
# 数据库 (PostgreSQL / Redis) 暴露检查
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "########## PostgreSQL ##########"
if ! command -v psql >/dev/null 2>&1 && ! pgrep -f "postgres" >/dev/null 2>&1; then
  echo "[i] PostgreSQL 未安装/未运行,跳过"
else
  echo "--- 进程 ---"
  pgrep -af postgres | head -5

  echo ""
  echo "--- 监听端口 (期望: 仅 127.0.0.1 或内网) ---"
  (ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | grep -E ":(5432|5433)" || echo "[i] 未发现 5432/5433 监听"

  echo ""
  echo "--- 配置文件位置 ---"
  PG_CONF=$(sudo -n -u postgres psql -tAc "SHOW config_file" 2>/dev/null || \
            find /etc/postgresql /var/lib/pgsql /var/lib/postgresql -name postgresql.conf 2>/dev/null | head -1)
  PG_HBA=$(sudo -n -u postgres psql -tAc "SHOW hba_file" 2>/dev/null || \
            find /etc/postgresql /var/lib/pgsql /var/lib/postgresql -name pg_hba.conf 2>/dev/null | head -1)
  echo "postgresql.conf: ${PG_CONF:-未找到}"
  echo "pg_hba.conf:     ${PG_HBA:-未找到}"

  echo ""
  echo "--- postgresql.conf 关键项 ---"
  if [[ -r "$PG_CONF" ]]; then
    grep -E "^[[:space:]]*(listen_addresses|port|password_encryption|ssl|log_connections|log_disconnections|log_min_duration_statement)[[:space:]]*=" "$PG_CONF" 2>/dev/null
  else
    sudo -n cat "$PG_CONF" 2>/dev/null | grep -E "^[[:space:]]*(listen_addresses|password_encryption|ssl|log_connections)" || echo "[!] 配置不可读"
  fi

  echo ""
  echo "--- pg_hba.conf 认证方式 (期望: 无 trust) ---"
  if [[ -r "$PG_HBA" ]]; then
    grep -vE "^[[:space:]]*#|^[[:space:]]*$" "$PG_HBA" 2>/dev/null
  else
    sudo -n cat "$PG_HBA" 2>/dev/null | grep -vE "^[[:space:]]*#|^[[:space:]]*$" || echo "[!] pg_hba.conf 不可读"
  fi

  echo ""
  echo "--- PG 版本 & 数据库列表 ---"
  PG_VERSION_RAW=$(sudo -n -u postgres psql -tAc "SELECT version()" 2>/dev/null | head -1 || true)
  if [[ -n "$PG_VERSION_RAW" ]]; then
    echo "$PG_VERSION_RAW"
    PG_VERSION=$(echo "$PG_VERSION_RAW" | grep -oE 'PostgreSQL[[:space:]]+[0-9]+(\.[0-9]+){0,2}' | awk '{print $2}' | head -1)
    echo "postgresql_version_normalized=${PG_VERSION:-unknown}"
    echo "official_doc_pg_runtime=https://www.postgresql.org/docs/current/runtime-config-connection.html"
    if [[ -n "$PG_VERSION" ]]; then
      echo "search_hint_1=postgresql ${PG_VERSION} CVE"
      echo "search_hint_2=postgresql ${PG_VERSION} security advisory"
    fi
  else
    echo "[i] 无法连接 PG"
  fi
  sudo -n -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datistemplate=false" 2>/dev/null || true
fi

echo ""
echo "########## Redis ##########"
if ! command -v redis-cli >/dev/null 2>&1 && ! pgrep -f "redis-server" >/dev/null 2>&1; then
  echo "[i] Redis 未安装/未运行,跳过"
else
  echo "--- 进程 ---"
  pgrep -af redis-server | head -5

  echo ""
  echo "--- 监听端口 (期望: 仅 127.0.0.1 或内网) ---"
  (ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | grep -E ":(6379|6380)" || echo "[i] 未发现 6379/6380 监听"

  echo ""
  echo "--- redis.conf 位置与关键项 ---"
  REDIS_CONF=$(ps -eo cmd | grep "[r]edis-server" | grep -oE "/[^ ]+\.conf" | head -1)
  REDIS_CONF=${REDIS_CONF:-/etc/redis/redis.conf}
  echo "redis.conf: $REDIS_CONF"
  if [[ -r "$REDIS_CONF" ]]; then
    grep -E "^[[:space:]]*(bind|port|protected-mode|requirepass|rename-command|tls-port|maxmemory|maxmemory-policy)" "$REDIS_CONF" 2>/dev/null \
      | sed -E 's/(requirepass[[:space:]]+).*/\1<REDACTED>/'
  else
    sudo -n grep -E "^[[:space:]]*(bind|port|protected-mode|requirepass|rename-command|tls-port)" "$REDIS_CONF" 2>/dev/null \
      | sed -E 's/(requirepass[[:space:]]+).*/\1<REDACTED>/' || echo "[!] redis.conf 不可读"
  fi

  echo ""
  echo "--- maxmemory 判定 (运行时取值,优于 conf 文件) ---"
  MAXMEM=$(timeout 3 redis-cli -h 127.0.0.1 CONFIG GET maxmemory 2>/dev/null | tail -1)
  MAXMEM_POLICY=$(timeout 3 redis-cli -h 127.0.0.1 CONFIG GET maxmemory-policy 2>/dev/null | tail -1)
  if [[ -z "$MAXMEM" ]]; then
    echo "[i] redis-cli 无密码连接失败,从 conf 文件读取"
    MAXMEM=$(grep -E "^[[:space:]]*maxmemory[[:space:]]" "$REDIS_CONF" 2>/dev/null | awk '{print $2}' | tail -1)
    MAXMEM_POLICY=$(grep -E "^[[:space:]]*maxmemory-policy[[:space:]]" "$REDIS_CONF" 2>/dev/null | awk '{print $2}' | tail -1)
  fi
  echo "maxmemory: ${MAXMEM:-(未取得)}"
  echo "maxmemory-policy: ${MAXMEM_POLICY:-(未取得)}"

  TOTAL_MEM=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null)
  if [[ -n "$TOTAL_MEM" ]]; then
    TOTAL_MEM_BYTES=$((TOTAL_MEM * 1024))
    echo "服务器总内存: $((TOTAL_MEM / 1024)) MB ($TOTAL_MEM_BYTES bytes)"
  fi

  if [[ "$MAXMEM" == "0" || -z "$MAXMEM" ]]; then
    echo "[!!!] HIGH: maxmemory=0(无上限),Redis 可能耗尽服务器内存触发 OOM kill"
    echo "      建议: 设置为服务器物理内存的 50%-70% (CONFIG SET maxmemory <bytes>)"
  else
    echo "[OK] maxmemory 已设置"
    if [[ "$MAXMEM_POLICY" == "noeviction" ]]; then
      echo "[!] INFO: maxmemory-policy=noeviction,达到上限时拒写但不淘汰,业务方需感知"
    fi
  fi

  echo ""
  echo "--- 尝试无密码连接 (如能成功 → CRITICAL) ---"
  if timeout 3 redis-cli -h 127.0.0.1 ping 2>/dev/null | grep -q PONG; then
    echo "[!!!] CRITICAL: Redis 127.0.0.1 无密码可连!"
  else
    echo "[OK] 无密码连接被拒绝"
  fi

  echo ""
  echo "--- Redis INFO server (需 auth, 跳过若失败) ---"
  REDIS_INFO=$(timeout 3 redis-cli -h 127.0.0.1 INFO server 2>/dev/null || true)
  if [[ -n "$REDIS_INFO" ]]; then
    echo "$REDIS_INFO" | grep -E "redis_version|os|arch_bits" | head -5
    REDIS_VERSION=$(echo "$REDIS_INFO" | sed -n 's/^redis_version://p' | head -1)
    echo "redis_version_normalized=${REDIS_VERSION:-unknown}"
    echo "official_doc_redis_security=https://redis.io/docs/latest/operate/oss_and_stack/management/security/"
    if [[ -n "$REDIS_VERSION" ]]; then
      echo "search_hint_redis_1=redis ${REDIS_VERSION} CVE"
      echo "search_hint_redis_2=redis ${REDIS_VERSION} security advisory"
    fi
  else
    echo "[i] 需要密码或无法连接"
    echo "official_doc_redis_security=https://redis.io/docs/latest/operate/oss_and_stack/management/security/"
  fi
fi

echo ""
echo "########## 公网可达性自测 ##########"
PUB_IP=$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null)
echo "公网 IP (best effort): ${PUB_IP:-unknown}"
if [[ -n "$PUB_IP" ]]; then
  echo "[i] 注意: 真实公网可达性需从外网测试,此处仅本机视角"
fi
REMOTE
