#!/bin/bash
# Stub: parent SDD session points CLAUDE_PROJECT_DIR at dwy-shared.
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null || true)
printf '%s' "$CMD" | grep -q 'git commit' || exit 0
exit 0
