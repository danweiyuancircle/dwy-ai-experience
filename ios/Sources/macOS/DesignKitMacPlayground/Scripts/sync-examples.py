#!/usr/bin/env python3
"""Copy compiled fixtures and generate the reading index; --check rejects stale copies."""
from pathlib import Path
import argparse
import re
import sys

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
catalog = (root / "EPlaygroundCatalog.swift").read_text()
identities = dict(re.findall(r'case (\w+) = "([a-z-]+)"', catalog))
fixtures = re.findall(r'case \.(\w+): "(\w+Example)"', catalog)
version = re.search(r'let version = "([^"]+)"', catalog).group(1)
failures = []
index = [f"# DesignKitMac Playground · {version}\n",
         "Platform: macOS 26.0+ · Module: DesignKitMac · Product: DesignKitMacPlayground\n",
         "Generated from compiled fixtures and bundled Markdown. Runtime GUI, IME, VoiceOver and dynamic material acceptance are separate.\n"]


def output(path: Path, value: str):
    if args.check:
        if not path.exists() or path.read_text() != value:
            failures.append(str(path.relative_to(root)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


for case, fixture in fixtures:
    identity = identities[case]
    source = (root / "Fixtures" / f"{fixture}.swift").read_text()
    output(root / "Resources" / "Examples" / f"{fixture}.swift.txt", source)
    index.append(f"## designkit.mac.{identity}\n\nSource: `ios/Sources/macOS/DesignKitMacPlayground/Fixtures/{fixture}.swift`\n")
    for language in ("en", "zh-Hans"):
        documentation = root / "Resources" / "Documentation" / language / f"{identity}.md"
        if not documentation.exists():
            failures.append(str(documentation.relative_to(root)))
            continue
        index.append(documentation.read_text())
    index.append("```swift\n" + source + "```\n")
output(root / "Resources" / "Index.md", "\n".join(index))
if failures:
    print("Stale or missing Playground resources:\n" + "\n".join(failures))
    sys.exit(1)
print(f"Validated {len(fixtures)} compiled fixture copies and bilingual documentation.")
