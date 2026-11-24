/**
 * 扫描本机已装 skills / Claude plugins / Codex plugins，并按收藏与 dwy 模板标注来源。
 */

import { execFile } from 'node:child_process'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { promisify } from 'node:util'
import { loadCatalog } from './skills-catalog.js'
import { GLOBAL_SKILL_DEST_IDS, resolveGlobalSkillDir } from './sync-global-skills.js'

const execFileAsync = promisify(execFile)

/** 从 `claude plugin list` 文本中提取 plugin@marketplace。 */
export function parseClaudePluginList(text) {
  const found = new Set()
  for (const line of String(text || '').split(/\r?\n/)) {
    const match = line.match(/([A-Za-z0-9._-]+@[A-Za-z0-9._-]+)/)
    if (match) found.add(match[1])
  }
  return [...found]
}

/**
 * 解析 `codex plugin list --json`。
 * 只返回已安装项的 pluginId（name@marketplace）。
 *
 * @param {string|object} raw
 * @returns {string[]}
 */
export function parseCodexPluginList(raw) {
  let data = raw
  if (typeof raw === 'string') {
    const text = raw.trim()
    if (!text) return []
    try {
      data = JSON.parse(text)
    } catch {
      // 非 JSON 时回退到与 Claude 相同的 name@marketplace 抽取
      return parseClaudePluginList(text)
    }
  }
  const installed = Array.isArray(data?.installed)
    ? data.installed
    : Array.isArray(data)
      ? data.filter(item => item?.installed)
      : []
  const ids = []
  for (const item of installed) {
    const id = item?.pluginId || (item?.name && item?.marketplaceName
      ? `${item.name}@${item.marketplaceName}`
      : null)
    if (typeof id === 'string' && id.includes('@')) ids.push(id)
  }
  return [...new Set(ids)]
}

async function defaultListClaudePlugins() {
  try {
    const { stdout, stderr } = await execFileAsync('claude', ['plugin', 'list'], {
      timeout: 20000,
      maxBuffer: 2 * 1024 * 1024,
      env: { ...process.env, FORCE_COLOR: '0' },
    })
    return parseClaudePluginList(`${stdout}\n${stderr}`)
  } catch (error) {
    const text = `${error.stdout || ''}\n${error.stderr || ''}\n${error.message || ''}`
    return parseClaudePluginList(text)
  }
}

async function defaultListCodexPlugins() {
  try {
    const { stdout, stderr } = await execFileAsync('codex', ['plugin', 'list', '--json'], {
      timeout: 20000,
      maxBuffer: 4 * 1024 * 1024,
      env: { ...process.env, FORCE_COLOR: '0' },
    })
    return parseCodexPluginList(`${stdout}\n${stderr}`)
  } catch (error) {
    const text = `${error.stdout || ''}\n${error.stderr || ''}`
    if (text.trim()) return parseCodexPluginList(text)
    return []
  }
}

async function skillNamesInRoot(root) {
  if (!await fs.pathExists(root)) return []
  const names = []
  for (const entry of await fs.readdir(root, { withFileTypes: true })) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue
    const skillMd = path.join(root, entry.name, 'SKILL.md')
    if (await fs.pathExists(skillMd)) names.push(entry.name)
  }
  return names
}

/**
 * @param {{
 *   homeDir?: string,
 *   codexHome?: string,
 *   templateSkillNames?: Set<string> | string[],
 *   catalog?: { entries: object[] },
 *   listPlugins?: () => Promise<string[]>,
 *   listCodexPlugins?: () => Promise<string[]>,
 * }} [opts]
 */
export async function scanInstalledSkills({
  homeDir = os.homedir(),
  codexHome = process.env.CODEX_HOME || path.join(homeDir, '.codex'),
  templateSkillNames = [],
  catalog,
  listPlugins = defaultListClaudePlugins,
  listCodexPlugins = defaultListCodexPlugins,
} = {}) {
  const templates = templateSkillNames instanceof Set
    ? templateSkillNames
    : new Set(templateSkillNames)
  const loaded = catalog || await loadCatalog(homeDir)

  const catalogSkillNames = new Set()
  const catalogClaudePlugins = new Set()
  const catalogCodexPlugins = new Set()
  for (const entry of loaded.entries) {
    if (entry.kind === 'skills-cli') {
      if (entry.skills?.length) for (const name of entry.skills) catalogSkillNames.add(name)
      else catalogSkillNames.add(entry.id)
    }
    if (entry.kind === 'claude-plugin') catalogClaudePlugins.add(entry.source)
    if (entry.kind === 'codex-plugin') catalogCodexPlugins.add(entry.source)
  }

  /** @type {Map<string, { name: string, agents: string[], provenance: string }>} */
  const skills = new Map()
  for (const destId of GLOBAL_SKILL_DEST_IDS) {
    const root = resolveGlobalSkillDir(destId, homeDir)
    for (const name of await skillNamesInRoot(root)) {
      const current = skills.get(name) || { name, agents: [], provenance: 'unknown' }
      if (!current.agents.includes(destId)) current.agents.push(destId)
      skills.set(name, current)
    }
  }
  const codexSkills = path.join(codexHome, 'skills')
  for (const name of await skillNamesInRoot(codexSkills)) {
    const current = skills.get(name) || { name, agents: [], provenance: 'unknown' }
    if (!current.agents.includes('codex')) current.agents.push('codex')
    skills.set(name, current)
  }

  for (const item of skills.values()) {
    if (templates.has(item.name)) item.provenance = 'dwy-template'
    else if (catalogSkillNames.has(item.name)) item.provenance = 'catalog'
    else item.provenance = 'unknown'
  }

  const claudePlugins = (await listPlugins()).map(source => ({
    source,
    kind: 'claude-plugin',
    runtime: 'claude',
    provenance: catalogClaudePlugins.has(source) ? 'catalog' : 'unknown',
  }))
  const codexPlugins = (await listCodexPlugins()).map(source => ({
    source,
    kind: 'codex-plugin',
    runtime: 'codex',
    provenance: catalogCodexPlugins.has(source) ? 'catalog' : 'unknown',
  }))

  const plugins = [...claudePlugins, ...codexPlugins]
    .sort((a, b) => a.source.localeCompare(b.source) || a.runtime.localeCompare(b.runtime))

  return {
    skills: [...skills.values()].sort((a, b) => a.name.localeCompare(b.name)),
    plugins,
  }
}
