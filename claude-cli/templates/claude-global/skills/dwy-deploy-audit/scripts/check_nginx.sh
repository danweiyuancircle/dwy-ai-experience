#!/usr/bin/env bash
# Nginx 配置检查 (只读)
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
if ! command -v nginx >/dev/null 2>&1; then
  echo "[i] nginx 未安装,跳过"
  exit 0
fi

echo "--- nginx version ---"
nginx -v 2>&1

echo ""
echo "--- nginx 进程运行用户 ---"
ps -eo user,pid,cmd | grep "[n]ginx: master" | head -1

echo ""
echo "--- nginx -T (effective config, 需 sudo 或 nginx 用户可读) ---"
NGINX_DUMP=$(sudo -n nginx -T 2>/dev/null || nginx -T 2>/dev/null || true)
if [[ -z "$NGINX_DUMP" ]]; then
  echo "[!] 无法 dump nginx 配置,改读 /etc/nginx/"
  ls -la /etc/nginx/ 2>/dev/null
  echo "--- /etc/nginx/nginx.conf (head) ---"
  head -80 /etc/nginx/nginx.conf 2>/dev/null
  echo "--- sites-enabled / conf.d ---"
  for d in /etc/nginx/sites-enabled /etc/nginx/conf.d; do
    [[ -d "$d" ]] && ls -la "$d" 2>/dev/null
  done
else
  echo "$NGINX_DUMP" | grep -E "^# configuration file" | head -20
  echo ""
  echo "--- KEY DIRECTIVES (filtered from nginx -T) ---"
  echo "$NGINX_DUMP" | grep -Ei "^[[:space:]]*(listen|server_name|return|rewrite|ssl_protocols|ssl_ciphers|ssl_prefer_server_ciphers|ssl_certificate|ssl_certificate_key|server_tokens|access_log|error_log|client_max_body_size|client_body_timeout|add_header|autoindex|location|root|alias|proxy_pass)" \
    | grep -v "^[[:space:]]*#" | head -200

  echo ""
  echo "--- HSTS / Security Headers 检查 ---"
  echo "$NGINX_DUMP" | grep -i "Strict-Transport-Security\|X-Frame-Options\|X-Content-Type-Options\|Content-Security-Policy\|Referrer-Policy" || echo "[!] 未找到任何安全 header"

  echo ""
  echo "--- HTTP→HTTPS 跳转检查 ---"
  echo "$NGINX_DUMP" | awk '/listen[[:space:]]+80/,/}/' | grep -i "return\|rewrite" | head -10 || echo "[!] 80 端口可能未配置强制跳转"

  echo ""
  echo "--- server_tokens ---"
  echo "$NGINX_DUMP" | grep -E "^[[:space:]]*server_tokens" || echo "[!] server_tokens 未显式配置 (默认 on,会暴露版本)"

  echo ""
  echo "--- access_log / error_log ---"
  echo "$NGINX_DUMP" | grep -E "^[[:space:]]*(access_log|error_log)" | head -10

  echo ""
  echo "--- client_max_body_size (对齐 dwy-payload-limits) ---"
  echo "$NGINX_DUMP" | grep -E "^[[:space:]]*client_max_body_size" || echo "[!] 未显式配置 client_max_body_size"
fi

echo ""
echo "--- nginx 配置语法检查 ---"
sudo -n nginx -t 2>&1 || nginx -t 2>&1 || echo "[i] 无法执行 nginx -t"

echo ""
echo "--- 危险路径暴露快测 (本机回环) ---"
for path in "/.env" "/.git/HEAD" "/.git/config" "/admin" "/phpmyadmin" "/.DS_Store"; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 3 "https://localhost${path}" 2>/dev/null || echo "000")
  printf "  %-20s -> https://localhost  HTTP %s\n" "$path" "$code"
done
REMOTE
