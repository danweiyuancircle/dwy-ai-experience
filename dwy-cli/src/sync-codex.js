import fs from 'fs-extra'
import path from 'path'
import { chalk } from './utils.js'
import { linkSkill, ensureSharedSkills, removeSkillEntry } from './skill-store.js'
import {
  extractDescription,
  loadHookManifests,
  scanSkills,
  scanHooks,
  resolveSourceDir,
  copyFilter,
  logAction,
} from './sync.js'

const BASELINE_START = '<!-- DWY-BASELINE:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->'
const BASELINE_END = '<!-- DWY-BASELINE:END -->'
const BASELINE_RE = /<!-- DWY-BASELINE:START[\s\S]*?DWY-BASELINE:END -->/
const BLOCK_START = '<!-- DWY-RULES:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->'
const BLOCK_END = '<!-- DWY-RULES:END -->'
const BLOCK_RE = /<!-- DWY-RULES:START[\s\S]*?DWY-RULES:END -->/

// ---------- rules → AGENTS.md ----------

function parseRulePaths(frontmatter) {
  const m = frontmatter.match(/^paths:\s*\n((?:\s*-\s*.*\n?)+)/m)
  if (!m) return []
  return m[1].split('\n')
    .map(l => l.trim())
    .filter(l => l.startsWith('-'))
    .map(l => l.replace(/^-\s*/, '').replace(/^["']|["']$/g, '').trim())
    .filter(Boolean)
}

async function ruleToSection(ruleItem) {
  const raw = await fs.readFile(ruleItem.sourcePath, 'utf-8')
  const fm = raw.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/)
  const frontmatter = fm ? fm[1] : ''
  let body = (fm ? raw.slice(fm[0].length) : raw).trim()
  // 去掉 body 开头的 H1 标题行（与下方生成的 ## 标题重复），不动其余内容
  body = body.replace(/^#\s+.*\n+/, '')

  const description = extractDescription(raw) || ruleItem.name
  const paths = parseRulePaths(frontmatter)
  const marker = `<!-- dwy-rule: ${ruleItem.name} -->`
  const title = `## [dwy] ${description}`
  const scopeLine = paths.length
    ? `*适用范围（Codex 无路径作用域，仅供模型参考）：${paths.map(p => '`' + p + '`').join('、')}*`
    : ''
  return [marker, title, scopeLine, body].filter(Boolean).join('\n\n')
}

export function parseManagedRuleNames(content) {
  const block = content.match(BLOCK_RE)
  if (!block) return new Set()
  const names = new Set()
  const re = /<!-- dwy-rule:\s*(.+?)\s*-->/g
  let m
  while ((m = re.exec(block[0]))) names.add(m[1])
  return names
}

export function parseManagedRuleSections(content) {
  const block = content.match(BLOCK_RE)
  if (!block) return new Map()

  const sections = new Map()
  const blockContent = block[0]
  const markerRe = /<!-- dwy-rule:\s*(.+?)\s*-->/g
  const markers = []
  let match
  while ((match = markerRe.exec(blockContent))) {
    markers.push({
      name: match[1],
      index: match.index,
    })
  }

  const blockEndIndex = blockContent.lastIndexOf(BLOCK_END)
  for (let i = 0; i < markers.length; i++) {
    const start = markers[i].index
    const end = i + 1 < markers.length ? markers[i + 1].index : blockEndIndex
    sections.set(markers[i].name, blockContent.slice(start, end).trim())
  }

  return sections
}

function upsertManagedBlock(content, blockBody) {
  if (!blockBody.trim()) {
    if (!BLOCK_RE.test(content)) return content
    const next = content.replace(BLOCK_RE, '').replace(/\n{3,}/g, '\n\n').trimEnd()
    return next ? next + '\n' : ''
  }
  const block = `${BLOCK_START}\n\n${blockBody}\n\n${BLOCK_END}`
  if (BLOCK_RE.test(content)) return content.replace(BLOCK_RE, block)
  const base = content.trimEnd()
  return base ? `${base}\n\n${block}\n` : `${block}\n`
}

function upsertBaselineBlock(content, baselineBody) {
  if (!baselineBody.trim()) {
    if (!BASELINE_RE.test(content)) return content
    const next = content.replace(BASELINE_RE, '').replace(/\n{3,}/g, '\n\n').trimEnd()
    return next ? `${next}\n` : ''
  }

  const block = `${BASELINE_START}\n\n${baselineBody.trim()}\n\n${BASELINE_END}`
  if (BASELINE_RE.test(content)) return content.replace(BASELINE_RE, block)

  const base = content.trimStart()
  return base ? `${block}\n\n${base}` : `${block}\n`
}

/** 判断文件是否含有有效的 dwy 通用规范；个人文件不作为继承依据。 */
export async function hasManagedBaseline(dest) {
  if (!await fs.pathExists(dest)) return false
  const match = (await fs.readFile(dest, 'utf8')).match(BASELINE_RE)
  return Boolean(match && match[0].replace(/<!--[\s\S]*?-->/g, '').trim())
}

/** 独立更新通用规范，空内容移除基线块；保留 Rules 和个人内容。 */
export async function syncBaselineDoc(baseline, dest) {
  const current = await fs.pathExists(dest) ? await fs.readFile(dest, 'utf-8') : ''
  const previous = baseline.trim() && current.trim() === baseline.trim() ? '' : current
  const next = upsertBaselineBlock(previous, baseline)
  if (next === current) return 0
  if (next.trim()) {
    await fs.ensureDir(path.dirname(dest))
    await fs.writeFile(dest, next)
  } else await fs.remove(dest)
  logAction(`baseline → ${dest}`)
  return 1
}

/** 兼容旧调用方；全局基线更新同样保留其他托管块。 */
export const syncGlobalBaselineDoc = syncBaselineDoc

/** 迁移旧入口中的基线；无托管标记时只移除与当前模板完全一致的文件。 */
export async function removeLegacyBaseline(baseline, dest) {
  if (!await fs.pathExists(dest)) return
  if (!baseline.trim()) return
  const current = await fs.readFile(dest, 'utf-8')
  const next = current.trim() === baseline.trim() ? '' : upsertBaselineBlock(current, '')
  if (next === current) return
  if (next.trim()) await fs.writeFile(dest, next)
  else await fs.remove(dest)
  logAction(`legacy baseline → ${dest}`, 'red', '×')
}

/** 三种 CLI 共用项目根 AGENTS.md；只写所选 Rules，保留托管块之外的项目内容。 */
export async function syncProjectAgentsMd(projectDir, selectedRules, {
  preservedRuleNames = new Set(),
} = {}) {
  const dest = path.join(projectDir, 'AGENTS.md')
  const current = await fs.pathExists(dest) ? await fs.readFile(dest, 'utf-8') : ''
  const selectedRuleNames = new Set(selectedRules.map(rule => rule.name))
  const existingSections = parseManagedRuleSections(current)
  const sections = []
  for (const rule of selectedRules) sections.push(await ruleToSection(rule))
  for (const ruleName of preservedRuleNames) {
    if (selectedRuleNames.has(ruleName)) continue
    const existingSection = existingSections.get(ruleName)
    if (existingSection) sections.push(existingSection)
  }
  const blockBody = sections.join('\n\n---\n\n')

  const next = upsertManagedBlock(current, blockBody)
  if (next === current) return 0
  await fs.ensureDir(path.dirname(dest))
  await fs.writeFile(dest, next)
  logAction(`AGENTS.md — ${blockBody.trim() ? `${selectedRules.length} rules` : 'rules removed'}`)
  return 1
}

export async function clearProjectAgentsMd(projectDir) {
  const dest = path.join(projectDir, 'AGENTS.md')
  if (!await fs.pathExists(dest)) return 0

  const current = await fs.readFile(dest, 'utf-8')
  const withoutBaseline = upsertBaselineBlock(current, '')
  const next = upsertManagedBlock(withoutBaseline, '')
  if (next === current) return 0

  if (!next.trim()) {
    await fs.remove(dest)
    logAction('AGENTS.md', 'red', '×')
    return 1
  }

  await fs.writeFile(dest, next)
  logAction('AGENTS.md — cleared', 'red', '×')
  return 1
}

// ---------- skills → .agents/skills/ ----------

export async function scanExistingCodexSkills(proj) {
  const dir = path.join(proj, '.agents', 'skills')
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir, { withFileTypes: true })
  return new Set(entries.filter(e => e.isDirectory() || e.isSymbolicLink()).map(e => e.name))
}

async function copySkillsFlat(skills, proj) {
  const root = path.join(proj, '.agents', 'skills')
  for (const s of skills) {
    const dest = path.join(root, s.name)
    await linkSkill({ skill: s, dest, backupRoot: path.join(proj, '.dwy', 'skill-backups') })
    logAction(`.agents/skills/${s.name}`)
  }
  return skills.length
}

async function removeUnselectedFlat(subdir, existingNames, selectedNames, templateNames, proj) {
  let count = 0
  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    // 项目独有(模板未提供过)的条目永不删除,保留用户自定义
    if (!templateNames.has(name)) continue
    const dest = path.join(proj, ...subdir, name)
    if (subdir[1] === 'skills') {
      await removeSkillEntry({ dest, backupRoot: path.join(proj, '.dwy', 'skill-backups') })
    } else {
      await fs.remove(dest)
    }
    logAction(`${subdir.join('/')}/${name}`, 'red', '×')
    count++
  }
  return count
}

// ---------- hooks → .codex/ ----------

export async function scanExistingCodexHooks(proj, configDir = path.join(proj, '.codex')) {
  const dir = path.join(configDir, 'hooks')
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir)
  return new Set(entries.filter(n => n !== '.gitkeep' && n !== '.DS_Store'))
}

