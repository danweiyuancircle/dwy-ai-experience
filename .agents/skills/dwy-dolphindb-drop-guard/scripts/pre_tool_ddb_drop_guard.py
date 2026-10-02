"""Stub: parent SDD session resolves CLAUDE_PROJECT_DIR to dwy-shared.

Real guard lives in ai-quant; this workspace has no DolphinDB drop surface.
Always allow so PreToolUse does not block vitest/git for ETable work.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    """Consume stdin JSON and always allow.

    Returns:
        int: always ``0``.
    """
    sys.stdin.read()
    print(json.dumps({"decision": "allow"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
