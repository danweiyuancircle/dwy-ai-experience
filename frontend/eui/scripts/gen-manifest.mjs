#!/usr/bin/env node
/**
 * 生成 dist/component-manifest.json
 *
 * 目的：给 AI（dwy-eui skill）一份"组件地图"，让它在下游消费方项目里
 * 凭 node_modules/@dwydev/eui/dist/component-manifest.json 就能定位
 * 每个组件的 props/emits 类型文件，避免靠 SKILL.md 的过期表格。
 *
 * 结构（双索引，紧凑）：
 * {
 *   "version": "2.1.0",
 *   "generatedAt": "...",
 *   "stats": { "directories": 87, "components": 117, "composables": 7 },
 *
 *   // 组件名 → 目录名（AI 知道组件名时一步定位）
 *   "componentToDir": {
 *     "EButton": "button",
 *     "ECommandInput": "command"
 *   },
 *
 *   // 目录 → { 类型文件, 该目录下所有组件 }（AI 拿到目录后看一眼就知道全貌）
 *   "directories": {
 *     "button": { "types": "components/button/types.d.ts", "components": ["EButton"] },
 *     "command": { "types": null, "components": ["ECommand", "ECommandInput", ...] }
 *   },
 *
 *   "composables": ["useMessage", "useTheme", ...]
 * }
 *
 * AI 使用顺序：
 *   1. 看 componentToDir["EButton"] 拿到 "button"
 *   2. 看 directories["button"].types → Read 这个文件拿 props/emits
 *   3. 看 directories["button"].components 知道该目录还有哪些兄弟组件
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkgRoot = join(__dirname, '..')
const componentsDir = join(pkgRoot, 'src/components')
const composablesDir = join(pkgRoot, 'src/composables')
const distDir = join(pkgRoot, 'dist')

const pkg = JSON.parse(readFileSync(join(pkgRoot, 'package.json'), 'utf8'))

const componentToDir = {}
const directories = {}

const dirs = readdirSync(componentsDir).filter((name) =>
  statSync(join(componentsDir, name)).isDirectory(),
)

for (const kebab of dirs.sort()) {
  const dir = join(componentsDir, kebab)
  const vueFiles = readdirSync(dir)
    .filter((f) => /^E.+\.vue$/.test(f))
    .map((f) => f.replace(/\.vue$/, ''))
    .sort()
  if (vueFiles.length === 0) continue

  const hasTypes = existsSync(join(dir, 'types.ts'))

  directories[kebab] = {
    types: hasTypes ? `components/${kebab}/types.d.ts` : null,
    components: vueFiles,
  }

  for (const name of vueFiles) {
    componentToDir[name] = kebab
  }
}

// composables：扫描 src/composables/*.ts，提取 export use* 函数
const composables = []
if (existsSync(composablesDir)) {
  for (const f of readdirSync(composablesDir)) {
    if (!f.endsWith('.ts') || f === 'index.ts') continue
    const content = readFileSync(join(composablesDir, f), 'utf8')
    const matches = content.matchAll(/export\s+(?:function|const)\s+(use[A-Z]\w*)/g)
    for (const m of matches) {
      if (!composables.includes(m[1])) composables.push(m[1])
    }
  }
  composables.sort()
}

const manifest = {
  version: pkg.version,
  generatedAt: new Date().toISOString(),
  stats: {
    directories: Object.keys(directories).length,
    components: Object.keys(componentToDir).length,
    composables: composables.length,
  },
  componentToDir,
  directories,
  composables,
}

if (!existsSync(distDir)) {
  console.error(`dist 目录不存在: ${distDir}\n请先 pnpm build`)
  process.exit(1)
}

const outPath = join(distDir, 'component-manifest.json')
writeFileSync(outPath, JSON.stringify(manifest, null, 2) + '\n')

console.log(
  `[gen-manifest] 已生成 ${outPath}\n` +
    `  version: ${pkg.version}\n` +
    `  directories: ${manifest.stats.directories}\n` +
    `  components: ${manifest.stats.components}\n` +
    `  composables: ${manifest.stats.composables}`,
)