async function copyCodexHooks(hooks, configDir) {
  if (hooks.length === 0) return 0
  const dir = path.join(configDir, 'hooks')
  await fs.ensureDir(dir)
  for (const h of hooks) {
    if (!await fs.pathExists(h.sourcePath)) {
      logAction(`.codex/hooks/${h.name}`, 'yellow', '!')
      continue
    }
    const dest = path.join(dir, h.name)
    await fs.copy(h.sourcePath, dest, { overwrite: true, filter: copyFilter(h.sourcePath) })
    if (!await fs.pathExists(dest)) {
      logAction(`.codex/hooks/${h.name}`, 'yellow', '!')
      continue
    }
    await fs.chmod(dest, 0o755)
    logAction(`.codex/hooks/${h.name}`)
  }
  return hooks.length
}

function globalHookCommand(configDir, name) {
  const script = path.join(configDir, 'hooks', name).replace(/\\/g, '/')
  return `bash '${script.replace(/'/g, "'\\''")}'`
}

/** 生成 Codex Hook 注册，继承检测和写入共用相同命令格式。 */
export function buildCodexHooksJson(manifests, selectedHookNames, global, configDir) {
  const hooksJson = { hooks: {} }
  const grouped = new Map()

  for (const manifest of manifests) {
    if (!selectedHookNames.has(manifest.name)) continue
    if (manifest.platforms && !manifest.platforms.includes('codex')) continue

    const event = manifest.event || 'PreToolUse'
    const matcher = manifest.matcher || 'Bash'
    const key = `${event}::${matcher}`
    const hooks = grouped.get(key) || []
    hooks.push({
      type: 'command',
      command: global
        ? globalHookCommand(configDir, manifest.name)
        : `bash "$(git rev-parse --show-toplevel)/.codex/hooks/${manifest.name}"`,
      ...(manifest.timeout ? { timeout: manifest.timeout } : {}),
    })
    grouped.set(key, hooks)
  }

  for (const [key, hooks] of grouped.entries()) {
    const [event, matcher] = key.split('::')
    hooksJson.hooks[event] ||= []
    hooksJson.hooks[event].push({ matcher, hooks })
  }

  return Object.keys(hooksJson.hooks).length > 0 ? hooksJson : {}
}

