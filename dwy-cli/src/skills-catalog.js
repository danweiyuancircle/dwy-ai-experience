/**
 * 第三方 skills/plugins 全局收藏清单。
 * 只存可迁移的源信息，不存绝对路径与凭据；安装执行交给官方 CLI。
 */

import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'

const CATALOG_VERSION = 1
const KINDS = new Set([
  'skills-cli',
  'claude-plugin',
  'claude-marketplace',
  'codex-plugin',
  'codex-marketplace',
])

/** @param {string} [homeDir] */
export function catalogPath(homeDir = os.homedir()) {
  return path.join(homeDir, '.dwy', 'skills-catalog', 'catalog.json')
}

function emptyCatalog() {
  return { version: CATALOG_VERSION, entries: [] }
}

/**
 * 规范化一条收藏。缺 id 时用 source；拒绝绝对路径与未知 kind。
 *
 * @param {object} raw
 */
export function normalizeEntry(raw) {
  if (!raw || typeof raw !== 'object') throw new Error('catalog entry 无效')
  const kind = raw.kind
  if (!KINDS.has(kind)) throw new Error(`catalog entry kind 无效: ${kind}`)

  const source = typeof raw.source === 'string' ? raw.source.trim() : ''
  if (!source) throw new Error('catalog entry source 不能为空')
  if (path.isAbsolute(source) || /^[A-Za-z]:[\\/]/.test(source)) {
    throw new Error('catalog entry 禁止绝对路径')
  }
  for (const key of ['path', 'installLocation', 'localPath']) {
    if (raw[key]) throw new Error('catalog entry 禁止绝对路径字段')
  }

  const id = (typeof raw.id === 'string' && raw.id.trim()) || source
  const entry = {
    id,
    kind,
    source,
    added_at: typeof raw.added_at === 'string' && raw.added_at ? raw.added_at : new Date().toISOString(),
  }

  if (Array.isArray(raw.skills)) {
    entry.skills = [...new Set(raw.skills.filter(name => typeof name === 'string' && name.trim()))]
  }
  if (Array.isArray(raw.agents)) {
    entry.agents = [...new Set(raw.agents.filter(name => typeof name === 'string' && name.trim()))]
  }
  if (typeof raw.note === 'string' && raw.note.trim()) entry.note = raw.note.trim()

  return entry
}

/** @param {string} [homeDir] */
export async function loadCatalog(homeDir = os.homedir()) {
  const file = catalogPath(homeDir)
  if (!await fs.pathExists(file)) return emptyCatalog()
  const raw = await fs.readJson(file)
  const entries = Array.isArray(raw?.entries)
    ? raw.entries.map(entry => normalizeEntry(entry))
    : []
  return { version: CATALOG_VERSION, entries }
}

/** @param {string} homeDir @param {{ version: number, entries: object[] }} catalog */
export async function saveCatalog(homeDir, catalog) {
  const file = catalogPath(homeDir)
  await fs.ensureDir(path.dirname(file))
  const entries = (catalog.entries || []).map(entry => normalizeEntry(entry))
  await fs.writeJson(file, { version: CATALOG_VERSION, entries }, { spaces: 2 })
  return { version: CATALOG_VERSION, entries }
}

/** @param {string} homeDir @param {object} raw */
export async function addCatalogEntry(homeDir, raw) {
  const entry = normalizeEntry(raw)
  const catalog = await loadCatalog(homeDir)
  const idx = catalog.entries.findIndex(item => item.id === entry.id)
  if (idx >= 0) {
    entry.added_at = catalog.entries[idx].added_at
    catalog.entries[idx] = entry
  } else {
    catalog.entries.push(entry)
  }
  await saveCatalog(homeDir, catalog)
  return entry
}

/** @param {string} homeDir @param {string} id */
export async function removeCatalogEntry(homeDir, id) {
  const catalog = await loadCatalog(homeDir)
  const next = catalog.entries.filter(entry => entry.id !== id)
  if (next.length === catalog.entries.length) {
    throw new Error(`收藏中不存在: ${id}`)
  }
  await saveCatalog(homeDir, { ...catalog, entries: next })
}

/** @param {string} homeDir @param {string} file */
export async function exportCatalog(homeDir, file) {
  const catalog = await loadCatalog(homeDir)
  await fs.ensureDir(path.dirname(path.resolve(file)))
  await fs.writeJson(file, catalog, { spaces: 2 })
  return catalog
}

/**
 * 导入收藏。默认 merge：同 id 覆盖；merge=false 则整表替换。
 *
 * @param {string} homeDir
 * @param {string} file
 * @param {{ merge?: boolean }} [opts]
 */
export async function importCatalog(homeDir, file, { merge = true } = {}) {
  const raw = await fs.readJson(file)
  const incoming = Array.isArray(raw?.entries)
    ? raw.entries.map(entry => normalizeEntry(entry))
    : []
  if (!merge) {
    return saveCatalog(homeDir, { version: CATALOG_VERSION, entries: incoming })
  }
  const catalog = await loadCatalog(homeDir)
  const byId = new Map(catalog.entries.map(entry => [entry.id, entry]))
  for (const entry of incoming) byId.set(entry.id, entry)
  return saveCatalog(homeDir, { version: CATALOG_VERSION, entries: [...byId.values()] })
}
