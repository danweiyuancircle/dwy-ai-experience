#!/usr/bin/env bash
# HTTPS / SSL 证书检查
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
echo "--- 检测可能的 HTTPS 站点 (从 nginx 配置) ---"
DOMAINS=()
NGINX_DUMP=$(sudo -n nginx -T 2>/dev/null || nginx -T 2>/dev/null || true)
if [[ -n "$NGINX_DUMP" ]]; then
  while IFS= read -r d; do
    [[ -n "$d" && "$d" != "_" && "$d" != "localhost" ]] && DOMAINS+=("$d")
  done < <(echo "$NGINX_DUMP" | awk '/server_name/ {for(i=2;i<=NF;i++) print $i}' | tr -d ';' | sort -u)
fi

if [[ ${#DOMAINS[@]} -eq 0 ]]; then
  DOMAINS+=("localhost")
fi

echo "目标域名: ${DOMAINS[*]}"

for D in "${DOMAINS[@]}"; do
  echo ""
  echo "===== $D ====="

  echo "--- HTTPS 可达性 ---"
  HTTPS_CODE=$(curl -k -sS -o /dev/null -w "%{http_code}" --max-time 5 "https://$D" 2>/dev/null || echo "000")
  HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code} -> %{redirect_url}" --max-time 5 "http://$D" 2>/dev/null || echo "000")
  echo "  https://$D  -> HTTP $HTTPS_CODE"
  echo "  http://$D   -> HTTP $HTTP_CODE"

  echo "--- 证书信息 ---"
  CERT=$(echo | timeout 5 openssl s_client -servername "$D" -connect "${D}:443" -showcerts 2>/dev/null </dev/null)
  if [[ -z "$CERT" ]]; then
    echo "  [!] 无法获取证书 (可能未启用 HTTPS 或域名无 DNS)"
    continue
  fi
  echo "$CERT" | openssl x509 -noout -subject -issuer -dates 2>/dev/null

  echo "--- SAN ---"
  echo "$CERT" | openssl x509 -noout -ext subjectAltName 2>/dev/null | grep -i "DNS:" | head -3

  echo "--- 剩余天数 ---"
  END=$(echo "$CERT" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  if [[ -n "$END" ]]; then
    END_TS=$(date -d "$END" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$END" +%s 2>/dev/null)
    NOW_TS=$(date +%s)
    if [[ -n "$END_TS" ]]; then
      DAYS=$(( (END_TS - NOW_TS) / 86400 ))
      echo "  剩余 $DAYS 天 (过期时间: $END)"
    fi
  fi

  echo "--- TLS 协议支持 ---"
  for proto in tls1 tls1_1 tls1_2 tls1_3; do
    R=$(echo | timeout 3 openssl s_client -"$proto" -connect "${D}:443" 2>&1 </dev/null | grep -E "Protocol|handshake failure|wrong version" | head -1)
    printf "  %-8s %s\n" "$proto" "$R"
  done
done
REMOTE
