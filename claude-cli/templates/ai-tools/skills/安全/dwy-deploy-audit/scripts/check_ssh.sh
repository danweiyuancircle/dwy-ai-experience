#!/usr/bin/env bash
# SSH 安全检查 (只读)
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- /etc/ssh/sshd_config (filtered key directives) ---"
SSHD_CONF="/etc/ssh/sshd_config"
SSHD_DIR="/etc/ssh/sshd_config.d"
if [[ -r "$SSHD_CONF" ]]; then
  grep -Ei "^[[:space:]]*(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|PermitEmptyPasswords|Port|Protocol|MaxAuthTries|LoginGraceTime|AllowUsers|AllowGroups|DenyUsers|DenyGroups|ChallengeResponseAuthentication|UsePAM|X11Forwarding|ClientAliveInterval|ClientAliveCountMax|LogLevel|Banner)" "$SSHD_CONF" 2>/dev/null
  if [[ -d "$SSHD_DIR" ]]; then
    echo "--- $SSHD_DIR/*.conf ---"
    grep -EiH "^[[:space:]]*(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|PermitEmptyPasswords|Port|Protocol|MaxAuthTries)" "$SSHD_DIR"/*.conf 2>/dev/null
  fi
else
  echo "[!] $SSHD_CONF 不可读 (需要 sudo)"
fi

echo ""
echo "--- effective sshd config (sshd -T, 需 sudo) ---"
sudo -n sshd -T 2>/dev/null | grep -Ei "^(permitrootlogin|passwordauthentication|pubkeyauthentication|permitemptypasswords|port|protocol|maxauthtries|logingracetime|allowusers|allowgroups|x11forwarding|loglevel)" || echo "[i] 无法读取 effective config (需要 sudo 或 sshd -T 不可用)"

echo ""
echo "--- ssh process & version ---"
sshd -V 2>&1 | head -2 || ssh -V 2>&1

echo ""
echo "--- recent failed logins (last 20) ---"
sudo -n journalctl _COMM=sshd --since "7 days ago" 2>/dev/null | grep -Ei "failed|invalid" | tail -20 \
  || sudo -n grep -Ei "failed|invalid" /var/log/auth.log 2>/dev/null | tail -20 \
  || echo "[i] 无法读取认证日志 (需要 sudo)"

echo ""
echo "--- fail2ban status ---"
if command -v fail2ban-client >/dev/null 2>&1; then
  sudo -n fail2ban-client status 2>/dev/null || echo "[i] fail2ban 已安装,但需要 sudo 查看状态"
else
  echo "[!] fail2ban 未安装"
fi

echo ""
echo "--- authorized_keys 概览 (当前用户) ---"
if [[ -r ~/.ssh/authorized_keys ]]; then
  awk '{print "  key: " $1 " " substr($2,1,16) "... " $3}' ~/.ssh/authorized_keys
  echo "  total: $(wc -l < ~/.ssh/authorized_keys) keys"
else
  echo "[i] 当前用户无 authorized_keys"
fi

echo ""
echo "--- /root/.ssh/authorized_keys (需 sudo) ---"
sudo -n test -f /root/.ssh/authorized_keys 2>/dev/null && \
  echo "  [!] root 用户存在 authorized_keys, 共 $(sudo -n wc -l < /root/.ssh/authorized_keys 2>/dev/null) 行" \
  || echo "[i] 无 root authorized_keys 或无 sudo 权限"
REMOTE
