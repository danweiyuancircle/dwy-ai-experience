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
DOCKER_SERVER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null || docker --version | grep -oE '[0-9]+(\.[0-9]+){1,3}' | head -1)
echo "docker_server_version_normalized=${DOCKER_SERVER_VERSION:-unknown}"
echo "official_doc_docker_security=https://docs.docker.com/engine/security/"
echo "official_doc_docker_remote_access=https://docs.docker.com/engine/daemon/remote-access/"
echo "official_doc_docker_logging=https://docs.docker.com/engine/logging/configure/"
echo "official_doc_docker_owasp=https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html"
if [[ -n "$DOCKER_SERVER_VERSION" ]]; then
  echo "search_hint_1=docker engine ${DOCKER_SERVER_VERSION} CVE"
  echo "search_hint_2=docker ${DOCKER_SERVER_VERSION} security advisory"
fi

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
echo "--- 镜像 tag 分级检查 (生产期望: 固定到具体 patch, 跑 /dwy-docker-image 选 N-1 minor) ---"
# 浮动 tag 黑名单 (无版本号或仅描述类的)
FLOATING_TAGS='^(latest|stable|mainline|edge|current|alpine|slim|bookworm|bullseye|buster|jammy|focal|noble|nightly)$'
docker ps --format "{{.Names}}|{{.Image}}" 2>/dev/null | while IFS='|' read -r name image; do
  # 拆 image 与 tag (注意 image 可能含 registry 域名如 ghcr.io/foo/bar:tag)
  if [[ "$image" == *"@sha256:"* ]]; then
    # tag@digest 形式 → digest 钉死, 最严格
    echo "  [OK+] $name  digest 钉死: $image"
    continue
  fi
  # 取最后一个冒号后内容当 tag (port 形式 registry:5000/foo:tag 也只取最后)
  base="${image%:*}"
  tag="${image##*:}"
  if [[ "$base" == "$image" ]]; then
    # 没有冒号 → 无 tag (等同 :latest)
    echo "  [!!!] CRITICAL $name  $image  省略 tag (等同 :latest), 不可重现"
    continue
  fi
  # 提取 tag 起始的语义版本前缀, 支持 "X" / "X.Y" / "X.Y.Z" / "X.Y.Z-suffix"
  ver_prefix=$(echo "$tag" | grep -oE '^[0-9]+(\.[0-9]+){0,3}')
  if [[ -n "$ver_prefix" ]]; then
    seg_count=$(echo "$ver_prefix" | awk -F. '{print NF}')
  else
    seg_count=0
  fi

  if [[ "$tag" == "latest" ]]; then
    echo "  [!!!] CRITICAL $name  $image  使用 :latest"
  elif echo "$tag" | grep -qE "$FLOATING_TAGS"; then
    echo "  [!!] HIGH    $name  $image  浮动 tag :$tag (随上游漂移)"
  elif [[ "$seg_count" == 0 ]]; then
    # 非数字开头, 可能是 commit hash / build id / 自定义 tag
    echo "  [i]          $name  $image  非 semver tag :$tag (确认是否 immutable; 如自建镜像走构建 id 视为 OK)"
  elif [[ "$seg_count" == 1 ]]; then
    echo "  [!!] HIGH    $name  $image  仅 major :$tag, 应固定到 minor 或 patch"
  elif [[ "$seg_count" == 2 ]]; then
    # 两段: postgres/mysql/mariadb/alpine/debian/ubuntu 已是 patch; nginx/redis/node 等三段 semver 则需升 patch
    echo "  [i]          $name  $image  两段 :$ver_prefix (postgres/mysql/alpine 视为 patch OK; redis/nginx/node 等需固定到三段)"
  else
    # 三段及以上 (含 -alpine 等后缀)
    echo "  [OK] $name  $image"
  fi
done
echo ""
echo "[i] 修复:对每条 [!!!] / [!!] / [!] 的镜像,跑 /dwy-docker-image 用 query_dockerhub.py 拿 N-1 minor 推荐版本"

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
DAEMON_JSON=$(sudo -n cat /etc/docker/daemon.json 2>/dev/null || cat /etc/docker/daemon.json 2>/dev/null || echo "")
if [[ -z "$DAEMON_JSON" ]]; then
  echo "[i] 无 daemon.json 或不可读"
else
  echo "$DAEMON_JSON"
fi

echo ""
echo "--- 容器 RestartPolicy (服务器重启后能否自动起来) ---"
for c in $(docker ps -aq 2>/dev/null); do
  name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
  policy=$(docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' "$c" 2>/dev/null)
  state=$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null)
  case "$policy" in
    always|unless-stopped)
      echo "  [OK] $name  state=$state  policy=$policy"
      ;;
    on-failure)
      echo "  [!] $name  state=$state  policy=on-failure (手动 stop / OOM 后不会重启)"
      ;;
    no|"")
      [[ "$state" == "running" ]] \
        && echo "  [!!!] CRITICAL: $name  state=running  policy=${policy:-no} (服务器重启后不会自动启动)" \
        || echo "  [i] $name  state=$state  policy=${policy:-no}"
      ;;
    *)
      echo "  [?] $name  policy=$policy (未知)"
      ;;
  esac
done

