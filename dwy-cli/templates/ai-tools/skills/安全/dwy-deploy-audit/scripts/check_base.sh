#!/usr/bin/env bash
# 基础环境识别: OS / 监听端口 / 运行服务 / Docker
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- OS ---"
cat /etc/os-release 2>/dev/null | grep -E "^(NAME|VERSION|ID)=" || echo "unknown"
uname -a

echo "--- KERNEL ---"
uname -r

echo "--- LISTENING PORTS (TCP) ---"
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | head -50

echo "--- LISTENING PORTS (UDP) ---"
(ss -ulnp 2>/dev/null || netstat -ulnp 2>/dev/null) | head -30

echo "--- ESTABLISHED CONNECTIONS (sample) ---"
(ss -tn state established 2>/dev/null || netstat -tn 2>/dev/null) | head -20

echo "--- RUNNING SERVICES ---"
systemctl list-units --type=service --state=running --no-pager 2>/dev/null | head -40

echo "--- INSTALLED RELEVANT BINARIES ---"
for cmd in nginx postgres psql redis-cli docker openssl ufw firewall-cmd iptables fail2ban-client; do
  path=$(command -v "$cmd" 2>/dev/null || true)
  printf "  %-20s %s\n" "$cmd" "${path:-<not installed>}"
done

echo "--- PUBLIC IP (best effort) ---"
# 回显地址是先验。一个失败换下一个。全部失败印 unknown。禁止用 hostname -I 的内网地址冒充公网 IP。
PUB_IP=""
for url in https://api.ipify.org https://ifconfig.me/ip https://icanhazip.com; do
  PUB_IP=$(curl -fsS --max-time 5 "$url" 2>/dev/null | tr -d '[:space:]')
  if printf '%s' "$PUB_IP" | grep -Eq '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'; then
    break
  fi
  PUB_IP=""
done
echo "${PUB_IP:-unknown}"
echo

echo "--- USER & SUDO ---"
id
sudo -n -l 2>/dev/null | head -5 || echo "no passwordless sudo"
REMOTE