/** 只识别完整生成命令及已知历史格式，保留同名个人路径。 */
export function isManagedCodexHookCommand(command, managedHookNames, configDir) {
  if (typeof command !== 'string') return false
  return [...managedHookNames].some(name => [
    globalHookCommand(configDir, name),
    `bash "$(git rev-parse --show-toplevel)/.codex/hooks/${name}"`,
    `bash "$HOME/.codex/hooks/${name}"`,
    `bash ~/.codex/hooks/${name}`,
  ].includes(command))
}

/** 只替换指定托管注册，保留其他命令及配置字段。 */
export function mergeCodexHooks(existingHooks, generatedHooks, managedHookNames, configDir) {
  const merged = {}
  const sourceEvents = new Set([
    ...Object.keys(existingHooks || {}),
    ...Object.keys(generatedHooks || {}),
  ])

  for (const event of sourceEvents) {
    const kept = []

    for (const cfg of existingHooks?.[event] || []) {
      const remainingHooks = (cfg.hooks || []).filter(hook => !isManagedCodexHookCommand(hook.command, managedHookNames, configDir))
      if (remainingHooks.length > 0) kept.push({ ...cfg, hooks: remainingHooks })
    }

    for (const cfg of generatedHooks?.[event] || []) kept.push(cfg)
    if (kept.length > 0) merged[event] = kept
  }

  return Object.keys(merged).length > 0 ? merged : undefined
}