echo ""
echo "--- 日志驱动配置 (防容器日志写满磁盘) ---"
LOG_DRIVER=$(echo "$DAEMON_JSON" | grep -oE '"log-driver"[[:space:]]*:[[:space:]]*"[^"]+"' | head -1)
LOG_MAX_SIZE=$(echo "$DAEMON_JSON" | grep -oE '"max-size"[[:space:]]*:[[:space:]]*"[^"]+"' | head -1)
LOG_MAX_FILE=$(echo "$DAEMON_JSON" | grep -oE '"max-file"[[:space:]]*:[[:space:]]*"[^"]+"' | head -1)
echo "log-driver: ${LOG_DRIVER:-(默认 json-file)}"
echo "max-size:   ${LOG_MAX_SIZE:-(未配置, 单容器日志可无限增长)}"
echo "max-file:   ${LOG_MAX_FILE:-(未配置)}"
if [[ -z "$LOG_MAX_SIZE" ]]; then
  echo "[!!] HIGH: 未限制单容器日志大小,长跑容器可能写满磁盘"
  echo "      建议: daemon.json 加 \"log-opts\": {\"max-size\": \"100m\", \"max-file\": \"3\"}"
fi

echo ""
echo "--- docker compose 文件位置 (用于人工核查) ---"
sudo -n find /home /opt /srv /root -maxdepth 5 \( -name "docker-compose*.yml" -o -name "compose.yml" \) 2>/dev/null | head -10

echo ""
echo "--- 镜像源加速检查 (国内服务器拉境外镜像必装) ---"
# a. 时区判定 (粗判境内)
TZ_VAL=$(timedatectl show -p Timezone --value 2>/dev/null || readlink -f /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||')
echo "服务器时区: ${TZ_VAL:-unknown}"
LIKELY_CN=0
case "$TZ_VAL" in
  Asia/Shanghai|Asia/Chongqing|Asia/Urumqi|Asia/Harbin|Asia/Hong_Kong|PRC) LIKELY_CN=1 ;;
esac
[[ "$LIKELY_CN" == "1" ]] && echo "→ 时区在 PRC, 拉境外 registry 不加速会非常慢" \
                          || echo "→ 时区非 PRC, 加速可选"

# b. daemon.json registry-mirrors
echo ""
MIRRORS=$(echo "$DAEMON_JSON" | grep -oE '"registry-mirrors"[[:space:]]*:[[:space:]]*\[[^]]*\]' | head -1)
if [[ -n "$MIRRORS" ]]; then
  echo "daemon registry-mirrors:"
  echo "  $MIRRORS"
  # 简单识别推荐源
  echo "$MIRRORS" | grep -oE 'https?://[a-zA-Z0-9.-]+' | while read u; do
    case "$u" in
      *daocloud*|*aliyun*|*aliyuncs*|*ustc*|*tsinghua*|*163*|*tencent*|*huaweicloud*)
        echo "    [OK] $u (国内加速源)" ;;
      *)
        echo "    [i]  $u (非已知国内主流源, 确认是否仍可用)" ;;
    esac
  done
else
  if [[ "$LIKELY_CN" == "1" ]]; then
    echo "[!!] HIGH: daemon.json 未配 registry-mirrors, 国内服务器拉 docker.io 镜像会非常慢"
  else
    echo "[i] daemon.json 未配 registry-mirrors (境外服务器一般不需要)"
  fi
  echo "      修复: 跑 /dwy-mirror-source 自动写入阿里云/中科大/daocloud 镜像源"
fi

# c. 当前运行中容器使用的境外 registry (registry-mirrors 仅对 docker.io 生效)
echo ""
echo "--- 运行容器 image registry 来源 (registry-mirrors 仅救 docker.io, 其他要改前缀) ---"
docker ps --format "{{.Names}}|{{.Image}}" 2>/dev/null | while IFS='|' read -r name image; do
  # 拆 registry: 必须含 "/" 且首段含 "." (域名) 或 ":" (port) 才算独立 registry
  # 否则视为隐式 docker.io (单段名 redis 或 namespace/name 格式 bitnami/redis)
  if [[ "$image" != */* ]]; then
    registry="docker.io"
  else
    first_seg="${image%%/*}"
    if [[ "$first_seg" == *.* || "$first_seg" == *:* ]]; then
      registry="$first_seg"
    else
      registry="docker.io"
    fi
  fi

  case "$registry" in
    docker.io)
      tag="OK 走 daemon registry-mirrors 加速"
      [[ -z "$MIRRORS" && "$LIKELY_CN" == "1" ]] && tag="[!!] 未配 mirror 国内拉取慢"
      ;;
    gcr.io|ghcr.io|k8s.gcr.io|registry.k8s.io|quay.io|mcr.microsoft.com|nvcr.io|docker.elastic.co)
      if [[ "$LIKELY_CN" == "1" ]]; then
        tag="[!!] HIGH 境外 registry, registry-mirrors 不生效, 必须把 image 名改 *.m.daocloud.io 前缀"
      else
        tag="[i] 境外 registry"
      fi
      ;;
    *daocloud*|*aliyun*|*aliyuncs*|*ustc*)
      tag="[OK] 已用国内镜像前缀"
      ;;
    *)
      tag="[i] 自建/私有 registry"
      ;;
  esac
  printf "  %-32s registry=%-32s %s\n" "$name" "$registry" "$tag"
done

echo ""
echo "[i] 修复路径:"
echo "      1. docker.io 加速  → /dwy-mirror-source 自动配 daemon registry-mirrors"
echo "      2. gcr/ghcr/k8s    → 把 image 改 <registry>.m.daocloud.io 前缀, 见 dwy-mirror-source 镜像替换表"
echo "      3. 镜像版本不固定  → /dwy-docker-image 选 N-1 minor 重新固定"
REMOTE
