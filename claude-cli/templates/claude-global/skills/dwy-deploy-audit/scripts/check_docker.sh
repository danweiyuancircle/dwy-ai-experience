#!/usr/bin/env bash
# Docker 安全检查
TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
if ! command -v docker >/dev/null 2>&1; then
  echo "[i] Docker 未安装,跳过"
  exit 0
fi

echo "--- docker version ---"
docker version --format '{{.Server.Version}} (client: {{.Client.Version}})' 2>/dev/null || docker --version

echo ""
echo "--- docker daemon 监听 ---"
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | grep -E ":(2375|2376)" \
  && echo "[!!!] CRITICAL: Docker daemon 暴露 TCP 端口" \
  || echo "[OK] Docker daemon 未暴露 TCP 端口"

echo ""
echo "--- 运行中容器列表 ---"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null

echo ""
echo "--- 容器端口绑定 (期望: 内部服务不暴露 0.0.0.0) ---"
docker ps --format "{{.Names}}|{{.Ports}}" 2>/dev/null | while IFS='|' read -r name ports; do
  if echo "$ports" | grep -qE "0\.0\.0\.0:(5432|6379|3306|27017|9200|11211)"; then
    echo "  [!!!] $name 暴露内部服务端口到 0.0.0.0: $ports"
  else
    echo "  [OK] $name $ports"
  fi
done

echo ""
echo "--- 镜像 tag 检查 (生产期望非 :latest) ---"
docker ps --format "{{.Names}}\t{{.Image}}" 2>/dev/null | awk -F'\t' '
{
  img=$2
  if (img ~ /:latest$/ || img !~ /:/) {
    print "  [!] " $1 "  使用 :latest 或无 tag → " img
  } else {
    print "  [OK] " $1 "  " img
  }
}'

echo ""
echo "--- 容器是否以 root 运行 ---"
for c in $(docker ps -q 2>/dev/null); do
  name=$(docker inspect -f '{{.Name}}' "$c" | sed 's|^/||')
  user=$(docker inspect -f '{{.Config.User}}' "$c")
  user="${user:-root}"
  if [[ "$user" == "root" || "$user" == "0" || "$user" == "0:0" ]]; then
    echo "  [!] $name  以 root 运行 (User=${user})"
  else
    echo "  [OK] $name  user=$user"
  fi
done

echo ""
echo "--- 特权容器检查 ---"
for c in $(docker ps -q 2>/dev/null); do
  name=$(docker inspect -f '{{.Name}}' "$c" | sed 's|^/||')
  priv=$(docker inspect -f '{{.HostConfig.Privileged}}' "$c")
  caps=$(docker inspect -f '{{.HostConfig.CapAdd}}' "$c")
  if [[ "$priv" == "true" ]]; then
    echo "  [!!!] $name  --privileged"
  fi
  if [[ "$caps" != "[]" && "$caps" != "<no value>" ]]; then
    echo "  [!] $name  额外 capabilities: $caps"
  fi
done

echo ""
echo "--- docker.sock 挂载检查 ---"
for c in $(docker ps -q 2>/dev/null); do
  name=$(docker inspect -f '{{.Name}}' "$c" | sed 's|^/||')
  mounts=$(docker inspect -f '{{range .Mounts}}{{.Source}}->{{.Destination}} {{end}}' "$c")
  if echo "$mounts" | grep -q "docker.sock"; then
    echo "  [!!!] $name  挂载了 docker.sock: $mounts"
  fi
done

echo ""
echo "--- docker daemon 配置 ---"
sudo -n cat /etc/docker/daemon.json 2>/dev/null || cat /etc/docker/daemon.json 2>/dev/null || echo "[i] 无 daemon.json 或不可读"

echo ""
echo "--- docker compose 文件位置 (用于人工核查) ---"
sudo -n find /home /opt /srv /root -maxdepth 5 -name "docker-compose*.yml" -o -name "compose.yml" 2>/dev/null | head -10
REMOTE
