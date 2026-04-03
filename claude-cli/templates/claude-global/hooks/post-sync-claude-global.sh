#!/bin/bash
# Claude Code PostToolUse Hook
# 当 Edit/Write 修改了 claude-global 模板文件时，自动同步到 ~/.claude/

# 快速路径检查：不含模板目录标记则直接退出
TEMPLATE_MARKER="claude-cli/templates/claude-global/"
echo "$TOOL_INPUT" | grep -q "$TEMPLATE_MARKER" || exit 0

# 用 python3 提取 file_path 并执行同步
python3 -c "
import json, sys, os, shutil

tool_input = os.environ.get('TOOL_INPUT', '')
if not tool_input:
    sys.exit(0)

try:
    data = json.loads(tool_input)
except (json.JSONDecodeError, TypeError):
    sys.exit(0)

file_path = data.get('file_path', '')
marker = '$TEMPLATE_MARKER'

if marker not in file_path:
    sys.exit(0)

# 提取相对路径
rel_path = file_path.split(marker, 1)[1]
if not rel_path or '..' in rel_path:
    sys.exit(0)

target_dir = os.path.expanduser('~/.claude')
dest_path = os.path.join(target_dir, rel_path)

# settings.json: 两层深合并
if rel_path == 'settings.json':
    try:
        with open(file_path) as f:
            new_settings = json.load(f)
    except Exception:
        sys.exit(0)

    if os.path.exists(dest_path):
        try:
            with open(dest_path) as f:
                existing = json.load(f)
        except Exception:
            existing = {}
        # 两层深合并：顶层 merge + dict value 二级 merge
        merged = dict(existing)
        for key, value in new_settings.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    else:
        os.makedirs(target_dir, exist_ok=True)
        merged = new_settings

    with open(dest_path, 'w') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'[sync] Merged settings.json -> {dest_path}')
else:
    # 其他文件：直接复制
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(file_path, dest_path)  # copy2 保留权限和时间戳
    print(f'[sync] Copied {rel_path} -> {dest_path}')
"

exit 0
