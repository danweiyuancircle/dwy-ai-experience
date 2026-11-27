#!/usr/bin/env python3
"""Mirror compiled Fixtures into Resources/Examples without the outermost #if os(iOS) guard; --check rejects stale copies."""
from pathlib import Path
import argparse
import sys

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()


def strip_guard(source: str) -> str:
    # 与 IOSPlaygroundCatalog.strippingPlatformGuard 完全一致：测试逐字比较两者。
    lines = source.split("\n")
    trailing = lines[-1] == ""
    if trailing:
        lines.pop()
    if not lines or lines[0] != "#if os(iOS)" or lines[-1] != "#endif":
        return source
    return "\n".join(lines[1:-1]) + ("\n" if trailing else "")


fixtures = sorted((root / "Fixtures").glob("*Example.swift"))
targets = {root / "Resources" / "Examples" / f"{f.name}.txt": strip_guard(f.read_text()) for f in fixtures}
failures = []
if args.check:
    for path, value in targets.items():
        if not path.exists() or path.read_text() != value:
            failures.append(str(path.relative_to(root)))
    existing = (root / "Resources" / "Examples")
    for path in existing.glob("*.txt") if existing.exists() else []:
        if path not in targets:
            failures.append(f"{path.relative_to(root)}: no matching fixture")
else:
    (root / "Resources" / "Examples").mkdir(parents=True, exist_ok=True)
    for path, value in targets.items():
        path.write_text(value)
if failures:
    print("Stale or orphaned Playground examples:\n" + "\n".join(failures))
    sys.exit(1)
print(f"Validated {len(fixtures)} iOS fixture copies." if args.check else f"Wrote {len(fixtures)} iOS fixture copies.")
