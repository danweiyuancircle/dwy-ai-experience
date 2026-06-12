# JS/TS 商业版 SDK 完整打包指南

目标：发布到 npm 的 `.tgz` 内**不含 src/、不含 sourcemap、不含 tsconfig**，只含压缩后的 `dist/` 与 `.d.ts` 类型定义。

## 关键原则

- `package.json` 的 `files` 字段是**白名单**，优先级高于 `.npmignore`
- 用 `tsup` 或 `rollup` 打包，强制 `minify: true` + `sourcemap: false` + `legalComments: 'none'`
- `.d.ts` 单独生成（用户要类型提示），但不能带 `.d.ts.map`（会映射回源码）

## 工具选择

| 工具 | 优势 | 推荐场景 |
|---|---|---|
| **tsup** | 零配置、内置 dts + 多格式 | **默认选择** |
| rollup + rollup-plugin-dts | 配置灵活、生态成熟 | 复杂 bundle 拆分 |
| esbuild | 最快、最小 | 简单单文件 SDK |

下面以 tsup 为准。

## 项目结构示例

```
mysdk/
├── package.json
├── tsup.config.ts
├── tsconfig.json                   # 仅本地用，不发
├── .gitignore
├── .npmignore                      # 可选（files 优先）
├── src/
│   ├── index.ts                    # 入口
│   ├── client.ts                   # 公开 API
│   └── _internal/                  # 内部模块
│       └── engine.ts
└── dist/                           # 构建产物（唯一发布内容）
    ├── index.js                    # ESM，minified
    ├── index.cjs                   # CJS，minified
    └── index.d.ts                  # 类型定义（无 .map）
```

## tsup.config.ts

```typescript
import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,                  // 生成 .d.ts
  sourcemap: false,           // 关键：不生成 .map（防止源码可还原）
  minify: true,               // 压缩
  legalComments: 'none',      // 去掉 /*! */ 版权注释（可能含路径）
  splitting: false,           // 不拆分（防止内部模块结构暴露）
  clean: true,                // 构建前清 dist/
  treeshake: true,
})
```

## package.json

```json
{
  "name": "@dwydev/mysdk",
  "version": "1.0.0",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsup",
    "prepublishOnly": "pnpm build && npm pack --dry-run"
  },
  "publishConfig": {
    "registry": "https://registry.npmjs.org/",
    "access": "public"
  }
}
```

`files` 白名单只列 3 项 → 其他全部不发（src/、tests/、tsconfig.json、tsup.config.ts、node_modules/ 自动不发）。

## 构建命令

```bash
# 清理 + 打包
rm -rf dist/
pnpm build

# 验证 dist/ 无 .map
find dist -name '*.map' -type f && echo "FAIL: sourcemap leaked" || echo "OK: no sourcemap"

# 干跑看 .tgz 内容
npm pack --dry-run --json | jq '.[] | .files[] | .path'
```

## 验收清单（流程 B 用）

| 检查项 | 命令 |
|---|---|
| package.json 有 files 白名单 | `jq '.files \| length > 0' package.json` |
| files 不含 src/ | `jq '.files \| any(. == "src" or . == "src/")' package.json` 应为 false |
| tsup 配置 minify + 无 sourcemap | `grep -E 'minify.*true' tsup.config.*` + `grep -E 'sourcemap.*false' tsup.config.*` |
| dist/ 下无 .map | `find dist -name '*.map'` 应为空 |
| .gitignore 含 .env / *.tsbuildinfo | `grep -E '\.env\\|\.tsbuildinfo' .gitignore` |

## 常见踩坑

| 现象 | 原因 | 修复 |
|---|---|---|
| 用 `.npmignore` 但 files 也定义了 | `files` 优先，`.npmignore` 被忽略 | 二选一，推荐只用 `files` |
| `.tgz` 里有 `.DS_Store` | macOS 系统文件，没被 ignore | `.gitignore` 加 `.DS_Store`；npm 默认会带 .gitignore 规则 |
| 发布后 .d.ts 含内部路径 | tsup 生成的 .d.ts 没合并 | 用 `dts: { resolve: true }` 合并所有类型，或改用 rollup-plugin-dts |
| 装完后用户 IDE 跳转到 minified 代码 | `.d.ts.map` 不小心发了 | 检查 `dist/` 无 `.d.ts.map`，tsup 默认不生成 |
| `bin` 字段指向的 CLI 被压缩后报 "no entry" | 缺 shebang `#!/usr/bin/env node` | tsup 配 `banner: { js: '#!/usr/bin/env node' }` |

## 参考 dwy-shared 内已有 SDK

`frontend/eui/` / `frontend/ekit/` 当前是**开源版**（Vite 构建，含 `vite-plugin-dts`）。若要转商业版：
1. 把 Vite 换成 tsup（或在 Vite 配置加 `build.minify: 'terser'` + `build.sourcemap: false`）
2. `package.json` 添加 `files: ["dist", "README.md", "LICENSE"]`
3. 删除 `dist/` 下所有 `.map` 文件
4. 跑 `npm pack --dry-run` 验收
