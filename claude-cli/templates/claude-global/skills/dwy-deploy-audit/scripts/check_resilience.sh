#!/usr/bin/env bash
# 自愈能力 / 资源耗尽防护检查 (只读)
#
# 检查范围:
#   B 类: 系统服务开机自启 (sshd / nginx / docker / postgres / redis / frps / fail2ban / 自定义)
#   D 类: 资源耗尽防护 (swap / ulimit / logrotate / 磁盘使用率 / 应用进程内存上限)
#
# 服务器意外重启后,这些配置决定了服务能否自动恢复;资源耗尽场景决定了
# 服务能否在异常下保住基本运行而不被全局拖垮。

TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "########## B. 系统服务开机自启 ##########"

# 默认必检清单
DEFAULT_SERVICES=(sshd ssh nginx docker docker.socket postgresql postgres redis redis-server fail2ban frps frpc supervisor crond cron)

echo "--- 默认必检清单 ---"
for svc in "${DEFAULT_SERVICES[@]}"; do
  # systemctl status 区分: not-found / disabled / enabled / static / masked
  enabled=$(systemctl is-enabled "$svc" 2>/dev/null || echo "n/a")
  active=$(systemctl is-active "$svc" 2>/dev/null || echo "n/a")
  if [[ "$enabled" == "n/a" && "$active" == "n/a" ]]; then
    continue  # 该服务未安装,跳过
  fi
  case "$enabled" in
    enabled|enabled-runtime|alias|static)
      icon="[OK]" ;;
    disabled)
      icon="[!!!] CRITICAL: 已部署但未开机自启,服务器重启后不会启动" ;;
    masked)
      icon="[!!!] CRITICAL: 服务被 mask,无法启动" ;;
    *)
      icon="[?] enabled=$enabled" ;;
  esac
  printf "  %-20s active=%-10s enabled=%-12s %s\n" "$svc" "$active" "$enabled" "$icon"
done

echo ""
echo "--- 自动探测: 当前 enabled 的所有 unit (供人工核对应用主进程是否在内) ---"
systemctl list-unit-files --type=service --state=enabled 2>/dev/null \
  | awk 'NR>1 && $1 != "" {print "  " $1}' \
  | head -40 || echo "[i] 无法列出 unit-files"

echo ""
echo "--- 自动探测: 当前 running 但 disabled 的服务 (重启后会消失) ---"
running_services=$(systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | awk '{print $1}')
for svc in $running_services; do
  enabled=$(systemctl is-enabled "$svc" 2>/dev/null)
  if [[ "$enabled" == "disabled" ]]; then
    echo "  [!!] $svc  正在运行但 disabled,重启后会丢失"
  fi
done


echo ""
echo "########## D. 资源耗尽防护 ##########"

echo "--- 内存与 swap ---"
free -h 2>/dev/null || vmstat -s 2>/dev/null | head -10
SWAP_SIZE=$(awk '/SwapTotal/ {print $2}' /proc/meminfo 2>/dev/null)
if [[ -z "$SWAP_SIZE" || "$SWAP_SIZE" == "0" ]]; then
  echo "[!] MEDIUM: 未配置 swap,内存吃紧时直接 OOM kill"
  echo "      建议: 至少配置 1-2GB swap (fallocate / dd + mkswap + swapon + /etc/fstab)"
else
  echo "[OK] swap 已配置: $((SWAP_SIZE / 1024)) MB"
fi

echo ""
echo "--- 根分区使用率 ---"
df -h / 2>/dev/null
ROOT_USE=$(df / --output=pcent 2>/dev/null | tail -1 | tr -d ' %')
if [[ -n "$ROOT_USE" ]]; then
  if [[ "$ROOT_USE" -ge 90 ]]; then
    echo "[!!!] CRITICAL: 根分区使用率 ${ROOT_USE}%, 即将写满"
  elif [[ "$ROOT_USE" -ge 80 ]]; then
    echo "[!] MEDIUM: 根分区使用率 ${ROOT_USE}%, 建议清理"
  else
    echo "[OK] 根分区使用率 ${ROOT_USE}%"
  fi
fi

echo ""
echo "--- /var/log 与 /var/lib/docker 大小 ---"
sudo -n du -sh /var/log /var/lib/docker /var/lib/postgresql 2>/dev/null \
  || du -sh /var/log /var/lib/docker /var/lib/postgresql 2>/dev/null \
  || echo "[i] 部分目录不可读"

echo ""
echo "--- logrotate 配置 ---"
if [[ -f /etc/logrotate.conf ]]; then
  echo "[OK] /etc/logrotate.conf 存在"
  ls /etc/logrotate.d/ 2>/dev/null | head -20 | sed 's|^|  |'
else
  echo "[!] HIGH: /etc/logrotate.conf 不存在,日志可能无限增长"
fi

# 关键服务是否有 logrotate 规则
echo ""
echo "--- 关键服务 logrotate 规则 ---"
for app in nginx postgresql redis docker rsyslog; do
  if [[ -f "/etc/logrotate.d/$app" ]]; then
    echo "  [OK] /etc/logrotate.d/$app"
  else
    if systemctl is-enabled "$app" >/dev/null 2>&1 || systemctl is-enabled "${app}-server" >/dev/null 2>&1; then
      echo "  [!] $app 已部署但无 logrotate 规则"
    fi
  fi
done

echo ""
echo "--- 文件描述符上限 (system + 关键服务) ---"
echo "  系统 fs.file-max:    $(sysctl -n fs.file-max 2>/dev/null)"
echo "  系统 fs.nr_open:     $(sysctl -n fs.nr_open 2>/dev/null)"
for app in nginx postgres redis-server; do
  pid=$(pgrep -f "[${app:0:1}]${app:1}" | head -1)
  if [[ -n "$pid" ]]; then
    soft=$(awk '/Max open files/ {print $4}' /proc/$pid/limits 2>/dev/null)
    hard=$(awk '/Max open files/ {print $5}' /proc/$pid/limits 2>/dev/null)
    echo "  $app (pid $pid): soft=$soft hard=$hard"
    if [[ -n "$soft" && "$soft" -lt 4096 ]]; then
      echo "    [!] MEDIUM: ulimit -n 偏低 ($soft),高并发场景可能耗尽"
    fi
  fi
done

echo ""
echo "--- /etc/security/limits.conf 自定义条目 ---"
sudo -n grep -vE "^[[:space:]]*#|^[[:space:]]*$" /etc/security/limits.conf 2>/dev/null \
  || grep -vE "^[[:space:]]*#|^[[:space:]]*$" /etc/security/limits.conf 2>/dev/null \
  || echo "[i] limits.conf 不可读"
ls /etc/security/limits.d/ 2>/dev/null | sed 's|^|  /etc/security/limits.d/|'

echo ""
echo "--- 内存压力指标 (PSI) ---"
if [[ -r /proc/pressure/memory ]]; then
  cat /proc/pressure/memory
else
  echo "[i] PSI 不可用 (内核 < 4.20 或未启用)"
fi

echo ""
echo "--- 关键容器内存上限 (避免容器吃掉宿主机) ---"
if command -v docker >/dev/null 2>&1; then
  docker ps -q 2>/dev/null | while read c; do
    name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
    mem=$(docker inspect -f '{{.HostConfig.Memory}}' "$c" 2>/dev/null)
    if [[ "$mem" == "0" ]]; then
      echo "  [!] $name  无内存上限,异常时可能耗尽宿主机"
    else
      echo "  [OK] $name  Memory=$((mem / 1024 / 1024)) MB"
    fi
  done
fi
REMOTE
