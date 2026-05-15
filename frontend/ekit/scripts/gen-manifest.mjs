#!/usr/bin/env node
/**
 * 生成 dist/module-manifest.json
 *
 * 目的：给 AI（dwy-ekit skill）一份"导出索引"，让它在下游消费方项目里
 * 凭 node_modules/@dwydev/ekit/dist/module-manifest.json 就能定位
 * 每个 API 的精确类型文件，避免靠 SKILL.md 的过期签名表格。
 *
 * 工作原理：
 *   解析 src/index.ts 的 re-export 语句，建立"导出名 → 模块"映射，
 *   并列出每个模块在 dist/ 下的所有 .d.ts 文件。
 *
 * 输出结构（双索引）：
 * {
 *   "version": "0.8.0",
 *   "generatedAt": "...",
 *   "stats": { "modules": 11, "exports": 70 },
 *
 *   // 导出名 → 模块（AI 知道 API 名称时一步定位）
 *   "exportToModule": {
 *     "createRequest": "request",
 *     "HttpClient": "request",
 *     "useStorage": "storage",
 *     "now": "date"
 *   },
 *
 *   // 模块 → 详情（文件清单 + 该模块下所有导出）
 *   "modules": {
 *     "request": {
 *       "entry": "request/index.d.ts",
 *       "files": ["request/types.d.ts", "request/client.d.ts", "..."],
 *       "values": ["createRequest", "tokenPlugin", "..."],
 *       "types":  ["HttpClient", "HttpConfig", "..."]
 *     }
 *   }
 * }
 *
 * AI 使用顺序：
 *   1. exportToModule["createRequest"] → "request"
 *   2. modules["request"].entry → 读它拿到入口
 *   3. modules["request"].files → 类型详情在 types.d.ts，实现细节在 client.d.ts / plugins.d.ts
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkgRoot = join(__dirname, '..')
const indexPath = join(pkgRoot, 'src/index.ts')
const distDir = join(pkgRoot, 'dist')

const pkg = JSON.parse(readFileSync(join(pkgRoot, 'package.json'), 'utf8'))
const indexSrc = readFileSync(indexPath, 'utf8')

// 匹配 `export [type] { a, b, c } from './module[/sub]'`
// 捕获组：1 = 'type ' 或 undefined，2 = 名称列表，3 = 模块路径
const reExport = /export\s+(type\s+)?\{([^}]+)\}\s+from\s+['"]\.\/([^'"]+)['"]/g

const modules = {}
const exportToModule = {}

for (const match of indexSrc.matchAll(reExport)) {
  const isType = !!match[1]
  const names = match[2]
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s.split(/\s+as\s+/i).pop().trim())
  const modulePath = match[3] // 可能是 'request' 或 'hooks/vueuse'
  const topModule = modulePath.split('/')[0]

  if (!modules[topModule]) {
    modules[topModule] = { entry: `${topModule}/index.d.ts`, files: [], values: [], types: [] }
  }
  for (const name of names) {
    exportToModule[name] = topModule
    if (isType) modules[topModule].types.push(name)
    else modules[topModule].values.push(name)
  }
}

// 补全每个 module 在 dist/ 下的 .d.ts 文件清单
for (const mod of Object.keys(modules)) {
  const dir = join(distDir, mod)
  if (!existsSync(dir)) {
    console.warn(`[gen-manifest] 警告：模块 ${mod} 没有 dist 产物`)
    continue
  }
  const files = collectDtsFiles(dir, mod)
  modules[mod].files = files.sort()
  modules[mod].values.sort()
  modules[mod].types.sort()
}

const manifest = {
  version: pkg.version,
  generatedAt: new Date().toISOString(),
  stats: {
    modules: Object.keys(modules).length,
    exports: Object.keys(exportToModule).length,
  },
  exportToModule: sortObjectKeys(exportToModule),
  modules: sortObjectKeys(modules),
}

if (!existsSync(distDir)) {
  console.error(`dist 目录不存在: ${distDir}\n请先 pnpm build`)
  process.exit(1)
}

const outPath = join(distDir, 'module-manifest.json')
writeFileSync(outPath, JSON.stringify(manifest, null, 2) + '\n')

console.log(
  `[gen-manifest] 已生成 ${outPath}\n` +
    `  version: ${pkg.version}\n` +
    `  modules: ${manifest.stats.modules}\n` +
    `  exports: ${manifest.stats.exports}`,
)

// ---- helpers ----

function collectDtsFiles(dir, prefix) {
  const out = []
  for (const name of readdirSync(dir)) {
    const full = join(dir, name)
    if (statSync(full).isDirectory()) {
      out.push(...collectDtsFiles(full, `${prefix}/${name}`))
    } else if (name.endsWith('.d.ts') && !name.endsWith('.d.ts.map')) {
      out.push(`${prefix}/${name}`)
    }
  }
  return out
}

function sortObjectKeys(obj) {
  const sorted = {}
  for (const k of Object.keys(obj).sort()) sorted[k] = obj[k]
  return sorted
}
