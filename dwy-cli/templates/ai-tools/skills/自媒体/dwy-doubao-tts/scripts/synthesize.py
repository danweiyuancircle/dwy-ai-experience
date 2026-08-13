#!/usr/bin/env python3
"""豆包声音复刻 2.0：HTTP Chunked 单向流式 TTS，写出完整音频文件。

配置只从 ~/.dwy/config.yaml 的 doubao_tts section 读取。
禁止向 skill / 项目目录写密钥或音色 ID。
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))

from global_config import CONFIG_PATH, SECTION_DOUBAO_TTS, get_section  # noqa: E402

# 流式帧：业务成功片；文档约定结束码 20000000
CODE_AUDIO = 0
CODE_DONE = 20000000

# 财经语境关键词（小写匹配前会保留中文原文）
FINANCE_KEYWORDS = (
    "股市",
    "基金",
    "理财",
    "财经",
    "利率",
    "涨跌",
    "a股",
    "港股",
    "美股",
    "纳斯达克",
    "投资",
    "证券",
    "债券",
    "期货",
    "外汇",
    "央行",
    "gdp",
    "cpi",
    "通胀",
    "宏观",
    "财报",
    "估值",
    "牛市",
    "熊市",
    "板块",
    "市盈率",
    "分红",
    "持仓",
    "量化",
    "对冲",
    "ipo",
    "美联储",
    "加息",
    "降息",
)


def load_config() -> dict[str, Any]:
    """加载 ~/.dwy/config.yaml#doubao_tts；缺文件或缺 api_key 直接失败。"""
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"配置不存在: {CONFIG_PATH}。请先运行 setup_config.py --api-key <KEY>"
        )
    cfg = get_section(SECTION_DOUBAO_TTS)
    if not cfg:
        raise ValueError(
            f"缺少 section `{SECTION_DOUBAO_TTS}`: {CONFIG_PATH}。"
            "请先运行 setup_config.py --migrate-legacy 或 --api-key <KEY>"
        )
    if not (cfg.get("api_key") or "").strip():
        raise ValueError("doubao_tts.api_key 为空，请先 setup_config.py --api-key <KEY>")
    if not (cfg.get("voices") or {}):
        raise ValueError("doubao_tts.voices 为空，请用 setup_config.py --voice KEY=ID 写入")
    return cfg


def resolve_voice_key(cfg: dict[str, Any], voice: str | None, text: str) -> str:
    """用户指定优先；否则财经关键词 → finance；否则 default_voice。"""
    voices = cfg.get("voices") or {}
    if voice:
        if voice not in voices:
            raise KeyError(f"未知音色 key: {voice}；可选: {', '.join(voices)}")
        return voice

    lower = text.lower()
    if any(k in text or k in lower for k in FINANCE_KEYWORDS):
        if "finance" in voices:
            return "finance"

    default = cfg.get("default_voice") or "young_female"
    if default not in voices:
        # 兜底：取第一个
        if not voices:
            raise KeyError("config.voices 为空")
        return next(iter(voices))
    return default


def speaker_id(cfg: dict[str, Any], voice_key: str) -> str:
    """从全局 config 取 speaker 音色 ID。"""
    meta = (cfg.get("voices") or {})[voice_key]
    sid = meta.get("id") if isinstance(meta, dict) else meta
    if not sid:
        raise KeyError(f"音色 {voice_key} 缺少 id")
    return str(sid)


def default_output_path(cfg: dict[str, Any], fmt: str) -> Path:
    """按配置 output_dir 生成带时间戳的文件路径。"""
    out_dir = Path(cfg.get("output_dir") or (Path.home() / "Movies" / "doubao-tts")).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return out_dir / f"口播_{stamp}.{fmt}"


def build_body(
    text: str,
    speaker: str,
    audio: dict[str, Any],
    speech_rate: int | None,
    loudness_rate: int | None,
    context_texts: list[str] | None,
    model: str | None = None,
) -> dict[str, Any]:
    """组装 req_params；additions 需为 JSON 字符串（接口约定）。"""
    params: dict[str, Any] = {
        "text": text,
        "speaker": speaker,
        "audio_params": {
            "format": audio.get("format") or "mp3",
            "sample_rate": int(audio.get("sample_rate") or 24000),
            "speech_rate": int(speech_rate if speech_rate is not None else audio.get("speech_rate") or 0),
            "loudness_rate": int(
                loudness_rate if loudness_rate is not None else audio.get("loudness_rate") or 0
            ),
        },
    }
    # 仅配置显式给出 model 时下发（复刻场景按控制台要求填写）
    if model:
        params["model"] = model
    additions: dict[str, Any] = {}
    if audio.get("disable_markdown_filter") is not None:
        additions["disable_markdown_filter"] = bool(audio["disable_markdown_filter"])
    if audio.get("disable_emoji_filter") is not None:
        additions["disable_emoji_filter"] = bool(audio["disable_emoji_filter"])
    if additions:
        params["additions"] = json.dumps(additions, ensure_ascii=False)
    if context_texts:
        params["context_texts"] = context_texts
    return {"req_params": params}