async function syncCodexHooksJson(sourceDir, configDir, selectedHookNames, global, staleHookNames) {
  const dest = path.join(configDir, 'hooks.json')
  const manifests = await loadHookManifests(sourceDir)
  const generated = buildCodexHooksJson(manifests, selectedHookNames, global, configDir)
  const managedHookNames = new Set(
    [...manifests.map(manifest => manifest.name), ...staleHookNames],
  )

  let nextJson
  if (await fs.pathExists(dest)) {
    const existing = await fs.readJson(dest)
    const nextHooks = mergeCodexHooks(existing.hooks, generated.hooks, managedHookNames, configDir)
    if (!nextHooks) {
      if (!existing.hooks) return 0
      const { hooks, ...rest } = existing
      if (Object.keys(rest).length === 0) {
        await fs.remove(dest)
        logAction('.codex/hooks.json — removed', 'red', '×')
        return 1
      }
      nextJson = rest
    } else {
      nextJson = { ...existing, hooks: nextHooks }
    }
  } else {
    if (!generated.hooks) return 0
    nextJson = generated
  }

  await fs.ensureDir(path.dirname(dest))
  await fs.writeJson(dest, nextJson, { spaces: 2 })
  logAction('.codex/hooks.json')
  return 1
}

/** 同步 Codex Skills 与 Hooks；全局 Hooks 遵循 codexHome。 */
export async function syncCodex({
  sourceDir: sourceDirOverride,
  projectDir,
  global = false,
  selected,
  homeDir,
  codexHome,
  sharedSkills,
  syncTypes = ['skills', 'hooks'],
  staleRemovals = {},
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const proj = projectDir || process.cwd()
  const configDir = global && codexHome ? codexHome : path.join(proj, '.codex')

  console.log(chalk.blue('\nScanning available config for Codex...\n'))

  const scans = {
    skills: await scanSkills(sourceDir),
    hooks: await scanHooks(sourceDir),
  }
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.hooks.length} hooks\n`))

  const existing = {
    skills: await scanExistingCodexSkills(proj),
    hooks: await scanExistingCodexHooks(proj, configDir),
  }
  const selectedNames = key => new Set((selected[key] || []).map(item => item.name))
  const syncedSelection = {
    skills: scans.skills.filter(item => selectedNames('skills').has(item.name)),
    hooks: scans.hooks.filter(item => selectedNames('hooks').has(item.name)),
  }
  const selectedHookNames = new Set(syncedSelection.hooks.map(h => h.name))

  console.log(chalk.blue(`\nSyncing to ${proj}...\n`))

  let syncedCount = 0
  let removedCount = 0

  if (syncTypes.includes('skills')) {
    const skills = sharedSkills
      ? sharedSkills.filter(skill => selectedNames('skills').has(skill.name))
      : await ensureSharedSkills({ skills: syncedSelection.skills, homeDir })
    syncedCount += await copySkillsFlat(skills, proj)
  }
  if (syncTypes.includes('hooks')) {
    syncedCount += await copyCodexHooks(syncedSelection.hooks, configDir)
    syncedCount += await syncCodexHooksJson(sourceDir, configDir, selectedHookNames, global, staleRemovals.hooks || [])
  }

  const skillTemplateNames = new Set([
    ...scans.skills.map(s => s.name),
    ...(staleRemovals.skills || new Set()),
  ])
  const hookTemplateNames = new Set([
    ...scans.hooks.map(h => h.name),
    ...(staleRemovals.hooks || new Set()),
  ])
  if (syncTypes.includes('skills')) removedCount += await removeUnselectedFlat(['.agents', 'skills'], existing.skills, new Set(syncedSelection.skills.map(s => s.name)), skillTemplateNames, proj)
  if (syncTypes.includes('hooks')) removedCount += await removeUnselectedFlat([path.relative(proj, configDir), 'hooks'], existing.hooks, selectedHookNames, hookTemplateNames, proj)

  console.log(chalk.blue(`\nDone! ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Skills → ${path.join(proj, '.agents', 'skills')}`))
  console.log(chalk.gray(`  Hooks  → ${configDir}`))
}
