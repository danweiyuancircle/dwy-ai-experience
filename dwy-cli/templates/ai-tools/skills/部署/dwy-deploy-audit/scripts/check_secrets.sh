#!/usr/bin/env bash
# 凭证强度审计 (只读, 全脱敏)
#
# 检查范围 (7 类):
#   1. .env 文件: PASSWORD/SECRET/TOKEN/KEY/AK/SK 字段
#   2. docker 容器内联 env (Config.Env)
#   3. Redis 容器 --requirepass 启动参数
#   4. Postgres 容器 POSTGRES_PASSWORD
#   5. frps/frpc auth.token (toml/ini)
#   6. DolphinDB 配置文件 password
#   7. SSH 私钥 类型 + 位数 (~/.ssh/id_*)
#
# 强制脱敏: 只输出派生指标 (len/classes/strength), 永不输出明文
# 字典词: 内置 ~30 个最常见弱口令

TARGET="$1"; shift
SSH_OPTS=("$@")

ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE'
# ---------- 强度评估函数 ----------
# 输入: 一个秘密字符串(从 stdin)
# 输出: "len=N classes=K strength=STRONG/MEDIUM/WEAK reason=xxx"
# 不打印明文, 不写文件
strength_of() {
  local val
  IFS= read -r val
  local len=${#val}

  # 字典词内置(精简, 30 个最常见弱口令; 大小写不敏感子串匹配)
  local weak_dict='password|passwd|123456|123123|qwerty|abc123|admin|administrator|root|test|demo|guest|user|welcome|letmein|changeme|secret|default|temp|public|private|master|sample|example|prod|dev|staging|backup|hello|monkey'
  local is_dict=0
  echo "$val" | grep -qiE "($weak_dict)" && is_dict=1

  # 字符类
  local has_upper=0 has_lower=0 has_digit=0 has_symbol=0
  [[ "$val" =~ [A-Z] ]] && has_upper=1
  [[ "$val" =~ [a-z] ]] && has_lower=1
  [[ "$val" =~ [0-9] ]] && has_digit=1
  [[ "$val" =~ [^a-zA-Z0-9] ]] && has_symbol=1
  local classes=$(( has_upper + has_lower + has_digit + has_symbol ))

  # 评级
  local strength reason
  if   [[ "$len" -lt 8 ]]; then          strength="WEAK";   reason="len<8"
  elif [[ "$is_dict" == "1" ]]; then     strength="WEAK";   reason="dict_match"
  elif [[ "$len" -lt 16 ]]; then         strength="MEDIUM"; reason="len<16"
  elif [[ "$classes" -lt 3 ]]; then      strength="MEDIUM"; reason="classes<3"
  else                                   strength="STRONG"; reason="ok"
  fi
  printf "len=%d classes=%d strength=%s reason=%s" "$len" "$classes" "$strength" "$reason"
}

# 排除明显是"数值/枚举配置参数"而非凭证的 key 名
# (子串匹配 TOKEN/KEY 会误命中 ACCESS_TOKEN_EXPIRE_MINUTES / KEY_TIMEOUT 这种)
is_config_not_secret() {
  local key="$1"
  echo "$key" | grep -qiE '(EXPIRE|EXPIRY|TTL|TIMEOUT|SECONDS|MINUTES|HOURS|DAYS|COUNT|LIMIT|RETRY|MAX|MIN|SIZE|LENGTH|INTERVAL|DELAY|ENABLED|DISABLED|MODE|TYPE|VERSION|PORT|HOST|URL|PATH|FILE|DIR)$|_(EXPIRE|TTL|TIMEOUT|SECONDS|MINUTES|HOURS|DAYS|COUNT|LIMIT|MAX|MIN|SIZE|MODE|TYPE)_'
}

# 包装: 给定 key+value, 加上"高敏字段长度门槛 32"判定
evaluate_secret() {
  local key="$1"
  local val="$2"
  [[ -z "$val" ]] && { echo "  (空值)"; return; }

  # 判定是否真凭证字段 (key 名含 PASSWORD/SECRET/ACCESS_KEY_SECRET 等明确含义的)
  # 这类即使值是纯数字短串(如 DolphinDB 默认 123456) 也必须评估为 WEAK 而非 SKIP
  local is_true_credential=0
  echo "$key" | grep -qiE '(PASSWORD|PASSWD|SECRET|PRIVATE[_-]?KEY|ACCESS[_-]?KEY[_-]?SECRET|_SK$|^SK_)' && is_true_credential=1

  # Bug fix 1: 跳过明显是配置参数的 key (含 EXPIRE/TTL/TIMEOUT/MAX/MIN 等)
  # 但真凭证字段不跳过
  if [[ "$is_true_credential" == "0" ]] && is_config_not_secret "$key"; then
    printf "  %-30s [i] SKIP: 看起来是配置参数(非凭证), key 名含 EXPIRE/TTL/TIMEOUT/MAX 等\n" "$key"
    return
  fi
  # Bug fix 1.b: 纯数字短值(像 30 / 86400 这种 TTL/expire) 跳过
  # 但真凭证字段不跳过 (DolphinDB 默认 123456 / Redis 默认 123 这种弱密码必须报)
  if [[ "$is_true_credential" == "0" ]] && [[ "$val" =~ ^[0-9]+$ ]] && [[ ${#val} -lt 10 ]]; then
    printf "  %-30s [i] SKIP: 纯数字短值(看起来是配置参数, len=%d)\n" "$key" "${#val}"
    return
  fi

  # 是否高敏字段
  local high_sens=0
  echo "$key" | grep -qiE 'SECRET|JWT|TOKEN|API[_-]?KEY|ACCESS[_-]?KEY[_-]?SECRET|PRIVATE[_-]?KEY|_AK$|_SK$|^AK_|^SK_' && high_sens=1

  local result
  result=$(printf '%s\n' "$val" | strength_of)
  local len=$(echo "$result" | grep -oE 'len=[0-9]+' | cut -d= -f2)
  local classes=$(echo "$result" | grep -oE 'classes=[0-9]+' | cut -d= -f2)
  local strength=$(echo "$result" | grep -oE 'strength=[A-Z]+' | cut -d= -f2)

  # Bug fix 2: 长度 >= 24 即视为 STRONG (即使 classes 少, 熵足够)
  # 例如 48 字符 base64 / 64 字符 hex 即使只 2 类, 熵 >= 192 bits 远超 128 bits 安全门槛
  if [[ "$strength" != "WEAK" && "$len" -ge 24 ]]; then
    strength="STRONG"
    result="${result/strength=MEDIUM/strength=STRONG}"
    result="${result/reason=classes<3/reason=long_enough}"
    result="${result/reason=len<16/reason=long_enough}"
  fi

  printf "  %-30s %s" "$key" "$result"
  # 严重级标记
  if   [[ "$strength" == "WEAK" ]]; then
    printf "  [!!!] CRITICAL: 弱凭证, 必须立即轮换\n"
  elif [[ "$high_sens" == "1" && "$len" -lt 32 ]]; then
    printf "  [!!] HIGH: 高敏字段建议 >= 32 字符随机串\n"
  elif [[ "$strength" == "MEDIUM" ]]; then
    printf "  [!] MEDIUM: 建议加长至 16+ 且 3 类字符\n"
  else
    printf "  [OK]\n"
  fi
}

# ---------- 1. .env 文件扫描 ----------
echo "########## 1. .env 文件凭证强度 ##########"
ENV_FILES=$(sudo -n find /home /opt /srv /root -maxdepth 6 -type f \
              \( -name ".env" -o -name ".env.*" -o -name "*.env" \) 2>/dev/null \
            | grep -vE '\.example|\.template|\.sample|\.bak|\.old|node_modules' \
            | sort -u | head -20)
[[ -z "$ENV_FILES" ]] && ENV_FILES=$(find /home /opt /srv /root -maxdepth 6 -type f \
              \( -name ".env" -o -name ".env.*" -o -name "*.env" \) 2>/dev/null \
            | grep -vE '\.example|\.template|\.sample|\.bak|\.old|node_modules' \
            | sort -u | head -20)

if [[ -z "$ENV_FILES" ]]; then
  echo "[i] 未找到 .env 文件"
else
  for f in $ENV_FILES; do
    echo ""
    echo "[$f]"
    # 只挑密码类字段, 解析 KEY=VALUE
    if ! sudo -n cat "$f" 2>/dev/null | head -1 >/dev/null && ! cat "$f" 2>/dev/null | head -1 >/dev/null; then
      echo "  [i] 不可读"
      continue
    fi
    (sudo -n cat "$f" 2>/dev/null || cat "$f" 2>/dev/null) \
      | grep -E '^[[:space:]]*[A-Z][A-Z0-9_]*[[:space:]]*=' \
      | grep -iE '(PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|ACCESS[_-]?KEY|PRIVATE[_-]?KEY|_AK|_SK|^AK_|^SK_)' \
      | while IFS='=' read -r key val; do
          key=$(echo "$key" | tr -d ' \t')
          # 去引号 + 行尾注释
          val=$(echo "$val" | sed -E 's/^[[:space:]]*//; s/[[:space:]]*#.*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//')
          evaluate_secret "$key" "$val"
        done
  done
fi

# ---------- 2. docker 容器内联 env ----------
echo ""
echo "########## 2. Docker 容器内联 env 凭证强度 ##########"
if command -v docker >/dev/null 2>&1; then
  for c in $(docker ps -q 2>/dev/null); do
    name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
    echo ""
    echo "[$name]"
    docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$c" 2>/dev/null \
      | grep -iE '(PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|ACCESS[_-]?KEY|PRIVATE[_-]?KEY|_AK=|_SK=|^AK_|^SK_)' \
      | while IFS='=' read -r key val; do
          key=$(echo "$key" | tr -d ' \t')
          evaluate_secret "$key" "$val"
        done
  done
else
  echo "[i] Docker 未安装"
fi

# ---------- 3. Redis requirepass (从启动参数提取) ----------
echo ""
echo "########## 3. Redis --requirepass 强度 ##########"
if command -v docker >/dev/null 2>&1; then
  REDIS_FOUND=0
  for c in $(docker ps -q 2>/dev/null); do
    image=$(docker inspect -f '{{.Config.Image}}' "$c" 2>/dev/null)
    if echo "$image" | grep -qi "redis"; then
      REDIS_FOUND=1
      name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
      echo ""
      echo "[$name]"
      args=$(docker inspect -f '{{range .Args}}{{.}} {{end}}' "$c" 2>/dev/null)
      pass=$(echo "$args" | grep -oE -- '--requirepass [^ ]+' | head -1 | awk '{print $2}')
      if [[ -n "$pass" ]]; then
        evaluate_secret "REDIS_PASSWORD(--requirepass)" "$pass"
      else
        echo "  [!!!] CRITICAL: Redis 未设置 --requirepass"
      fi
    fi
  done
  [[ "$REDIS_FOUND" == "0" ]] && echo "[i] 未发现 Redis 容器"
fi

# ---------- 4. Postgres POSTGRES_PASSWORD (容器 env, 已在 2 覆盖, 此处单独 highlight) ----------
echo ""
echo "########## 4. Postgres POSTGRES_PASSWORD 强度 ##########"
if command -v docker >/dev/null 2>&1; then
  PG_FOUND=0
  for c in $(docker ps -q 2>/dev/null); do
    image=$(docker inspect -f '{{.Config.Image}}' "$c" 2>/dev/null)
    if echo "$image" | grep -qi "postgres"; then
      PG_FOUND=1
      name=$(docker inspect -f '{{.Name}}' "$c" 2>/dev/null | sed 's|^/||')
      echo ""
      echo "[$name]"
      pass=$(docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$c" 2>/dev/null \
              | grep '^POSTGRES_PASSWORD=' | head -1 | cut -d= -f2-)
      if [[ -n "$pass" ]]; then
        evaluate_secret "POSTGRES_PASSWORD" "$pass"
      else
        echo "  [!!!] CRITICAL: 未取得 POSTGRES_PASSWORD (是否 secrets 挂载或 trust 认证?)"
      fi
    fi
  done
  [[ "$PG_FOUND" == "0" ]] && echo "[i] 未发现 Postgres 容器"
fi

# ---------- 5. frp auth.token ----------
echo ""
echo "########## 5. frps/frpc auth.token 强度 ##########"
FRP_FILES=$(sudo -n find /etc /opt /home /root -maxdepth 6 -type f \
              \( -name "frps.toml" -o -name "frpc.toml" -o -name "frps.ini" -o -name "frpc.ini" \) 2>/dev/null \
            | grep -vE '\.bak|\.old|\.example' | sort -u | head -10)
[[ -z "$FRP_FILES" ]] && FRP_FILES=$(find /etc /opt /home /root -maxdepth 6 -type f \
              \( -name "frps.toml" -o -name "frpc.toml" -o -name "frps.ini" -o -name "frpc.ini" \) 2>/dev/null \
            | grep -vE '\.bak|\.old|\.example' | sort -u | head -10)

if [[ -z "$FRP_FILES" ]]; then
  echo "[i] 未发现 frp 配置文件"
else
  for f in $FRP_FILES; do
    echo ""
    echo "[$f]"
    # 提 token = "xxx" / token = xxx / auth.token = xxx
    # 注意: 必须用 { ...; } | grep 而非 cat || cat | grep
    # 后者因 | 优先级高于 ||, 当 sudo 成功时只跑 sudo cat, 后续 pipeline 被丢弃,
    # 导致 token 变量 = 整个文件内容, evaluate_secret 用 read 取第一行 (常是 bindPort=7000)
    token=$( { sudo -n cat "$f" 2>/dev/null || cat "$f" 2>/dev/null; } \
            | grep -iE '^[[:space:]]*(auth\.)?token[[:space:]]*=' \
            | head -1 | sed -E 's/.*=//; s/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//')
    if [[ -n "$token" ]]; then
      evaluate_secret "frp.token" "$token"
    else
      echo "  [!!] HIGH: 未配 token (frp 无认证, 任何人可注册到此 frps)"
    fi
  done
fi

# ---------- 6. DolphinDB 密码 ----------
echo ""
echo "########## 6. DolphinDB 配置密码强度 ##########"
DDB_FILES=$(sudo -n find /etc /opt /home /root -maxdepth 6 -type f \
              \( -name "dolphindb.cfg" -o -name "cluster.cfg" -o -name "controller.cfg" -o -name "agent.cfg" \) 2>/dev/null \
            | grep -vE '\.bak|\.old|\.example' | sort -u | head -10)
[[ -z "$DDB_FILES" ]] && DDB_FILES=$(find /etc /opt /home /root -maxdepth 6 -type f \
              \( -name "dolphindb.cfg" -o -name "cluster.cfg" -o -name "controller.cfg" -o -name "agent.cfg" \) 2>/dev/null \
            | grep -vE '\.bak|\.old|\.example' | sort -u | head -10)

if [[ -z "$DDB_FILES" ]]; then
  echo "[i] 未发现 DolphinDB 配置文件"
else
  for f in $DDB_FILES; do
    echo ""
    echo "[$f]"
    # DolphinDB 用户密码通常在 users.cfg 或通过 createUser 写入, 这里只看配置文件里的
    # adminPassword / password / encryptedPassword 等字段
    found=0
    while IFS='=' read -r key val; do
      key=$(echo "$key" | tr -d ' \t')
      val=$(echo "$val" | sed -E 's/^[[:space:]]*//; s/[[:space:]]*$//; s/^"//; s/"$//')
      [[ -n "$val" ]] && { evaluate_secret "$key" "$val"; found=1; }
    done < <(sudo -n grep -iE '(password|passwd|admin[Pp]ass)' "$f" 2>/dev/null \
              || grep -iE '(password|passwd|admin[Pp]ass)' "$f" 2>/dev/null)
    [[ "$found" == "0" ]] && echo "  [i] 配置文件中未直接含密码字段(可能用 users.cfg 或 createUser 写入)"
  done
fi

# ---------- 7. SSH 私钥强度 ----------
echo ""
echo "########## 7. SSH 私钥类型 / 位数 ##########"
# 当前用户 + root 的 ~/.ssh/ (Bug fix 3: 去重, root 用户登录时 $HOME=/root 会重复)
SSH_DIRS=$(printf '%s\n' "$HOME/.ssh" /root/.ssh /home/*/.ssh 2>/dev/null | sort -u)
for ssh_dir in $SSH_DIRS; do
  [[ -d "$ssh_dir" ]] || continue
  for kf in "$ssh_dir"/id_rsa "$ssh_dir"/id_ed25519 "$ssh_dir"/id_ecdsa "$ssh_dir"/id_dsa; do
    [[ -f "$kf" ]] || continue
    info=$(ssh-keygen -l -f "$kf" 2>/dev/null || sudo -n ssh-keygen -l -f "$kf" 2>/dev/null)
    if [[ -z "$info" ]]; then
      echo "  $kf  [i] 无法读取(权限?)"
      continue
    fi
    bits=$(echo "$info" | awk '{print $1}')
    type=$(echo "$info" | grep -oE '\([A-Z0-9]+\)$' | tr -d '()')
    perm=$(stat -c '%a' "$kf" 2>/dev/null)

    case "$type" in
      ED25519)
        printf "  %-40s type=%-8s bits=%-4s perm=%s  [OK]\n" "$kf" "$type" "$bits" "$perm" ;;
      RSA)
        if   [[ "$bits" -ge 4096 ]]; then mark="[OK]"
        elif [[ "$bits" -ge 3072 ]]; then mark="[OK] (建议升 ed25519)"
        elif [[ "$bits" -ge 2048 ]]; then mark="[!] MEDIUM: RSA-${bits} 可接受但建议升 ed25519 或 RSA-4096"
        else                              mark="[!!!] CRITICAL: RSA-${bits} 已不安全, 立即轮换"
        fi
        printf "  %-40s type=%-8s bits=%-4s perm=%s  %s\n" "$kf" "$type" "$bits" "$perm" "$mark" ;;
      ECDSA)
        printf "  %-40s type=%-8s bits=%-4s perm=%s  [!] MEDIUM: ECDSA 存疑(NIST 曲线), 建议 ed25519\n" "$kf" "$type" "$bits" "$perm" ;;
      DSA)
        printf "  %-40s type=%-8s bits=%-4s perm=%s  [!!!] CRITICAL: DSA 已废弃, 立即轮换\n" "$kf" "$type" "$bits" "$perm" ;;
      *)
        printf "  %-40s type=%-8s bits=%-4s perm=%s\n" "$kf" "$type" "$bits" "$perm" ;;
    esac

    # 权限检查
    if [[ -n "$perm" && "$perm" != "600" && "$perm" != "400" ]]; then
      echo "    [!!] HIGH: 私钥权限 $perm 过宽, 应 600"
    fi
  done
done

echo ""
echo "########## 凭证强度汇总 ##########"
echo "[i] 修复指引:"
echo "  - WEAK 密码: 立即轮换 (建议 >= 16 字符 + 三类字符的强密码)"
echo "  - 高敏字段 (JWT/SECRET/AK/SK): >= 32 字符随机串"
echo "  - 生成命令: openssl rand -base64 24 | tr -d '=+/' | cut -c1-20"
echo "  - 高敏: openssl rand -hex 32  (生成 64 字符 hex token)"
REMOTE
