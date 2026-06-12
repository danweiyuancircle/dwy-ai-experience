"""Extracts a single version section from a markdown changelog for GitHub Releases."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def extract_version_body(changelog_text: str, version: str) -> str:
    """Returns the markdown body for one version section, excluding the version header."""
    matches = list(VERSION_HEADER_RE.finditer(changelog_text))
    for index, match in enumerate(matches):
      if match.group(1).strip() != version:
        continue

      body_start = match.end()
      body_end = matches[index + 1].start() if index + 1 < len(matches) else len(changelog_text)
      body = changelog_text[body_start:body_end].strip()
      if not body:
        raise ValueError(f"version section is empty: {version}")
      return body

    raise ValueError(f"version section not found: {version}")


def build_release_body(changelog_path: Path, version: str, release_name: str) -> str:
    """Builds the final GitHub Release body for the requested package version."""
    changelog_text = changelog_path.read_text(encoding="utf-8")
    version_body = extract_version_body(changelog_text, version)
    return f"## {release_name}\n\n{version_body}\n"


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("changelog_path")
    parser.add_argument("version")
    parser.add_argument("release_name")
    return parser.parse_args()


def main() -> int:
    """Entrypoint for command-line usage."""
    args = parse_args()
    try:
        body = build_release_body(Path(args.changelog_path), args.version, args.release_name)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
