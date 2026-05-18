#!/usr/bin/env bash
# 依赖服务连通性 / 防火墙
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- 防火墙状态 ---"
if command -v ufw >/dev/null 2>&1; then
  echo "[ufw]"
  sudo -n ufw status verbose 2>/dev/null || echo "  [!] 需 sudo 查看 ufw"
fi
if command -v firewall-cmd >/dev/null 2>&1; then
  echo "[firewalld]"
  sudo -n firewall-cmd --state 2>/dev/null
  sudo -n firewall-cmd --list-all 2>/dev/null
fi
echo "[iptables]"
sudo -n iptables -L INPUT -n --line-numbers 2>/dev/null | head -20 || echo "  [i] 无法读取 iptables"

echo ""
echo "--- 监听端口 (按地址分组) ---"
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | awk 'NR>1 {print $4}' | awk -F: '{
  port=$NF;
  ip=substr($0,1,length($0)-length(port)-1);
  if (ip=="0.0.0.0" || ip=="*" || ip=="[::]") public[port]++;
  else if (ip=="127.0.0.1" || ip=="[::1]") loop[port]++;
  else internal[port]++;
}
END {
  print "公网监听 (0.0.0.0 / *):"
  for (p in public) print "  " p
  print "内网监听 (具体 IP):"
  for (p in internal) print "  " p
  print "回环监听 (127.0.0.1):"
  for (p in loop) print "  " p
}'

echo ""
echo "--- 系统负载与内存 ---"
uptime
free -h 2>/dev/null | head -3

echo ""
echo "--- 磁盘 ---"
df -h | grep -vE "tmpfs|udev" | head -10

echo ""
echo "--- 已安装的 Web 应用进程 (常见) ---"
ps -eo user,pid,%cpu,%mem,cmd --sort=-%mem 2>/dev/null \
  | grep -E "(nginx|node|python|uvicorn|gunicorn|java|php-fpm|redis-server|postgres|mysql|mongod)" \
  | grep -v grep | head -20

echo ""
echo "--- 应用健康检查端点 (常见路径自测) ---"
NGINX_DUMP=$(sudo -n nginx -T 2>/dev/null || nginx -T 2>/dev/null || true)
DOMAINS=$(echo "$NGINX_DUMP" | awk '/server_name/ {for(i=2;i<=NF;i++) print $i}' | tr -d ';' | sort -u | grep -v "^_$" | head -3)
[[ -z "$DOMAINS" ]] && DOMAINS="localhost"
for D in $DOMAINS; do
  for path in "/health" "/api/health" "/healthz" "/_health" "/status"; do
    code=$(curl -k -sS -o /dev/null -w "%{http_code}" --max-time 3 "https://$D$path" 2>/dev/null || echo "000")
    [[ "$code" != "404" && "$code" != "000" ]] && printf "  https://%s%s -> %s\n" "$D" "$path" "$code"
  done
done

echo ""
echo "--- 系统更新提示 ---"
if command -v apt >/dev/null 2>&1; then
  sudo -n apt list --upgradable 2>/dev/null | head -10 || echo "  [i] 无法检查 apt 更新"
elif command -v yum >/dev/null 2>&1; then
  sudo -n yum check-update 2>/dev/null | head -10 || echo "  [i] 无法检查 yum 更新"
fi

echo ""
echo "--- 内核/系统启动时间 ---"
who -b 2>/dev/null
echo "kernel: $(uname -r)"
REMOTE
