/** 安装本次实际 tgz 到全新消费目录；需先 build，不使用源码或 workspace 链接。 */
import { execFileSync } from 'node:child_process'
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const temporary = mkdtempSync(join(tmpdir(), 'auth-web-tgz-smoke-'))
try {
  execFileSync('pnpm', ['pack', '--pack-destination', temporary], { cwd: root, stdio: 'pipe' })
  const name = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version
  writeFileSync(join(temporary, 'package.json'), JSON.stringify({
    name: 'auth-web-consumer-smoke', private: true, type: 'module',
    dependencies: {
      '@dwydev/auth-web': `file:./dwydev-auth-web-${name}.tgz`,
      '@dwydev/eui': '2.7.1', 'vue': '3.5.32', 'lucide-vue-next': '1.0.0',
    },
  }, null, 2))
  execFileSync('pnpm', ['install', '--ignore-scripts', '--no-frozen-lockfile'], { cwd: temporary, stdio: 'pipe' })
  copyFileSync(join(root, 'tests/fixtures/consumer-smoke.mjs'), join(temporary, 'smoke.mjs'))
  console.log(execFileSync(process.execPath, ['smoke.mjs'], { cwd: temporary, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim())
} catch (cause) {
  console.error(cause.stdout?.toString() ?? '', cause.stderr?.toString() ?? '')
  throw cause
} finally {
  rmSync(temporary, { recursive: true, force: true })
}
