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
echo "--- 应用健康检查端点 (经本地 nginx 回环 + --resolve, 避免 hairpin NAT) ---"
NGINX_DUMP=$(sudo -n nginx -T 2>/dev/null || nginx -T 2>/dev/null || true)
# 只取真实 server_name 指令行(行首仅空白 + 关键字), 去行内注释, 拆多域名, 过滤 _ / 通配 / 空 / 非法 token
# 旧实现用 awk '/server_name/' 会误匹配注释行里的 server_name 文字, 产出 _) 1. :80 等垃圾域名
DOMAINS=$(echo "$NGINX_DUMP" \
  | grep -E '^[[:space:]]*server_name[[:space:]]' \
  | sed -E 's/#.*$//; s/^[[:space:]]*server_name[[:space:]]+//; s/;.*$//' \
  | tr ' ' '\n' \
  | grep -E '^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$' \
  | grep -v '^_$' \
  | sort -u | head -5)
[[ -z "$DOMAINS" ]] && DOMAINS="localhost"
# 是否启用 https(443 在监听); 公网域名从本机直连会触发 hairpin NAT 返回 000,
# 用 --resolve 把域名钉到回环, 既走本地 nginx 又匹配 SNI 证书, 才是白盒正解
HAS_HTTPS=$( (ss -tln 2>/dev/null || netstat -tln 2>/dev/null) | grep -qE ':443[[:space:]]' && echo yes || echo no )
for D in $DOMAINS; do
  for path in "/api/health" "/health" "/healthz" "/_health" "/status"; do
    if [[ "$HAS_HTTPS" == "yes" ]]; then
      code=$(curl -k -sS -o /dev/null -w "%{http_code}" --max-time 3 --resolve "$D:443:127.0.0.1" "https://$D$path" 2>/dev/null || echo "000")
      scheme="https"
    else
      code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 3 --resolve "$D:80:127.0.0.1" "http://$D$path" 2>/dev/null || echo "000")
      scheme="http"
    fi
    [[ "$code" != "404" && "$code" != "000" ]] && printf "  %s://%s%s -> %s\n" "$scheme" "$D" "$path" "$code"
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
