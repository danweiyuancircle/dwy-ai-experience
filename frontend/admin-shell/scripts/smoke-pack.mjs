/** 构建后用实际 tgz 在干净目录安装，并验证子入口、泛型和真实组件渲染。 */
import { execFileSync } from 'node:child_process'
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const temporary = mkdtempSync(join(tmpdir(), 'admin-kit-consumer-'))
const metadata = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'))
try {
  execFileSync('pnpm', ['pack', '--pack-destination', temporary], { cwd: root, stdio: 'pipe' })
  // 基础包也使用本轮实际 tgz，不要求尚未发行的源码已经出现在 registry。
  const foundation = {}
  for (const directory of ['eui', 'ekit']) {
    const directoryRoot = join(dirname(root), directory)
    const info = JSON.parse(readFileSync(join(directoryRoot, 'package.json'), 'utf8'))
    execFileSync('pnpm', ['pack', '--pack-destination', temporary], { cwd: directoryRoot, stdio: 'pipe' })
    foundation[info.name] = `file:./dwydev-${directory}-${info.version}.tgz`
  }
  writeFileSync(join(temporary, 'package.json'), JSON.stringify({
    name: 'admin-kit-consumer-smoke', private: true, type: 'module', packageManager: 'pnpm@10.19.0',
    dependencies: {
      '@dwydev/admin-kit': `file:./dwydev-admin-kit-${metadata.version}.tgz`,
      ...foundation,
      vue: '3.5.32', 'vue-router': '4.6.4', 'lucide-vue-next': '1.0.0',
      '@vueuse/core': '14.4.0', tailwindcss: '4.2.3', 'vue-sonner': '2.0.9',
      zod: '3.25.76', axios: '1.15.1', dayjs: '1.11.20', typescript: '5.9.3',
      vite: '8.0.3',
    },
  }, null, 2))
  execFileSync('pnpm', ['install', '--ignore-scripts', '--strict-peer-dependencies', '--no-frozen-lockfile', '--registry=https://registry.npmjs.org'], {
    cwd: temporary, stdio: 'pipe',
  })
  for (const name of ['consumer-smoke.mjs', 'consumer-types.ts']) {
    copyFileSync(join(root, 'tests/fixtures', name), join(temporary, name))
  }
  writeFileSync(join(temporary, 'tsconfig.json'), JSON.stringify({
    compilerOptions: { strict: true, noEmit: true, skipLibCheck: true, target: 'ES2022', module: 'ESNext', moduleResolution: 'Bundler' },
    include: ['consumer-types.ts'],
  }))
  execFileSync('pnpm', ['exec', 'tsc', '--project', 'tsconfig.json'], { cwd: temporary, stdio: 'pipe' })
  // 按真实 Vue/Vite 消费路径打包 SSR；现有 ekit 的 dayjs 子路径需要 bundler 解析。
  writeFileSync(join(temporary, 'smoke-vite.config.mjs'), `export default {
    ssr: { noExternal: true },
    build: { ssr: 'consumer-smoke.mjs', outDir: 'bundle', minify: false,
      rolldownOptions: { output: { entryFileNames: 'consumer-smoke.mjs' } } },
  }`)
  execFileSync('pnpm', ['exec', 'vite', 'build', '--config', 'smoke-vite.config.mjs'], { cwd: temporary, stdio: 'pipe' })
  console.log(execFileSync(process.execPath, ['bundle/consumer-smoke.mjs'], {
    cwd: temporary, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
  }).trim())
} catch (cause) {
  console.error(cause.stdout?.toString() ?? '', cause.stderr?.toString() ?? '')
  throw cause
} finally {
  rmSync(temporary, { recursive: true, force: true })
}
