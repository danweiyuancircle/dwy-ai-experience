---
name: dwy-eapi
description: "Use when building or changing FastAPI backends that use dwyeapi: Pydantic Settings, async SQLAlchemy, Redis, JWT/bcrypt, AppError/NotFoundError/BusinessError, ApiResponse/PageData, pagination, loguru, health checks, PII masking, timezone-aware dt, ARQ tasks, email verification codes, Gmail alias canonicalization. The single navigation skill for dwyeapi."
---

# dwyeapi

FastAPI 基础设施包。本文件只做**路由**：探测安装版本 → 选文档线 → 不够再读源码（先 clone tag，拿不到再读虚拟环境）。

对外只有这一个 skill。`v0/` `v1/` 不是独立 skill，禁止当多个入口用。

## 每次写 dwyeapi 代码前（强制）

1. **探测安装版本**（按顺序，命中即停）
   ```bash
   python -c "import dwyeapi; print(dwyeapi.__version__)"
   ```
   失败则读项目 `pyproject.toml` / `uv.lock` 里 `dwyeapi` 约束。
   仍失败：按 `v0` 给脚手架，并声明「未探测到安装版本」。

2. **选线**：读同目录 `versions.yml`。`0.y.z` → `v0/`，`1.y.z` → `v1/`，`2.y.z` → `v2/`。目录不存在（例如装了 1.x 但还没有 `v1/`）→ 不要用 `v0` 冒充；按下面「读源码」拿该版本代码，并说明文档线未建。

3. **读文档**：先 `shared/`（跨大版本不变），再该线 `vN/`。能力标了版本下限（如 `canonicalize_email` ≥0.9.6）时，安装版本低于下限 → 当不存在。

4. **文档不够 / 和记忆冲突 / 下限对不上** → 读代码，顺序如下（命中即停）：
   1. clone 安装版本对应 tag（见下）
   2. tag 不存在 / clone 失败 → 读**当前虚拟环境**里已安装的 `dwyeapi` 源码
   3. 虚拟环境也没有 → **停下来问人**，禁止猜 API，禁止拿旁边 dwy-shared master 冒充

## 读源码

### 1. clone tag（优先）

```bash
VER=0.9.6                          # 换成第 1 步探测到的版本
TAG="dwyeapi@${VER}"
DEST=".dwy/eapi-src/${VER}"        # 项目内缓存，已 gitignore

if [ ! -d "$DEST/backend/src/dwyeapi" ]; then
  git clone --depth 1 --branch "$TAG" \
    --filter=blob:none --sparse \
    https://github.com/danweiyuancircle/dwy-ai-experience.git \
    "$DEST"
  git -C "$DEST" sparse-checkout set backend/src/dwyeapi
fi
# 只读 $DEST/backend/src/dwyeapi/ 的模块 docstring
```

- `--branch` 必须是 `dwyeapi@x.y.z`，禁止 clone 默认 branch。
- 必须 sparse，只要 `backend/src/dwyeapi`。

### 2. 虚拟环境（clone 拿不到时）

```bash
python -c "import dwyeapi, os; print(os.path.dirname(dwyeapi.__file__))"
# 输出形如 .venv/lib/python3.11/site-packages/dwyeapi
# 读该目录下模块 docstring
```

editable 安装时这个路径就是消费方正在跑的代码，当作安装版本真相。

文档与源码冲突：信源码。clone 与 venv 都读到且不一致：以 **venv** 为准（editable / 热修），回复里写明。

## 文档地图

| 路径 | 何时读 |
|------|--------|
| `shared/layering.md` | 分层、禁 HTTPException |
| `shared/timezone.md` | 禁 `datetime.now` |
| `shared/response-envelope.md` | ApiResponse 信封 |
| `shared/anticorruption.md` | 禁止直调 redis/jwt/logging |
| `v0/index.md` | 0.x 模块清单、接入、陷阱 |
| `v0/providers-email.md` | 邮件 Provider 注册表 |
| `v0/email-canonical.md` | Gmail 规范化（≥0.9.6） |
| `v0/breaking.md` | 0.x 内部 breaking |
| `references/tasks-integration-guide.md` | 只用 tasks 时读 |

## 禁止

| 借口 | 实际 |
|------|------|
| 读旁边 dwy-shared master | 消费方版本可能不同。先 clone 安装版本的 tag，不行再读本项目 venv |
| 文档是 0.9，装的 0.9.6，差不多 | 有下限的能力必须对照版本 |
| tag 没有就猜 / 直接停 | clone 失败后读 venv；venv 也没有才停 |
| 再开一个 `dwy-eapi-v0` skill | 对外只有 `dwy-eapi` |
