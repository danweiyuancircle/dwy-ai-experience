#!/usr/bin/env python3
"""Validate cue-timeline.json without third-party dependencies."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("version") != 1:
        errors.append("version must be 1")
    fps = document.get("fps")
    if not isinstance(fps, (int, float)) or fps <= 0:
        errors.append("fps must be positive")
        return errors
    canvas = document.get("canvas", {})
    if canvas.get("subtitleBandPx", 0) < 160:
        errors.append("canvas.subtitleBandPx must be at least 160")
    cues = document.get("cues")
    if not isinstance(cues, list) or not cues:
        return errors + ["cues must be a non-empty array"]
    last_end_ms = last_end_frame = -1
    ids: set[str] = set()
    for cue in cues:
        cue_id = cue.get("cueId")
        if not cue_id or cue_id in ids:
            errors.append(f"cueId must be unique: {cue_id!r}")
        ids.add(cue_id)
        start_ms, end_ms = cue.get("startMs"), cue.get("endMs")
        start_frame, end_frame = cue.get("startFrame"), cue.get("endFrame")
        if not isinstance(start_ms, int) or not isinstance(end_ms, int) or end_ms <= start_ms:
            errors.append(f"{cue_id}: invalid millisecond range")
        if not isinstance(start_frame, int) or not isinstance(end_frame, int) or end_frame <= start_frame:
            errors.append(f"{cue_id}: invalid frame range")
        if start_ms < last_end_ms or start_frame < last_end_frame:
            errors.append(f"{cue_id}: overlaps previous cue")
        if isinstance(start_ms, int) and isinstance(end_ms, int) and isinstance(start_frame, int) and isinstance(end_frame, int):
            expected = round((end_ms - start_ms) * fps / 1000)
            if abs((end_frame - start_frame) - expected) > 1:
                errors.append(f"{cue_id}: frame duration disagrees with milliseconds")
        if cue.get("voText") != cue.get("caption", {}).get("text"):
            errors.append(f"{cue_id}: voiceover and caption text differ")
        for effect in cue.get("sfx", []):
            if effect.get("frame", -1) < start_frame or effect.get("frame", 10**9) >= end_frame:
                errors.append(f"{cue_id}: SFX frame must fall inside the cue")
        last_end_ms, last_end_frame = end_ms, end_frame
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_cue_timeline.py cue-timeline.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    document = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(document)
    if errors:
        print(f"FAIL {path}")
        print("\n".join(f"  - {error}" for error in errors))
        return 1
    print(f"OK {path}  cues={len(document['cues'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
