/**
 * dwy 自升级：把全局安装的 create-dwy 升到 npm dist-tag latest（正式版）。
 * 不引入第三方更新器，安装命令走用户本机 npm/pnpm/yarn/bun。
 * 源码目录 / 非全局安装拒绝执行，避免把仓库工作树覆盖成 npm 包。
 */

import { spawn } from 'node:child_process'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { PACKAGE_ROOT, chalk } from './utils.js'

/** npm 包名，bin 是 dwy */
export const PACKAGE_NAME = 'create-dwy'

const DEFAULT_REGISTRY = 'https://registry.npmjs.org/'

/**
 * 比较 a、b 两个三段版本号。a>b 返回 1，相等 0，a<b -1。
 * 只处理正式版 MAJOR.MINOR.PATCH，不解析 beta。
 *
 * @param {string} a
 * @param {string} b
 */
export function compareVersions(a, b) {
  const parse = (v) => v.split('.').map(part => Number.parseInt(part, 10) || 0)
  const left = parse(a)
  const right = parse(b)
  for (let i = 0; i < 3; i++) {
    if (left[i] > right[i]) return 1
    if (left[i] < right[i]) return -1
  }
  return 0
}

/**
 * 根据包安装路径判断全局包管理器。
 * pnpm/yarn/bun 路径里也常有 node_modules/create-dwy，必须先匹配专用目录。
 *
 * @param {string} pkgRoot
 * @returns {'npm' | 'pnpm' | 'yarn' | 'bun' | 'unknown'}
 */
export function detectInstaller(pkgRoot) {
  const normalized = pkgRoot.replace(/\\/g, '/')
  if (normalized.includes('/pnpm/global/') || normalized.includes('/.local/share/pnpm/')) return 'pnpm'
  if (normalized.includes('/yarn/global/') || normalized.includes('/.yarn/')) return 'yarn'
  if (normalized.includes('/.bun/install/')) return 'bun'
  if (normalized.endsWith('/node_modules/create-dwy')) return 'npm'
  return 'unknown'
}

/**
 * 构造升级命令。一律钉 @latest，不用 @next/@beta。
 *
 * @param {'npm' | 'pnpm' | 'yarn' | 'bun' | 'unknown'} installer
 * @returns {[string, string[]] | null}
 */
export function buildUpgradeCommand(installer) {
  const spec = `${PACKAGE_NAME}@latest`
  if (installer === 'pnpm') return ['pnpm', ['add', '-g', spec]]
  if (installer === 'yarn') return ['yarn', ['global', 'add', spec]]
  if (installer === 'bun') return ['bun', ['add', '-g', spec]]
  if (installer === 'npm') return ['npm', ['install', '-g', spec]]
  return null
}

/**
 * 读当前包版本。测试可注入 currentVersion，避免读盘。
 *
 * @param {string} [pkgRoot]
 */
function readCurrentVersion(pkgRoot = PACKAGE_ROOT) {
  const pkg = JSON.parse(readFileSync(path.join(pkgRoot, 'package.json'), 'utf-8'))
  return pkg.version
}

/**
 * 查 npm registry 的 latest。用官方 JSON，不跟浮动 tag 以外的通道。
 *
 * @param {typeof fetch} [fetchFn]
 */
export async function fetchLatestVersion(fetchFn = globalThis.fetch) {
  const registry = (process.env.npm_config_registry || DEFAULT_REGISTRY).replace(/\/?$/, '/')
  const url = `${registry}${PACKAGE_NAME}/latest`
  const response = await fetchFn(url, { headers: { Accept: 'application/json', 'User-Agent': 'create-dwy' } })
  if (!response.ok) {
    throw new Error(`查询最新版本失败：${url} HTTP ${response.status}`)
  }
  const body = await response.json()
  const version = body?.version
  if (!version || typeof version !== 'string') {
    throw new Error(`npm latest 未返回 version：${url}`)
  }
  return version
}

/**
 * 跑包管理器命令，stdio 继承方便用户看安装进度。
 * Windows 要 shell，才能找到 npm.cmd。
 *
 * @param {string} cmd
 * @param {string[]} args
 */
function runSpawn(cmd, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      stdio: 'inherit',
      shell: process.platform === 'win32',
    })
    child.on('error', reject)
    child.on('exit', (code) => {
      if (code === 0) resolve()
      else reject(new Error(`${cmd} ${args.join(' ')} 退出码 ${code}`))
    })
  })
}

/**
 * 执行自升级。返回结构化结果供测试断言；失败抛错。
 *
 * @param {object} [opts]
 * @param {string} [opts.currentVersion]
 * @param {string} [opts.pkgRoot]
 * @param {() => Promise<string>} [opts.fetchLatest]
 * @param {(cmd: string, args: string[]) => Promise<void>} [opts.runCommand]
 */
export async function selfUpgrade({
  currentVersion,
  pkgRoot = PACKAGE_ROOT,
  fetchLatest = fetchLatestVersion,
  runCommand = runSpawn,
} = {}) {
  const current = currentVersion || readCurrentVersion(pkgRoot)
  const installer = detectInstaller(pkgRoot)
  const command = buildUpgradeCommand(installer)
  if (!command) {
    throw new Error(
      `当前不是全局安装的 ${PACKAGE_NAME}（路径 ${pkgRoot}），无法自升级。请先 npm i -g ${PACKAGE_NAME}，或在源码仓 git pull。`,
    )
  }

  const latest = await fetchLatest()
  const cmp = compareVersions(current, latest)
  if (cmp === 0) {
    console.log(chalk.green(`已是最新正式版 ${current}`))
    return { status: 'up-to-date', current, latest, installer }
  }
  if (cmp > 0) {
    console.log(chalk.yellow(`当前 ${current} 新于 npm latest ${latest}，不降级`))
    return { status: 'newer-local', current, latest, installer }
  }

  const [cmd, args] = command
  console.log(chalk.blue(`升级 ${PACKAGE_NAME} ${current} → ${latest}`))
  console.log(chalk.gray(`  ${cmd} ${args.join(' ')}`))
  await runCommand(cmd, args)
  console.log(chalk.green(`已升级到 ${latest}`))
  return { status: 'upgraded', current, latest, installer }
}
