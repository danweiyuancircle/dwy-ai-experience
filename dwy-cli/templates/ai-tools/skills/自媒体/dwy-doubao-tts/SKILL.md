---
name: dwy-doubao-tts
description: >
  豆包配音：用火山引擎豆包声音复刻 2.0（seed-icl-2.0）HTTP Chunked 单向流式接口，
  为自媒体口播生成 MP3 音频。API Key / 音色 ID 只读用户全局 ~/.dwy/config.yaml，
  禁止写入 skill 或任何项目目录。触发：豆包配音、口播配音、TTS、语音合成、
  生成口播音频、/doubao-tts、/dwy-doubao-tts。
---

# 豆包配音（dwy-doubao-tts）

自媒体口播：读全局密钥与音色 → 收口播文案 → 按语境选音色 → 流式合成 MP3 → 回报路径。

`SKILL_DIR` = 本 `SKILL.md` 所在目录（`dwy` 同步后随平台落在 `.claude/skills/dwy-doubao-tts` 或 `.agents/skills/dwy-doubao-tts`）。脚本一律用 `$SKILL_DIR/scripts/`，禁止写 `~/.grok/skills`。

## 硬约束

1. **私人配置唯一位置**：`~/.dwy/config.yaml`（权限 `600`），豆包段为顶层 key `doubao_tts`
2. **禁止**把 `api_key`、音色 ID 写入 skill、项目、commit；禁止回显完整 Key
3. 输出音频默认 `doubao_tts.output_dir`（默认 `~/Movies/doubao-tts`），不落到仓库内
4. 模型资源：`X-Api-Resource-Id: seed-icl-2.0`
5. 接口：`POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`

## 全局配置约定（`~/.dwy/config.yaml`）

用户级统一配置文件，多业务共用，各业务独立 section：

```yaml
version: 1

doubao_tts:
  api_key: "<仅本机>"
  resource_id: seed-icl-2.0
  endpoint: https://openspeech.bytedance.com/api/v3/tts/unidirectional
  default_voice: young_female
  voices:
    finance:
      id: "<音色ID>"
      label: 金融财经
    young_female:
      id: "<音色ID>"
      label: 年轻女性
  audio:
    format: mp3
    sample_rate: 24000
  output_dir: ~/Movies/doubao-tts

# 其它业务可继续追加顶层 key，互不覆盖
# other_service:
#   ...
```

结构说明见 `references/config.example.yaml`（示例无真实密钥）。

## 启动流程（每次触发必做）

### 1. 检查全局配置

```bash
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, str(Path(r'$SKILL_DIR') / 'scripts'))
from global_config import CONFIG_PATH, SECTION_DOUBAO_TTS, get_section
c = get_section(SECTION_DOUBAO_TTS)
assert c.get('api_key') and c.get('voices'), 'missing'
print('ok', CONFIG_PATH)
"
```

- 失败 → 「首次配置 / 迁移」，**不要**继续合成
- 成功 → 步骤 2

### 2. 收集用户输入

消息里若无完整口播正文，必须提问补齐，禁止瞎编：

| 字段 | 必选 | 说明 |
|------|------|------|
| `text` | 是 | 口播全文 |
| `voice` | 否 | `finance` / `young_female` / 配置其它 key；不传则自动选 |
| `output` | 否 | 输出绝对路径 |
| `speech_rate` / `loudness_rate` | 否 | `[-50,100]` |
| `context_texts` | 否 | 语音指令 |

### 3. 自动选音色

音色 ID **只从** `~/.dwy/config.yaml` 的 `doubao_tts.voices` 读，skill 内不硬编码真实 ID。

| 角色 key | 适用语境 |
|----------|----------|
| `finance` | 财经、股市、基金、理财、利率、宏观、投研 |
| `young_female` | 生活、种草、日常、泛娱乐、默认兜底 |

1. 用户指定 `voice` → 用该 key
2. 否则文案命中财经关键词 → `finance`
3. 否则 → `default_voice`
4. 两可 → 先问用户

### 4. 执行合成

```bash
python3 "$SKILL_DIR/scripts/synthesize.py" \
  --text-file /tmp/doubao_tts_input.txt \
  --voice <finance|young_female|...> \
  [--output /absolute/path/out.mp3]
```

- 长文优先 `--text-file`；单次建议 ≤ 1000 汉字
- 成功 stdout JSON：`{"ok":true,"path":"...","voice":"...","bytes":N}`

### 5. 回报用户

绝对路径、音色 key/label、文件大小；可 `open "<path>"` 试听。**禁止**回显 API Key。

## 首次配置 / 迁移

```bash
# 从旧路径 ~/.config/doubao-tts/config.json 迁到 ~/.dwy/config.yaml
python3 "$SKILL_DIR/scripts/setup_config.py" --migrate-legacy

# 或写入 / 更新 Key（可同时补音色）
python3 "$SKILL_DIR/scripts/setup_config.py" \
  --api-key '<USER_KEY>' \
  --voice 'finance=<ID>,金融财经' \
  --voice 'young_female=<ID>,年轻女性'
```

- 写入：`~/.dwy/config.yaml` → `doubao_tts`
- 成功后删除旧 JSON，避免双份密钥
- **永不**写入当前 git 仓库或 skill 目录

仅换 Key：

```bash
python3 "$SKILL_DIR/scripts/setup_config.py" --api-key '<NEW>' --update-key-only
```

## 协议要点

见 `references/api.md`。Header：`X-Api-Key` / `X-Api-Resource-Id` / `X-Api-Request-Id`；流式 `code==0` 拼 base64，结束码 `20000000`。

## 安全

- 私人信息只在 `~/.dwy/config.yaml`
- 不在项目建 `.env` / 本地 config
- 用户要求拷进项目 → 拒绝
