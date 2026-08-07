#!/usr/bin/env python3
"""Validate media package shots.json (schema version 1).

Usage:
  python validate_shots.py path/to/shots.json
  python validate_shots.py path/to/package/   # reads shots.json inside

Exit 0 = ok; 1 = validation errors; 2 = usage/io error.
Does not require jsonschema package: checks the critical contract rules inline.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

SHOT_ID_RE = re.compile(r"^[A-Z][0-9]{2}$")
PRESETS = {
    "hold",
    "fade_up",
    "scale_in",
    "draw_on",
    "highlight_pulse",
    "slide_in",
    "crossfade",
}


def load_package(path: Path) -> tuple[dict, Path]:
    if path.is_dir():
        path = path / "shots.json"
    if not path.is_file():
        raise FileNotFoundError(f"shots.json not found: {path}")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data, path


def validate(data: dict, fps_tol: float = 0.51) -> list[str]:
    errs: list[str] = []

    if data.get("version") != 1:
        errs.append(f"version must be 1, got {data.get('version')!r}")

    for key in ("fps", "width", "height", "chapters", "shots"):
        if key not in data:
            errs.append(f"missing top-level field: {key}")

    if errs:
        return errs

    fps = data["fps"]
    if not isinstance(fps, (int, float)) or fps <= 0:
        errs.append(f"fps must be > 0, got {fps!r}")

    chapters = data.get("chapters") or []
    shots = data.get("shots") or []
    if not isinstance(chapters, list) or len(chapters) < 1:
        errs.append("chapters must be a non-empty array")
    if not isinstance(shots, list) or len(shots) < 1:
        errs.append("shots must be a non-empty array")
        return errs

    shot_by_id: dict[str, dict] = {}
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            errs.append(f"shots[{i}] not an object")
            continue
        sid = s.get("shot_id")
        if not sid or not isinstance(sid, str) or not SHOT_ID_RE.match(sid):
            errs.append(f"shots[{i}].shot_id invalid: {sid!r} (expect A00-style)")
        else:
            if sid in shot_by_id:
                errs.append(f"duplicate shot_id: {sid}")
            shot_by_id[sid] = s

        for req in (
            "chapter_id",
            "order",
            "vo_text",
            "duration_sec",
            "duration_frames",
        ):
            if req not in s:
                errs.append(f"shot {sid or i}: missing {req}")

        vo = s.get("vo_text")
        if not isinstance(vo, str) or not vo.strip():
            errs.append(f"shot {sid or i}: vo_text empty")

        sec = s.get("duration_sec")
        frames = s.get("duration_frames")
        if isinstance(sec, (int, float)) and sec <= 0:
            errs.append(f"shot {sid}: duration_sec must be > 0")
        if isinstance(frames, int) and frames <= 0:
            errs.append(f"shot {sid}: duration_frames must be > 0")
        if (
            isinstance(sec, (int, float))
            and isinstance(frames, int)
            and isinstance(fps, (int, float))
            and fps > 0
            and sec > 0
        ):
            expected = round(sec * fps)
            if abs(expected - frames) > fps_tol:
                errs.append(
                    f"shot {sid}: duration_frames={frames} != round(sec*fps)={expected}"
                )

        motion = s.get("motion") or {}
        if isinstance(motion, dict):
            preset = motion.get("preset")
            if preset is not None and preset not in PRESETS:
                errs.append(f"shot {sid}: unknown motion.preset {preset!r}")

        builds = s.get("builds_on")
        if builds and isinstance(builds, str) and builds not in shot_by_id and builds:
            # may appear later in list; check after pass
            pass

        assets = s.get("assets")
        if assets is not None:
            if not isinstance(assets, list):
                errs.append(f"shot {sid}: assets must be array")
            else:
                for j, a in enumerate(assets):
                    if not isinstance(a, dict):
                        errs.append(f"shot {sid} assets[{j}] not object")
                        continue
                    if a.get("type_only"):
                        continue
                    if not a.get("role") or not a.get("path"):
                        errs.append(
                            f"shot {sid} assets[{j}]: need role+path (or type_only)"
                        )

    # builds_on integrity (after all ids known)
    for sid, s in shot_by_id.items():
        builds = s.get("builds_on")
        if builds in (None, "", "null"):
            continue
        if isinstance(builds, str) and builds not in shot_by_id:
            errs.append(f"shot {sid}: builds_on {builds!r} not in shots")

    # chapters vs shots
    chapter_ids = set()
    for ci, ch in enumerate(chapters):
        if not isinstance(ch, dict):
            errs.append(f"chapters[{ci}] not an object")
            continue
        cid = ch.get("chapter_id")
        if not cid:
            errs.append(f"chapters[{ci}]: missing chapter_id")
        else:
            chapter_ids.add(cid)
        ids = ch.get("shot_ids") or []
        if not ids:
            errs.append(f"chapter {cid}: shot_ids empty")
        for sid in ids:
            if sid not in shot_by_id:
                errs.append(f"chapter {cid}: shot_id {sid} missing from shots[]")

    for sid, s in shot_by_id.items():
        cid = s.get("chapter_id")
        if cid and chapter_ids and cid not in chapter_ids:
            errs.append(f"shot {sid}: chapter_id {cid!r} not in chapters")

    # optional totals
    if "total_duration_frames" in data and shot_by_id:
        sum_f = sum(
            s.get("duration_frames", 0)
            for s in shot_by_id.values()
            if isinstance(s.get("duration_frames"), int)
        )
        if data["total_duration_frames"] != sum_f:
            errs.append(
                f"total_duration_frames={data['total_duration_frames']} != sum shots {sum_f}"
            )

    return errs


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        data, path = load_package(Path(argv[1]))
    except Exception as e:
        print(f"IO error: {e}", file=sys.stderr)
        return 2

    errs = validate(data)
    if errs:
        print(f"FAIL {path} ({len(errs)} error(s))")
        for e in errs:
            print(f"  - {e}")
        return 1
    n = len(data.get("shots") or [])
    print(f"OK {path}  version=1  shots={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
