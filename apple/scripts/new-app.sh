#!/usr/bin/env bash
# 从骨架 Templates 生成 iOS / macOS 空业务工程。
# 部署底线写死在模板：iOS 17.0+、macOS 14.0+。
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  apple/scripts/new-app.sh --platform ios|macos --name AppName --bundle-id com.example.app --output /path/to/dir

Options:
  --platform     ios | macos（必填）
  --name         产品 / 模块名，须合法 Swift 标识（如 MyApp）（必填）
  --bundle-id    Bundle Identifier（必填）
  --output       输出目录（将创建 <output>/<name>）（必填）
  --team-id      DEVELOPMENT_TEAM，默认空字符串（可后补）
  --skeleton     统一仓库绝对路径，默认本脚本所在仓库根

Example:
  apple/scripts/new-app.sh --platform macos --name DemoMac --bundle-id com.dwy.demomac --output ~/WebstormProjects
EOF
}

PLATFORM=""
APP_NAME=""
BUNDLE_ID=""
OUTPUT_PARENT=""
TEAM_ID=""
SKELETON_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="${2:-}"; shift 2 ;;
    --name) APP_NAME="${2:-}"; shift 2 ;;
    --bundle-id) BUNDLE_ID="${2:-}"; shift 2 ;;
    --output) OUTPUT_PARENT="${2:-}"; shift 2 ;;
    --team-id) TEAM_ID="${2:-}"; shift 2 ;;
    --skeleton) SKELETON_ROOT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$PLATFORM" || -z "$APP_NAME" || -z "$BUNDLE_ID" || -z "$OUTPUT_PARENT" ]]; then
  echo "error: missing required args" >&2
  usage
  exit 1
fi

case "$PLATFORM" in
  ios|macos) ;;
  *) echo "error: --platform must be ios or macos" >&2; exit 1 ;;
esac

if [[ ! "$APP_NAME" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "error: --name must be a valid Swift type identifier" >&2
  exit 1
fi

SKELETON_ROOT="$(cd "$SKELETON_ROOT" && pwd)"
# 模板资源位于统一仓库 apple 子目录；--skeleton 始终表示仓库根。
TEMPLATE_DIR="$SKELETON_ROOT/apple/Templates/${PLATFORM}-app"
if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "error: template not found: $TEMPLATE_DIR" >&2
  exit 1
fi

DEST="$OUTPUT_PARENT/$APP_NAME"
if [[ -e "$DEST" ]]; then
  echo "error: destination already exists: $DEST" >&2
  exit 1
fi

mkdir -p "$OUTPUT_PARENT"
cp -R "$TEMPLATE_DIR" "$DEST"

# 目录 / 文件名：AppName* → 真实名（先深后浅）
while IFS= read -r path; do
  base="$(basename "$path")"
  parent="$(dirname "$path")"
  new_base="${base//AppName/$APP_NAME}"
  if [[ "$base" != "$new_base" ]]; then
    mv "$path" "$parent/$new_base"
  fi
done < <(find "$DEST" \( -name '*AppName*' \) | awk '{ print length, $0 }' | sort -rn | cut -d' ' -f2-)

export DEST_ROOT="$DEST"
export REPLACE_APP_NAME="$APP_NAME"
export REPLACE_BUNDLE_ID="$BUNDLE_ID"
export REPLACE_TEAM_ID="$TEAM_ID"
# SwiftPM 远端 package 身份取仓库名；固定版本下限由未来 0.4.0 tag 提供。
export REPLACE_PACKAGE_URL="https://github.com/danweiyuancircle/dwy-ai-experience.git"
export REPLACE_PACKAGE_VERSION="0.4.0"
export REPLACE_PACKAGE_ID="dwy-ai-experience"

python3 - <<'PY'
import os
from pathlib import Path

root = Path(os.environ["DEST_ROOT"])
repls = [
    # 唯一占位符，避免 BUNDLE_ID 误伤 PRODUCT_BUNDLE_IDENTIFIER
    ("__APP_NAME__", os.environ["REPLACE_APP_NAME"]),
    ("__BUNDLE_ID__", os.environ["REPLACE_BUNDLE_ID"]),
    ("__TEAM_ID__", os.environ["REPLACE_TEAM_ID"]),
    ("__PACKAGE_URL__", os.environ["REPLACE_PACKAGE_URL"]),
    ("__PACKAGE_VERSION__", os.environ["REPLACE_PACKAGE_VERSION"]),
    ("__PACKAGE_ID__", os.environ["REPLACE_PACKAGE_ID"]),
]
skip_suffix = {".png", ".jpg", ".jpeg", ".icns", ".pdf", ".zip"}
for path in root.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() in skip_suffix:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    orig = text
    for a, b in repls:
        text = text.replace(a, b)
    if text != orig:
        path.write_text(text, encoding="utf-8")
PY

echo "✓ created $DEST"
echo "  platform : $PLATFORM"
echo "  name     : $APP_NAME"
echo "  bundle   : $BUNDLE_ID"
echo "  skeleton : $SKELETON_ROOT"
echo "  deploy   : iOS 17.0+ / macOS 14.0+ (template)"
echo
echo "Next:"
echo "  cd \"$DEST\""
echo "  xcodegen generate"
if [[ "$PLATFORM" == "macos" ]]; then
  echo "  open ${APP_NAME}.xcodeproj"
  echo "  # or: swift test  (BizCore pure logic)"
else
  echo "  open ${APP_NAME}.xcodeproj"
  echo "  # or: swift test  (BizCore pure logic; host macOS)"
fi
