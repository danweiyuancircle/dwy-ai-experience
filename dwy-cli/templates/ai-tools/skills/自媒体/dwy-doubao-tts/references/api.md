# 豆包单向流式 TTS（HTTP Chunked）摘要

权威字段以火山引擎控制台文档为准。实现以 `scripts/synthesize.py` 为准。下面的地址、`seed-icl-2.0`、结束码和取值范围是当前先验。调用失败或模型下线就换控制台当前文档，不要把新地址写回本文件。

## 配置

私人信息只读：`~/.dwy/config.yaml` → 顶层 key `doubao_tts`  
示例骨架：`config.example.yaml`（无真实密钥）

## Endpoint

`POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`

## Headers

| Header | 必选 | 说明 |
|--------|------|------|
| `X-Api-Key` | 是 | `doubao_tts.api_key` |
| `X-Api-Resource-Id` | 是 | 默认 `seed-icl-2.0` |
| `X-Api-Request-Id` | 是 | 客户端 uuid |

## Body

```json
{
  "req_params": {
    "text": "口播正文",
    "speaker": "<音色ID>",
    "audio_params": {
      "format": "mp3",
      "sample_rate": 24000,
      "speech_rate": 0,
      "loudness_rate": 0
    }
  }
}
```

## 响应（Chunked）

- `code == 0`：`data` 为 base64 音频片  
- `code == 20000000`：结束  
- Header `X-Tt-Logid` 排障用  
