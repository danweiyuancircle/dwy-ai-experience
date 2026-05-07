#!/usr/bin/env bash
# 扫描项目中所有 Docker 镜像引用，输出违规清单（latest / 浮动 tag / 缺 tag）。
#
# 用法：
#     bash scan_images.sh [project-path]
#
# 不传路径则扫描当前目录。脚本只读不写，仅输出报告，不修改任何文件。

set -euo pipefail

ROOT="${1:-.}"

if [ ! -d "$ROOT" ]; then
    echo "错误：路径不存在或不是目录：$ROOT" >&2
    exit 2
fi

# 浮动 tag 黑名单（不含版本号的纯字符串 tag）
FLOATING_TAGS_RE='^(latest|stable|mainline|current|release|lts|rolling|main|master|head|edge|nightly|alpine|slim|bookworm|bullseye|buster|jammy|focal|noble|trixie)$'

# 临时输出文件
TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

count_critical=0
count_high=0
count_low=0

# 工具函数：分级记录
record() {
    local level="$1"
    local file="$2"
    local line="$3"
    local content="$4"
    local hint="$5"
    printf "[%s] %s:%s\n  %s\n  → %s\n\n" "$level" "$file" "$line" "$content" "$hint" >> "$TMP_OUT"
    case "$level" in
        critical) count_critical=$((count_critical + 1)) ;;
        high) count_high=$((count_high + 1)) ;;
        low) count_low=$((count_low + 1)) ;;
    esac
}

# 解析 image 字符串，返回违规级别和提示
# 输入：image_ref（如 nginx:latest、postgres、redis:7）
# 输出：通过 record 函数记录
analyze_image() {
    local image_ref="$1"
    local file="$2"
    local line="$3"
    local raw_line="$4"

    # 去掉 digest 部分（@sha256:...）参与 tag 分析
    local without_digest="${image_ref%@sha256:*}"

    # 拆分 image 和 tag
    local image_part tag_part
    if [[ "$without_digest" == *:* ]]; then
        # 注意 registry 可能含端口（如 registry.example.com:5000/image:tag）
        # 用最后一个冒号分隔
        image_part="${without_digest%:*}"
        tag_part="${without_digest##*:}"
    else
        image_part="$without_digest"
        tag_part=""
    fi

    # 1. 缺 tag（等同于 latest）
    if [ -z "$tag_part" ]; then
        record "critical" "$file" "$line" "$raw_line" "镜像 $image_part 未指定 tag（等同于 latest），改为固定版本如 $image_part:<N-1-minor>"
        return
    fi

    # 2. 显式 latest
    if [ "$tag_part" = "latest" ]; then
        record "critical" "$file" "$line" "$raw_line" "禁止使用 latest，改为固定版本如 $image_part:<N-1-minor>（用 query_dockerhub.py 查推荐版本）"
        return
    fi

    # 3. 浮动 tag（不含数字）
    if [[ "$tag_part" =~ $FLOATING_TAGS_RE ]]; then
        record "high" "$file" "$line" "$raw_line" "tag '$tag_part' 是浮动 tag，会随上游更新漂移，改为带版本号的具体 tag"
        return
    fi

    # 4. 单段数字（如 redis:7、postgres:17）
    if [[ "$tag_part" =~ ^v?[0-9]+$ ]]; then
        record "high" "$file" "$line" "$raw_line" "单段版本号 '$tag_part' 实际是浮动 tag（指向该 major 最新），钉到 minor 或 patch"
        return
    fi

    # 5. 看起来固定但没有 digest（仅作为低优先级提醒）
    if [[ "$tag_part" =~ ^v?[0-9]+\.[0-9]+ ]] && [[ ! "$image_ref" =~ @sha256: ]]; then
        # 不是所有 image 都需要 digest，这里只对常见生产关键服务提醒
        if [[ "$image_part" =~ (postgres|mysql|mariadb|mongo|redis|kafka|rabbitmq|elasticsearch|nginx|envoyproxy)$ ]]; then
            record "low" "$file" "$line" "$raw_line" "生产关键服务建议追加 @sha256:... digest，让 image 完全不可篡改"
        fi
    fi
}

# 扫描 Dockerfile 风格文件
scan_dockerfiles() {
    while IFS= read -r -d '' f; do
        local lineno=0
        while IFS= read -r line; do
            lineno=$((lineno + 1))
            # 匹配 FROM 指令，去掉 AS 别名
            if [[ "$line" =~ ^[[:space:]]*FROM[[:space:]]+([^[:space:]]+) ]]; then
                local image_ref="${BASH_REMATCH[1]}"
                # 跳过参数化的 FROM（如 FROM ${BASE_IMAGE}）
                if [[ "$image_ref" =~ ^\$\{ ]] || [[ "$image_ref" =~ ^\$[A-Z_] ]]; then
                    continue
                fi
                # 跳过 scratch
                if [ "$image_ref" = "scratch" ]; then
                    continue
                fi
                analyze_image "$image_ref" "$f" "$lineno" "$(echo "$line" | sed 's/^[[:space:]]*//')"
            fi
        done < "$f"
    done < <(find "$ROOT" \
        \( -name "Dockerfile" -o -name "Dockerfile.*" -o -name "*.Dockerfile" \) \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -print0)
}

# 扫描 yaml 风格文件（compose / k8s / CI）
scan_yaml_files() {
    while IFS= read -r -d '' f; do
        local lineno=0
        while IFS= read -r line; do
            lineno=$((lineno + 1))
            # 匹配 image: xxx 或 image: "xxx"
            if [[ "$line" =~ ^[[:space:]]*image:[[:space:]]*[\"\']?([^[:space:]\"\'#]+) ]]; then
                local image_ref="${BASH_REMATCH[1]}"
                # 跳过模板变量
                if [[ "$image_ref" =~ ^\$\{ ]] || [[ "$image_ref" =~ ^\$[A-Z_] ]] || [[ "$image_ref" =~ \{\{ ]]; then
                    continue
                fi
                analyze_image "$image_ref" "$f" "$lineno" "$(echo "$line" | sed 's/^[[:space:]]*//')"
            fi
        done < "$f"
    done < <(find "$ROOT" \
        \( -name "docker-compose*.yml" -o -name "docker-compose*.yaml" \
           -o -name "compose.yml" -o -name "compose.yaml" \
           -o -name "*.yaml" -o -name "*.yml" \) \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/dist/*" \
        -not -path "*/build/*" \
        -print0)
}

echo "扫描目录: $ROOT" >&2
echo "" >&2

scan_dockerfiles
scan_yaml_files

# 输出结果
total=$((count_critical + count_high + count_low))

if [ "$total" -eq 0 ]; then
    echo "✅ 未发现违规：所有镜像都已固定到具体版本。"
    exit 0
fi

cat "$TMP_OUT"

echo "----------------------------------------"
echo "汇总: $total 项问题"
echo "  critical: $count_critical  (latest / 缺 tag)"
echo "  high:     $count_high      (浮动 tag / 单段版本号)"
echo "  low:      $count_low       (建议补 digest)"
echo ""
echo "下一步："
echo "  1. 用 query_dockerhub.py <image> 查每个违规镜像的推荐版本"
echo "  2. 用 Edit 工具逐项修复，不要批量替换（不同环境可能用不同 tag 变体）"

# 有 critical 或 high 时返回非零，方便 CI 集成
if [ "$count_critical" -gt 0 ] || [ "$count_high" -gt 0 ]; then
    exit 1
fi
exit 0
