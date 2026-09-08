---
name: dwy-eui
description: "Use when building Vue 3 UI with @dwydev/eui: pick components, forms, tables, overlays, admin layout, theme, i18n, EConfigProvider. The single navigation skill for @dwydev/eui."
---

# @dwydev/eui

Vue 3 组件库（Reka-ui + shadcn 视觉 + Element Plus 式 API + Tailwind 4）。本文件只做**路由**：探测安装版本 → 选文档线 → 不够再读源码（先 clone tag，拿不到再读 `node_modules`）。

对外只有这一个 skill。`v1/` `v2/` 不是独立 skill，禁止当多个入口用。

## 每次写 @dwydev/eui 代码前（强制）

1. **探测安装版本**（按顺序，命中即停）
   ```bash
   node -p "require('@dwydev/eui/package.json').version"
   ```
   失败则读 `pnpm-workspace.yaml` catalog `'@dwydev/eui'`，再读 `package.json` 的 `dependencies` / `peerDependencies`。
   仍失败：按 `v2` 给脚手架，并声明「未探测到安装版本」。

2. **选线**：读同目录 `versions.yml`。`2.y.z` → `v2/`，`1.y.z` → `v1/`。目录不存在（例如装了 3.x 但还没有 `v3/`）→ 不要用 `v2` 冒充；按下面「读源码」拿该版本代码，并说明文档线未建。

3. **读文档**：先 `shared/`（跨大版本不变），再该线 `vN/`。能力标了版本下限（如 `component-manifest.json` ≥2.1.0、`useEuiMobile` ≥2.4）时，安装版本低于下限 → 当不存在。

4. **文档不够 / 和记忆冲突 / 下限对不上** → 读代码，顺序如下（命中即停）：
   1. clone 安装版本对应 tag（见下）
   2. tag 不存在 / clone 失败 → 读**当前项目** `node_modules/@dwydev/eui`
   3. `node_modules` 也没有 → **停下来问人**，禁止猜 props，禁止拿旁边 dwy-shared master 冒充

## 读源码

### 1. clone tag（优先）

```bash
VER=2.4.0                          # 换成第 1 步探测到的版本
TAG="@dwydev/eui@${VER}"
DEST=".dwy/eui-src/${VER}"         # 项目内缓存，已 gitignore

if [ ! -d "$DEST/frontend/eui/src" ]; then
  git clone --depth 1 --branch "$TAG" \
    --filter=blob:none --sparse \
    https://github.com/danweiyuancircle/dwy-ai-experience.git \
    "$DEST"
  git -C "$DEST" sparse-checkout set frontend/eui/src frontend/eui/package.json
fi
# 只读 $DEST/frontend/eui/src/ 的组件 types.ts / .vue
```

- `--branch` 必须是 `@dwydev/eui@x.y.z`（含 `-beta.N`），禁止 clone 默认 branch。
- 必须 sparse，只要 `frontend/eui/src`。

### 2. node_modules（clone 拿不到时）

```bash
# 版本与清单
node -p "require('@dwydev/eui/package.json').version"
ls node_modules/@dwydev/eui/dist/component-manifest.json
# props/emits：dist/components/{kebab}/types.d.ts
# slots：.d.ts 常被擦成 any，clone 源码搜 <slot
```

`node_modules` 是消费方正在跑的代码，当作安装版本真相。

文档与源码冲突：信源码。clone 与 node_modules 都读到且不一致：以 **node_modules** 为准，回复里写明。

## 文档地图

| 路径 | 何时读 |
|------|--------|
| `shared/form.md` | 禁原生 form、ESelect 空 value、zod rules |
| `shared/overlay.md` | `v-model:open`、Dialog padding、Sheet zIndex |
| `shared/reka.md` | 封装 reka 必须 v-model |
| `shared/config-theme.md` | EConfigProvider、useTheme、cn() |
| `v2/index.md` | 2.x 组件导航、composables、陷阱 |
| `v2/lookup.md` | manifest / types.d.ts 怎么查 |
| `v2/breaking.md` | 2.x 内部 breaking（含 2.4.0 删组件） |
| `v1/index.md` | 1.x 导航；无 manifest 时怎么查 |
| `references/eui-integration-guide.md` | 新项目接入 |
| `references/eui-design-guide.md` | 中后台设计 |
| `references/eui-landing-design-guide.md` | 落地页设计 |

## 禁止

| 借口 | 实际 |
|------|------|
| 读旁边 dwy-shared master | 消费方版本可能不同。先 clone 安装版本的 tag，不行再读本项目 node_modules |
| 文档是 2.1，装的 2.4.0，差不多 | 有下限的能力必须对照版本；已删组件当不存在 |
| tag 没有就猜 / 直接停 | clone 失败后读 node_modules；也没有才停 |
| 再开一个 `dwy-eui-v2` skill | 对外只有 `dwy-eui` |
