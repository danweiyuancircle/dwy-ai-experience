#!/usr/bin/env python3
"""Validate the immutable visual tokens of the knowledge-town style preset."""

import json
from pathlib import Path


PRESET_PATH = Path(__file__).resolve().parents[1] / "assets" / "knowledge-town-paper-film-v1.json"


def main() -> None:
    preset = json.loads(PRESET_PATH.read_text(encoding="utf-8"))
    assert preset["visualTokens"]["ink"] == "#14213d"
    assert preset["visualTokens"]["accent"] == ["#ffd161", "#77dfd1", "#ff9cb9"]
    assert preset["stickerSystem"]["caption"]["required"] is True
    assert preset["assetAcceptance"]["alphaPreviewBackgrounds"] == ["#14213d", "#f4e8c6"]
    assert preset["themeFreedom"]["allowThemeSpecificSceneAndCamera"] is True
    print(f"Validated {preset['styleId']} visual system.")


if __name__ == "__main__":
    main()
