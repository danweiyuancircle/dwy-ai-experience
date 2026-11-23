#!/usr/bin/env python3
"""Build the single source of truth for narration, captions, visuals, and SFX."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--beats", type=Path, required=True)
    parser.add_argument("--preset", type=Path, required=True)
    parser.add_argument("--voice", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    captions = load_json(args.captions)
    beat_document = load_json(args.beats)
    preset = load_json(args.preset)
    fps = beat_document.get("fps", preset.get("fps", 30))
    beats = beat_document.get("beats", [])
    caption_index = {(item["startMs"], item["endMs"]): item for item in captions}
    sfx_map = preset.get("audio", {}).get("sfxMap", {})
    cues = []

    for beat in beats:
        caption = caption_index.get((beat["startMs"], beat["endMs"]))
        if caption is None:
            raise ValueError(f"缺少与 {beat['cueId']} 对应的字幕时码")
        if caption["text"].strip() != beat["captionText"].strip():
            raise ValueError(f"{beat['cueId']} 字幕文本与视觉 beat 不一致")
        sfx = []
        for item in sfx_map.get(beat["visualAction"], []):
            start_frame = beat["startFrame"] + item["offsetFrames"]
            sfx.append({**item, "frame": start_frame})
        cues.append({
            "cueId": beat["cueId"],
            "sceneId": beat["sceneId"],
            "startMs": beat["startMs"],
            "endMs": beat["endMs"],
            "startFrame": beat["startFrame"],
            "endFrame": beat["endFrame"],
            "voText": caption["text"],
            "caption": {"text": caption["text"], "mode": beat.get("captionMode", "bottomSpeechBubble")},
            "visual": {
                "action": beat["visualAction"],
                "keyword": beat.get("onScreenKeyword", ""),
                "timing": beat.get("progressiveTiming", {}),
            },
            "sfx": sfx,
        })

    output = {
        "version": 1,
        "styleId": preset["styleId"],
        "fps": fps,
        "voice": {"file": args.voice, "timingStatus": "estimated_until_forced_alignment"},
        "canvas": preset["canvas"],
        "audio": {"bgm": preset.get("audio", {}), "duckDuringVoice": True},
        "cues": cues,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
