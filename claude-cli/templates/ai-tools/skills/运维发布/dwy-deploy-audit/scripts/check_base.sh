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
curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}'
echo

echo "--- USER & SUDO ---"
id
sudo -n -l 2>/dev/null | head -5 || echo "no passwordless sudo"
REMOTE
