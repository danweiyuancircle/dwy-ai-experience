#!/usr/bin/env python3
"""初始化 / 更新豆包配音配置到用户全局 ~/.dwy/config.yaml（doubao_tts section）。

禁止写入 skill 目录与任何 git 项目。
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

# 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from global_config import (  # noqa: E402
    LEGACY_JSON,
    SECTION_DOUBAO_TTS,
    get_section,
    set_section,
    try_load_legacy_doubao_json,
)

# 结构默认值：不含真实 api_key / 音色 ID（私人信息只由用户写入全局 YAML）
DEFAULT_SECTION: dict = {
    "api_key": "",
    "resource_id": "seed-icl-2.0",
    "endpoint": "https://openspeech.bytedance.com/api/v3/tts/unidirectional",
    "voices": {},
    "default_voice": "young_female",
    "audio": {
        "format": "mp3",
        "sample_rate": 24000,
        "speech_rate": 0,
        "loudness_rate": 0,
        "disable_markdown_filter": True,
        "disable_emoji_filter": True,
    },
    "output_dir": str(Path.home() / "Movies" / "doubao-tts"),
}


def deep_merge(base: dict, overlay: dict) -> dict:
    """浅层 + 一层 dict 合并；overlay 优先。"""
    out = copy.deepcopy(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            merged = dict(out[k])
            merged.update(v)
            out[k] = merged
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_doubao_section() -> dict:
    """优先 ~/.dwy/config.yaml#doubao_tts，其次旧 JSON。"""
    sec = get_section(SECTION_DOUBAO_TTS)
    if sec:
        return sec
    return try_load_legacy_doubao_json()


def main() -> int:
    parser = argparse.ArgumentParser(description="写入豆包配音到 ~/.dwy/config.yaml")
    parser.add_argument("--api-key", help="火山引擎语音 API Key")
    parser.add_argument(
        "--update-key-only",
        action="store_true",
        help="仅更新 api_key",
    )
    parser.add_argument("--default-voice", help="覆盖 default_voice（如 finance / young_female）")
    parser.add_argument("--output-dir", help="覆盖口播输出目录")
    parser.add_argument(
        "--voice",
        action="append",
        metavar="KEY=ID[,label]",
        help="写入/更新音色，可重复。例: --voice finance=S_xxx,金融财经",
    )
    parser.add_argument(
        "--migrate-legacy",
        action="store_true",
        help="强制从 ~/.config/doubao-tts/config.json 迁移到 ~/.dwy/config.yaml",
    )
    args = parser.parse_args()

    existing = load_doubao_section()
    legacy = try_load_legacy_doubao_json()

    if args.migrate_legacy and legacy:
        existing = deep_merge(existing or {}, legacy)

    if args.update_key_only:
        if not args.api_key:
            print("error: --update-key-only 需要 --api-key", file=sys.stderr)
            return 2
        if not existing:
            print("error: 尚无 doubao_tts 配置可更新", file=sys.stderr)
            return 2
        sec = copy.deepcopy(existing)
        sec["api_key"] = args.api_key.strip()
    else:
        sec = deep_merge(DEFAULT_SECTION, existing or {})
        # 首次且无 voices：若有 legacy 整段带入
        if not sec.get("voices") and legacy.get("voices"):
            sec = deep_merge(sec, legacy)
        if args.api_key:
            sec["api_key"] = args.api_key.strip()
        elif not (sec.get("api_key") or "").strip():
            if legacy.get("api_key"):
                sec["api_key"] = legacy["api_key"]
            else:
                print("error: 需要 --api-key（或先有可迁移的旧配置）", file=sys.stderr)
                return 2

    if args.default_voice:
        sec["default_voice"] = args.default_voice
    if args.output_dir:
        sec["output_dir"] = str(Path(args.output_dir).expanduser())

    if args.voice:
        voices = dict(sec.get("voices") or {})
        for item in args.voice:
            if "=" not in item:
                print(f"error: 无效 --voice {item!r}，需 KEY=ID[,label]", file=sys.stderr)
                return 2
            key, rest = item.split("=", 1)
            key = key.strip()
            if "," in rest:
                vid, label = rest.split(",", 1)
                voices[key] = {"id": vid.strip(), "label": label.strip()}
            else:
                prev = voices.get(key) if isinstance(voices.get(key), dict) else {}
                voices[key] = {**prev, "id": rest.strip()}
        sec["voices"] = voices

    if not (sec.get("api_key") or "").strip():
        print("error: api_key 为空", file=sys.stderr)
        return 2

    path = set_section(SECTION_DOUBAO_TTS, sec)

    removed_legacy = False
    if LEGACY_JSON.is_file() and (args.migrate_legacy or legacy):
        try:
            LEGACY_JSON.unlink()
            removed_legacy = True
            parent = LEGACY_JSON.parent
            if parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
        except OSError:
            pass

    print(
        json.dumps(
            {
                "ok": True,
                "path": str(path),
                "section": SECTION_DOUBAO_TTS,
                "voices": list((sec.get("voices") or {}).keys()),
                "default_voice": sec.get("default_voice"),
                "resource_id": sec.get("resource_id"),
                "has_api_key": bool(sec.get("api_key")),
                "removed_legacy": removed_legacy,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
