#!/usr/bin/env bash
# 环境变量与文件权限检查
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- 全局搜索 .env 文件位置 (限制深度,跳过 /proc /sys) ---"
sudo -n find /home /opt /srv /var/www /root /etc -maxdepth 6 -type f \
  \( -name ".env" -o -name ".env.*" -o -name "*.env" \) \
  ! -name "*.example" ! -name "*.sample" ! -name "*.template" \
  -printf "%M  %u:%g  %p  (%s bytes)\n" 2>/dev/null \
  || find /home /opt /srv /var/www -maxdepth 6 -type f \
       \( -name ".env" -o -name ".env.*" \) \
       ! -name "*.example" ! -name "*.sample" \
       -printf "%M  %u:%g  %p  (%s bytes)\n" 2>/dev/null \
  || echo "[!] 无 sudo,部分目录无法扫描"

echo ""
echo "--- nginx 静态根目录是否包含敏感文件 ---"
NGINX_DUMP=$(sudo -n nginx -T 2>/dev/null || nginx -T 2>/dev/null || true)
if [[ -n "$NGINX_DUMP" ]]; then
  ROOTS=$(echo "$NGINX_DUMP" | awk '/^[[:space:]]*root /{print $2}' | tr -d ';' | sort -u)
  for r in $ROOTS; do
    echo ">> root = $r"
    [[ -d "$r" ]] || { echo "  [!] 目录不存在或不可读"; continue; }
    for s in ".env" ".git" ".DS_Store" "package.json" "composer.json" "wp-config.php"; do
      if [[ -e "$r/$s" ]]; then
        echo "  [!] 暴露: $r/$s"
      fi
    done
  done
fi

echo ""
echo "--- 关键文件权限 ---"
for f in /etc/shadow /etc/passwd /etc/sudoers /etc/ssh/sshd_config /etc/nginx/nginx.conf; do
  ls -l "$f" 2>/dev/null || echo "  [i] $f 不可读"
done

echo ""
echo "--- 应用进程运行用户 (期望非 root) ---"
ps -eo user,pid,cmd --sort=user 2>/dev/null | grep -E "(node|python|uvicorn|gunicorn|java|php-fpm|fastapi|uwsgi)" | grep -v grep | head -20

echo ""
echo "--- sudo 免密配置 ---"
sudo -n cat /etc/sudoers 2>/dev/null | grep -v "^#" | grep -v "^$" | head -20 || echo "[i] 无 sudo 权限读取 /etc/sudoers"
sudo -n ls /etc/sudoers.d/ 2>/dev/null | head -10

echo ""
echo "--- 全局环境变量泄漏排查 (是否有密码/key 写在 /etc/environment 或 /etc/profile) ---"
for f in /etc/environment /etc/profile /etc/bash.bashrc; do
  if [[ -r "$f" ]]; then
    grep -iE "password|secret|token|api_key|apikey" "$f" 2>/dev/null \
      | sed -E 's/(password|secret|token|api[_-]?key)([^=]*=)([^[:space:]]+)/\1\2<REDACTED>/gi' \
      || true
  fi
done

echo ""
echo "--- crontab 中是否有可疑命令 ---"
sudo -n crontab -l 2>/dev/null | head -20 || crontab -l 2>/dev/null | head -20
echo "--- /etc/cron.d/ /etc/cron.daily/ ---"
ls /etc/cron.d/ /etc/cron.daily/ 2>/dev/null | head -20
REMOTE