def parse_stream_lines(raw: bytes) -> list[dict[str, Any]]:
    """把 chunked 响应体拆成 JSON 对象列表。

    兼容：每行一个 JSON；或粘连的 }{ 形态。
    """
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    objs: list[dict[str, Any]] = []
    # 先按行
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            objs.append(json.loads(line))
            continue
        except json.JSONDecodeError:
            pass
        # 粘连 JSON：用 }{ 切
        parts = re.split(r"\}\s*\{", line)
        if len(parts) == 1:
            raise ValueError(f"无法解析响应行: {line[:200]}")
        for i, part in enumerate(parts):
            if i == 0:
                s = part + "}"
            elif i == len(parts) - 1:
                s = "{" + part
            else:
                s = "{" + part + "}"
            objs.append(json.loads(s))
    return objs


def synthesize(
    cfg: dict[str, Any],
    text: str,
    voice_key: str,
    output: Path,
    speech_rate: int | None,
    loudness_rate: int | None,
    context_texts: list[str] | None,
    timeout: int,
) -> dict[str, Any]:
    """发单向流式请求，拼接 base64 音频并落盘。"""
    endpoint = cfg.get("endpoint") or "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
    resource_id = cfg.get("resource_id") or "seed-icl-2.0"
    speaker = speaker_id(cfg, voice_key)
    audio = cfg.get("audio") or {}
    model = cfg.get("model") or audio.get("model")
    body = build_body(text, speaker, audio, speech_rate, loudness_rate, context_texts, model)
    req_id = str(uuid.uuid4())

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": cfg["api_key"].strip(),
        "X-Api-Resource-Id": resource_id,
        "X-Api-Request-Id": req_id,
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(endpoint, data=data, headers=headers, method="POST")

    try:
        with urlopen(request, timeout=timeout) as resp:
            raw = resp.read()
            logid = resp.headers.get("X-Tt-Logid") or resp.headers.get("x-tt-logid") or ""
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code}: {err_body}") from e
    except URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e

    chunks: list[bytes] = []
    last_msg = ""
    done = False
    for obj in parse_stream_lines(raw):
        code = obj.get("code")
        msg = obj.get("message") or ""
        if msg:
            last_msg = msg
        if code == CODE_AUDIO:
            b64 = obj.get("data") or ""
            if b64:
                chunks.append(base64.b64decode(b64))
        elif code == CODE_DONE:
            done = True
            break
        elif code not in (None, CODE_AUDIO, CODE_DONE):
            # 非 0 且非结束：业务错误
            if code != 0:
                raise RuntimeError(f"合成失败 code={code} message={msg} logid={logid}")

    if not chunks:
        raise RuntimeError(f"未收到音频数据 message={last_msg} logid={logid} done={done}")

    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = b"".join(chunks)
    output.write_bytes(payload)

    voice_meta = (cfg.get("voices") or {}).get(voice_key) or {}
    return {
        "ok": True,
        "path": str(output),
        "voice": voice_key,
        "label": voice_meta.get("label") if isinstance(voice_meta, dict) else voice_key,
        "bytes": len(payload),
        "request_id": req_id,
        "logid": logid,
        "done": done,
    }


def read_text(args: argparse.Namespace) -> str:
    """从 --text / --text-file / stdin 取文案。"""
    if args.text_file:
        return Path(args.text_file).expanduser().read_text(encoding="utf-8").strip()
    if args.text is not None:
        return args.text.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("error: 请提供 --text 或 --text-file 或 stdin 管道")


def main() -> int:
    parser = argparse.ArgumentParser(description="豆包配音流式合成")
    parser.add_argument("--text", help="口播正文")
    parser.add_argument("--text-file", help="从文件读口播正文（推荐长文）")
    parser.add_argument("--voice", help="音色 key：finance / young_female / 配置自定义")
    parser.add_argument("--output", help="输出音频绝对路径")
    parser.add_argument("--speech-rate", type=int, help="语速 [-50,100]")
    parser.add_argument("--loudness-rate", type=int, help="音量 [-50,100]")
    parser.add_argument(
        "--context-text",
        action="append",
        dest="context_texts",
        help="语音指令，可重复传入",
    )
    parser.add_argument("--timeout", type=int, default=120, help="HTTP 超时秒数")
    args = parser.parse_args()

    try:
        text = read_text(args)
        if not text:
            print("error: 文案为空", file=sys.stderr)
            return 2
        # 口播合理上限；超长仍允许但告警（由调用方拆段更佳）
        if len(text) > 5000:
            print("warning: 文案超过 5000 字，建议分段合成", file=sys.stderr)

        cfg = load_config()
        voice_key = resolve_voice_key(cfg, args.voice, text)
        fmt = ((cfg.get("audio") or {}).get("format") or "mp3").lstrip(".")
        out = Path(args.output) if args.output else default_output_path(cfg, fmt)

        result = synthesize(
            cfg=cfg,
            text=text,
            voice_key=voice_key,
            output=out,
            speech_rate=args.speech_rate,
            loudness_rate=args.loudness_rate,
            context_texts=args.context_texts,
            timeout=args.timeout,
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as e:
        # 永不打印 config 全文 / api_key
        print(f"error: {e}", file=sys.stderr)
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
