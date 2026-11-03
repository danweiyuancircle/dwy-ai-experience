import fs from 'fs-extra'
import path from 'node:path'
import { buildClaudeHooksSettings, isManagedClaudeHookCommand, mergeClaudeHooks, loadHookManifests, scanHooks } from './sync.js'
import { buildCodexHooksJson, hasManagedBaseline, isManagedCodexHookCommand, mergeCodexHooks } from './sync-codex.js'

/** Hook 配置文件名由平台决定，Codex 根目录由调用方解析。 */
export function hookConfigFile(platform, root) {
  return path.join(root, platform === 'claude' ? 'settings.json' : 'hooks.json')
}

async function readHookConfig(platform, root) {
  const file = hookConfigFile(platform, root)
  if (!await fs.pathExists(file)) return {}
  const config = await fs.readJson(file)
  if (!config || typeof config !== 'object' || Array.isArray(config)
    || (config.hooks !== undefined && (!config.hooks || typeof config.hooks !== 'object' || Array.isArray(config.hooks)))) {
    throw new Error(`Hook 配置格式无效：${file}`)
  }
  for (const configs of Object.values(config.hooks || {})) {
    if (!Array.isArray(configs) || configs.some(cfg => !cfg || typeof cfg !== 'object' || !Array.isArray(cfg.hooks)
      || cfg.hooks.some(hook => !hook || typeof hook !== 'object'))) throw new Error(`Hook 配置格式无效：${file}`)
  }
  return config
}

/** 查找待移除名称的托管注册；不要求脚本仍在，便于清理坏配置。 */
export async function hasManagedHookConfig(platform, root, names) {
  const config = await readHookConfig(platform, root)
  const matches = platform === 'claude' ? isManagedClaudeHookCommand : isManagedCodexHookCommand
  return Object.values(config.hooks || {}).some(configs => configs.some(cfg => cfg.hooks.some(hook => matches(hook.command, names, root))))
}

/** 不隐式改变用户的全局禁用开关；启用前明确报告冲突。 */
export async function assertHooksEnabled(platform, root) {
  if ((await readHookConfig(platform, root)).disableAllHooks === true) throw new Error(`Hooks 被 disableAllHooks 禁用，无法启用：${hookConfigFile(platform, root)}`)
}

/** 只移除指定托管脚本和注册，不补装或更新其他 Hooks。 */
export async function removeManagedHooks(platform, root, names, paths) {
  const file = hookConfigFile(platform, root)
  if (paths.includes(file)) {
    const config = await readHookConfig(platform, root)
    const merge = platform === 'claude' ? mergeClaudeHooks : mergeCodexHooks
    const nextHooks = merge(config.hooks, undefined, names, root)
    const next = { ...config }
    if (nextHooks) next.hooks = nextHooks
    else delete next.hooks
    if (JSON.stringify(config) !== JSON.stringify(next)) {
      if (Object.keys(next).length) await fs.writeJson(file, next, { spaces: 2 })
      else await fs.remove(file)
    }
  }
  for (const dest of paths) if (dest !== file) await fs.remove(dest)
}

/** 解析通用规范的原生全局入口；Cursor 没有文件入口。 */
export function globalBaselinePath(platform, homeDir, codexHome) {
  return { claude: path.join(homeDir, '.claude', 'CLAUDE.md'), codex: path.join(codexHome, 'AGENTS.md'),
    opencode: path.join(homeDir, '.config', 'opencode', 'AGENTS.md') }[platform]
}

/** 返回所选 CLI 中实际提供 dwy 全局通用规范的平台。 */
export async function baselineProviders(platforms, { homeDir, codexHome }) {
  const providers = []
  for (const platform of platforms) {
    const dest = globalBaselinePath(platform, homeDir, codexHome)
    if (dest && await hasManagedBaseline(dest)) providers.push(platform)
  }
  return providers
}

/** 全局 Hook 必须在对应事件及 matcher 下注册了完整执行命令，且脚本仍有效。 */
export async function globalHookNames({ platform, sourceDir, homeDir, codexHome }) {
  if (!['claude', 'codex'].includes(platform)) return new Set()
  const root = platform === 'claude' ? path.join(homeDir, '.claude') : codexHome
  const config = await readHookConfig(platform, root)
  if (config.disableAllHooks === true) return new Set()
  const manifests = await loadHookManifests(sourceDir)
  const result = new Set()
  for (const hook of await scanHooks(sourceDir)) {
    const names = new Set([hook.name])
    const generated = platform === 'claude' ? buildClaudeHooksSettings(manifests, names, true)
      : buildCodexHooksJson(manifests, names, true, root)
    const registrations = Object.entries(generated.hooks || {}).flatMap(([event, configs]) =>
      configs.flatMap(cfg => cfg.hooks.map(command => ({ event, matcher: cfg.matcher, command: command.command }))))
    if (registrations.length === 0) continue
    const registered = registrations.every(expected => {
      const configs = config.hooks?.[expected.event] || []
      return configs.some(cfg => cfg.matcher === expected.matcher && Array.isArray(cfg.hooks)
        && cfg.hooks.some(item => item.type === 'command' && item.command === expected.command))
    })
    if (!registered) continue
    const stat = await fs.stat(path.join(root, 'hooks', hook.name)).catch(error => {
      if (['ENOENT', 'ENOTDIR', 'ELOOP'].includes(error.code)) return null
      throw error
    })
    if (stat?.isFile()) result.add(hook.name)
  }
  return result
}

/** 配置写入与清理不能穿透边界内的目录或文件链接；确认前及执行时均检查。 */
export async function assertConfigPath(dest, root) {
  const nearest = async start => {
    let current = start
    while (!await fs.lstat(current).catch(error => { if (error.code === 'ENOENT') return null; throw error })) current = path.dirname(current)
    return current
  }
  const base = await nearest(root)
  const expectedRoot = path.resolve(await fs.realpath(base), path.relative(base, root))
  const entry = await nearest(dest)
  const expected = path.resolve(expectedRoot, path.relative(root, entry))
  let actual
  try { actual = await fs.realpath(entry) } catch (error) {
    if (!['ENOENT', 'ELOOP', 'ENOTDIR'].includes(error.code)) throw error
    throw new Error(`配置入口为无效链接，保留原入口：${entry}`)
  }
  if (actual !== expected) throw new Error(`配置入口链接指向外部位置，保留原入口：${entry}`)
}
