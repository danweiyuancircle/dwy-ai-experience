/**
 * dwy 自升级：把全局安装的 create-dwy 升到 npm dist-tag latest（正式版）。
 * 不引入第三方更新器，安装命令走用户本机 npm/pnpm/yarn/bun。
 * 源码目录 / 非全局安装拒绝执行，避免把仓库工作树覆盖成 npm 包。
 */

import { execFile, spawn } from 'node:child_process'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { promisify } from 'node:util'
import { PACKAGE_ROOT, chalk } from './utils.js'

/** npm 包名，bin 是 dwy */
export const PACKAGE_NAME = 'create-dwy'

const DEFAULT_REGISTRY = 'https://registry.npmjs.org/'
const execFileAsync = promisify(execFile)

function upgradeRegistry() {
  const value = process.env.npm_config_registry || DEFAULT_REGISTRY
  let registry
  try {
    registry = new URL(value)
  } catch {
    throw new Error('npm_config_registry 必须是有效的 HTTP(S) registry 地址')
  }
  if (process.platform === 'win32' && /[&|<>^%!"()\r\n]/.test(value + registry.href)) {
    throw new Error('npm_config_registry 含 Windows 命令解释器不支持的字符')
  }
  if (!['http:', 'https:'].includes(registry.protocol) || registry.search || registry.hash) {
    throw new Error('npm_config_registry 必须是无查询参数及片段的 HTTP(S) registry 地址')
  }
  // 原生 fetch 不支持 URL 凭据，直接传入会在错误消息里泄露原地址。
  if (registry.username || registry.password) throw new Error('npm_config_registry 不支持 URL 内嵌凭据')
  return registry.href.replace(/\/?$/, '/')
}

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
 * 固定本轮查询到的正式版本及 registry，避免安装器的镜像 latest 滞后导致降回旧包。
 *
 * @param {'npm' | 'pnpm' | 'yarn' | 'bun' | 'unknown'} installer
 * @param {string} version 来自已校验的正式版本查询结果
 * @returns {[string, string[]] | null}
 */
export function buildUpgradeCommand(installer, version) {
  const spec = `${PACKAGE_NAME}@${version}`, registry = `--registry=${upgradeRegistry()}`
  if (installer === 'pnpm') return ['pnpm', ['add', '-g', spec, registry]]
  if (installer === 'yarn') return ['yarn', ['global', 'add', spec, registry]]
  if (installer === 'bun') return ['bun', ['add', '-g', spec, registry]]
  if (installer === 'npm') return ['npm', ['install', '-g', spec, registry]]
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
  const registry = upgradeRegistry()
  const url = `${registry}${PACKAGE_NAME}/latest`
  const response = await fetchFn(url, { headers: { Accept: 'application/json', 'User-Agent': 'create-dwy' } })
  if (!response.ok) {
    const { origin, pathname } = new URL(url)
    throw new Error(`查询最新版本失败：${origin}${pathname} HTTP ${response.status}`)
  }
  const body = await response.json()
  const version = body?.version
  if (typeof version !== 'string' || !/^\d+\.\d+\.\d+$/.test(version)) {
    throw new Error('npm latest 未返回有效的正式 version')
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

async function readActiveVersion() {
  const { stdout } = await execFileAsync('dwy', ['--version'], {
    shell: process.platform === 'win32', timeout: 10000,
  })
  const version = stdout.trim()
  if (!/^\d+\.\d+\.\d+$/.test(version)) throw new Error('无法从当前 PATH 中的 dwy 读取有效版本')
  return version
}

/**
 * 执行自升级。返回结构化结果供测试断言；失败抛错。
 *
 * @param {object} [opts]
 * @param {string} [opts.currentVersion]
 * @param {string} [opts.pkgRoot]
 * @param {() => Promise<string>} [opts.fetchLatest]
 * @param {(cmd: string, args: string[]) => Promise<void>} [opts.runCommand]
 * @param {() => Promise<string>} [opts.readInstalledVersion] 回读 PATH 中实际将用于刷新的 CLI 版本
 */
export async function selfUpgrade({
  currentVersion,
  pkgRoot = PACKAGE_ROOT,
  fetchLatest = fetchLatestVersion,
  runCommand = runSpawn,
  readInstalledVersion = readActiveVersion,
} = {}) {
  const current = currentVersion || readCurrentVersion(pkgRoot)
  const installer = detectInstaller(pkgRoot)
  if (installer === 'unknown') {
    throw new Error(
      `当前不是全局安装的 ${PACKAGE_NAME}（路径 ${pkgRoot}），无法自升级。请先 npm i -g ${PACKAGE_NAME}，或在源码仓 git pull。`,
    )
  }

  const latest = await fetchLatest()
  const cmp = compareVersions(current, latest)
  if (cmp > 0) {
    console.log(chalk.yellow(`当前 ${current} 新于 npm latest ${latest}，不降级`))
    return { status: 'newer-local', current, latest, installer }
  }

  if (cmp < 0) {
    const [cmd, args] = buildUpgradeCommand(installer, latest)
    console.log(chalk.blue(`升级 ${PACKAGE_NAME} ${current} → ${latest}`))
    console.log(chalk.gray(`  ${cmd} ${args.join(' ')}`))
    await runCommand(cmd, args)
  }
  const installed = await readInstalledVersion()
  if (installed !== latest) {
    throw new Error(`升级未生效：目标 ${latest}，当前 PATH 中 dwy --version 为 ${installed}；未刷新共享 Skills。请检查全局安装路径与 registry。`)
  }
  try {
    // 必须启动新安装的 CLI；pnpm 升级后旧进程的模块路径仍可能指向旧版本。
    await runCommand('dwy', ['refresh'])
  } catch (error) {
    throw new Error(`CLI ${installed} 已就绪，但配置刷新失败：${error.message}`, { cause: error })
  }
  if (cmp === 0) {
    console.log(chalk.green(`已是最新正式版 ${installed}`))
    return { status: 'up-to-date', current, latest, installer }
  }
  console.log(chalk.green(`已升级到 ${latest}`))
  return { status: 'upgraded', current, latest, installer }
}
