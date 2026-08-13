#!/usr/bin/env python3
"""用户全局配置读写：~/.dwy/config.yaml

私人信息（API Key、音色 ID 等）只放在此文件，不进 skill、不进项目仓库。
多业务共用一个 YAML，各业务占独立顶层 key（如 doubao_tts）。
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

import yaml

# 用户主目录全局配置根（非项目 .dwy）
DWY_HOME = Path.home() / ".dwy"
CONFIG_PATH = DWY_HOME / "config.yaml"

# 豆包配音在全局 YAML 中的 section 名
SECTION_DOUBAO_TTS = "doubao_tts"

# 旧路径：迁移用
LEGACY_JSON = Path.home() / ".config" / "doubao-tts" / "config.json"


def ensure_dwy_home() -> None:
    """确保 ~/.dwy 存在且仅本人可访问。"""
    DWY_HOME.mkdir(parents=True, exist_ok=True)
    os.chmod(DWY_HOME, stat.S_IRWXU)


def load_root() -> dict[str, Any]:
    """加载整份全局 YAML；不存在返回带 version 的空结构。"""
    if not CONFIG_PATH.is_file():
        return {"version": 1}
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if data is None:
        return {"version": 1}
    if not isinstance(data, dict):
        raise ValueError(f"全局配置格式错误（需 mapping）: {CONFIG_PATH}")
    data.setdefault("version", 1)
    return data


def save_root(root: dict[str, Any]) -> Path:
    """原子写入 ~/.dwy/config.yaml，chmod 600。"""
    ensure_dwy_home()
    root = dict(root)
    root.setdefault("version", 1)
    text = yaml.safe_dump(
        root,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    tmp = CONFIG_PATH.with_suffix(".yaml.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(CONFIG_PATH)
    os.chmod(CONFIG_PATH, stat.S_IRUSR | stat.S_IWUSR)
    return CONFIG_PATH


def get_section(name: str) -> dict[str, Any]:
    """读取某一业务 section；缺失返回 {}。"""
    root = load_root()
    sec = root.get(name)
    if sec is None:
        return {}
    if not isinstance(sec, dict):
        raise ValueError(f"section {name!r} 必须是 mapping: {CONFIG_PATH}")
    return sec


def set_section(name: str, section: dict[str, Any]) -> Path:
    """覆盖写入某一业务 section，保留其它业务配置。"""
    root = load_root()
    root[name] = section
    return save_root(root)


def try_load_legacy_doubao_json() -> dict[str, Any]:
    """读取旧版 ~/.config/doubao-tts/config.json（若存在）。"""
    if not LEGACY_JSON.is_file():
        return {}
    import json

    return json.loads(LEGACY_JSON.read_text(encoding="utf-8"))
