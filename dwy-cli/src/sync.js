import fs from 'fs-extra'
import path from 'path'
import { isCancel } from '@clack/prompts'
import {
  SEARCH_PLACEHOLDER,
  searchableMultiselect,
  searchableSelect,
} from './searchable-select.js'
import { chalk, DEFAULT_TEMPLATE_REPO_URL, getDwyHomeDir, runGit } from './utils.js'

const CATEGORIES = [
  { key: 'skills', label: 'Skills' },
  { key: 'rules', label: 'Rules' },
  { key: 'commands', label: 'Commands' },
  { key: 'hooks', label: 'Hooks' },
]

const COPY_EXCLUDE_PATTERNS = [
  /(?:^|\/)\.venv(?:\/|$)/,
  /(?:^|\/)__pycache__(?:\/|$)/,
  /(?:^|\/)\.pytest_cache(?:\/|$)/,
  /(?:^|\/)\.ruff_cache(?:\/|$)/,
  /(?:^|\/)\.mypy_cache(?:\/|$)/,
  /(?:^|\/)node_modules(?:\/|$)/,
  /(?:^|\/)\.DS_Store$/,
  /\.pyc$/,
]

const TEMPLATE_SOURCE_CANDIDATES = [
  ['dwy-cli', 'templates', 'ai-tools'],
  ['claude-cli', 'templates', 'ai-tools'],
  ['templates', 'ai-tools'],
]

export function copyFilter(src) {
  return !COPY_EXCLUDE_PATTERNS.some(re => re.test(src))
}

export function extractDescription(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return ''
  const lines = match[1].split('\n')
  let i = 0
  while (i < lines.length) {
    const kv = lines[i].match(/^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$/)
    if (!kv) { i++; continue }
    if (kv[1] === 'description') {
      const trimmed = kv[2].trim()
      if (trimmed === '>' || trimmed === '|') {
        i++
        const parts = []
        while (i < lines.length && (lines[i].startsWith('  ') || lines[i].trim() === '')) {
          parts.push(lines[i].trim())
          i++
        }
        return parts.filter(Boolean).join(' ')
      }
      return trimmed.replace(/^["']|["']$/g, '')
    }
    i++
  }
  return ''
}

function extractTitleLine(content) {
  const headingMatch = content.match(/^#\s+(.+)$/m)
  if (headingMatch) return headingMatch[1].trim()

  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (trimmed.startsWith('# ')) return trimmed.slice(2).trim()
    if (trimmed.startsWith('//')) return trimmed.replace(/^\/\/\s*/, '').trim()
    if (trimmed.startsWith('#')) return trimmed.replace(/^#\s*/, '').trim()
    return trimmed
  }

  return ''
}

async function readEntryDescription(entryPath, fallback) {
  if (!await fs.pathExists(entryPath)) return fallback

  try {
    const stat = await fs.stat(entryPath)
    if (stat.isDirectory()) {
      const readmePath = path.join(entryPath, 'README.md')
      if (!await fs.pathExists(readmePath)) return fallback
      const readme = await fs.readFile(readmePath, 'utf-8')
      return extractDescription(readme) || extractTitleLine(readme) || fallback
    }

    const content = await fs.readFile(entryPath, 'utf-8')
    return extractDescription(content) || extractTitleLine(content) || fallback
  } catch {
    return fallback
  }
}

export async function scanSkills(sourceDir) {
  const skillsDir = path.join(sourceDir, 'skills')
  if (!await fs.pathExists(skillsDir)) return []

  const skills = []
  for (const cat of await fs.readdir(skillsDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(skillsDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue
      const skillPath = path.join(catDir, entry.name)
      const skillMd = path.join(skillPath, 'SKILL.md')
      if (!await fs.pathExists(skillMd)) continue
      const content = await fs.readFile(skillMd, 'utf-8')
      skills.push({
        name: entry.name,
        description: extractDescription(content) || '（无描述）',
        category: cat.name,
        sourcePath: skillPath,
        type: 'skill',
      })
    }
  }
  return skills.sort((a, b) => a.name.localeCompare(b.name))
}

export async function scanRules(sourceDir) {
  const rulesDir = path.join(sourceDir, 'rules')
  if (!await fs.pathExists(rulesDir)) return []

  const rules = []
  for (const cat of await fs.readdir(rulesDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(rulesDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (!entry.isFile() || !entry.name.endsWith('.md')) continue
      const rulePath = path.join(catDir, entry.name)
      const content = await fs.readFile(rulePath, 'utf-8')
      rules.push({
        name: entry.name,
        description: extractDescription(content) || '（无描述）',
        category: cat.name,
        sourcePath: rulePath,
        type: 'rule',
      })
    }
  }
  return rules.sort((a, b) => a.name.localeCompare(b.name))
}

export async function scanCommands(sourceDir) {
  const commandsDir = path.join(sourceDir, 'commands')
  if (!await fs.pathExists(commandsDir)) return []

  const entries = await fs.readdir(commandsDir, { withFileTypes: true })
  const commands = await Promise.all(entries
    .filter(e => e.name !== '.gitkeep' && e.name !== '.DS_Store')
    .map(async e => ({
      name: e.name,
      description: await readEntryDescription(
        path.join(commandsDir, e.name),
        e.isDirectory() ? '命令目录' : '命令文件',
      ),
      category: e.isDirectory() ? '目录命令' : '文件命令',
      sourcePath: path.join(commandsDir, e.name),
      type: 'command',
    })))

  return commands.sort((a, b) => a.name.localeCompare(b.name))
}

export async function scanHooks(sourceDir) {
  const hooksDir = path.join(sourceDir, 'hooks')
  if (!await fs.pathExists(hooksDir)) return []

  const hooks = []
  for (const cat of await fs.readdir(hooksDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(hooksDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (entry.name === '.gitkeep') continue
      const hookPath = path.join(catDir, entry.name)
      hooks.push({
        name: entry.name,
        description: await readEntryDescription(
          hookPath,
          entry.isDirectory() ? '钩子目录' : '钩子脚本',
        ),
        category: cat.name,
        sourcePath: hookPath,
        type: 'hook',
      })
    }
  }
  return hooks.sort((a, b) => a.name.localeCompare(b.name))
}

export async function loadHookManifests(sourceDir) {
  const manifestPath = path.join(sourceDir, 'hook-manifests', 'hooks.json')
  if (!await fs.pathExists(manifestPath)) return []
  return fs.readJson(manifestPath)
}

export async function readBaselineDoc(sourceDir) {
  const baselinePath = path.join(sourceDir, 'CLAUDE.md')
  if (!await fs.pathExists(baselinePath)) return ''
  return fs.readFile(baselinePath, 'utf-8')
}

export async function scanExisting(projectTargetDir, typePlural) {
  const dir = path.join(projectTargetDir, typePlural)
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir)
  return new Set(entries.filter(name => name !== '.gitkeep' && name !== '.DS_Store'))
}

/**
 * 将扫描项转为可搜索扁平 options。
 * label 带分类前缀便于筛选；完整 description 进底部公共说明区（不截断塞 hint）。
 *
 * @param {Array<{ name: string, category?: string, description?: string }>} items
 * @returns {Array<{ value: string, label: string, description?: string }>}
 */
function buildSearchableOptions(items) {
  return items
    .slice()
    .sort((a, b) => {
      const catCmp = (a.category || '其他').localeCompare(b.category || '其他', 'zh')
      if (catCmp !== 0) return catCmp
      return a.name.localeCompare(b.name, 'zh')
    })
    .map(item => {
      const category = item.category || '其他'
      return {
        value: item.name,
        label: `${category} / ${item.name}`,
        // 完整描述给底部公共区；搜索也匹配 description
        description: item.description || undefined,
      }
    })
}

/**
 * 可搜索多选一层。items 为空直接返回 []，不弹窗。
 * 取消返回 null，调用方必须中止整次同步。
 *
 * @param {Array<{ name: string, category?: string, description?: string }>} items
 * @param {string} label
 * @param {Iterable<string>} defaultNames
 */
export async function promptSelection(items, label, defaultNames) {
  if (items.length === 0) return []
  // 可搜索多选 + 底部说明区（聚焦项描述不跟在行尾）
  const selectedNames = await searchableMultiselect({
    message: `选择 ${label}`,
    options: buildSearchableOptions(items),
    initialValues: [...defaultNames],
    maxItems: 15,
    required: false,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(selectedNames)) return null
  const selectedSet = new Set(selectedNames)
  return items.filter(item => selectedSet.has(item.name))
}

/**
 * 交互式选择：每步可回退到上一步，最后总览支持任意类别重选。
 * categories 可缩成仅 Skills，未出现的类别返回空数组（调用方不得据此删除已有项）。
 * 返回 { skills, rules, commands, hooks } 或 null（取消）。
 *
 * @param {object} scans
 * @param {object} existing
 * @param {{ categories?: Array<{ key: string, label: string }> }} [opts]
 */
export async function interactiveSelect(scans, existing, { categories = CATEGORIES } = {}) {
  const sel = {
    skills: [],
    rules: [],
    commands: [],
    hooks: [],
  }

  // 第一轮：顺序遍历，每步给导航
  let i = 0
  while (i < categories.length) {
    const { key, label } = categories[i]
    const defaultNames = sel[key]?.length
      ? new Set(sel[key].map(x => x.name))
      : existing[key]
    sel[key] = await promptSelection(scans[key], label, defaultNames)
    if (sel[key] === null) return null

    if (i === categories.length - 1) break

    const nextLabel = categories[i + 1].label
    const prevLabel = i > 0 ? categories[i - 1].label : null
    // 导航步可搜索单选（选项少，交互与多选一致）
    const nav = await searchableSelect({
      message: `${label} 已选 ${sel[key].length} 项。下一步：`,
      options: [
        { label: `继续选 ${nextLabel}`, value: 'next' },
        ...(prevLabel ? [{ label: `返回重选 ${prevLabel}`, value: 'back' }] : []),
        { label: '取消同步', value: 'cancel' },
      ],
      initialValue: 'next',
      placeholder: SEARCH_PLACEHOLDER,
    })
    if (isCancel(nav) || nav === 'cancel') return null
    i = nav === 'back' ? i - 1 : i + 1
  }

  // 第二轮：总览 + 任意重选
  while (true) {
    console.log(chalk.gray('\n选择汇总：'))
    for (const { key, label } of categories) {
      console.log(chalk.gray(`  ${label.padEnd(10)} ${sel[key].length} 项`))
    }
    const final = await searchableSelect({
      message: '确认提交还是重选？',
      options: [
        { label: '确认提交', value: 'confirm' },
        ...categories.map(c => ({ label: `重选 ${c.label}`, value: c.key })),
        { label: '取消同步', value: 'cancel' },
      ],
      initialValue: 'confirm',
      placeholder: SEARCH_PLACEHOLDER,
    })
    if (isCancel(final) || final === 'cancel') return null
    if (final === 'confirm') return sel
    const cat = categories.find(c => c.key === final)
    sel[final] = await promptSelection(scans[final], cat.label, new Set(sel[final].map(x => x.name)))
    if (sel[final] === null) return null
  }
}

export function logAction(label, color = 'green', prefix = '✓') {
  console.log(chalk[color](`  ${prefix} ${label}`))
}

function getTemplateRepoCacheDir() {
  return path.join(getDwyHomeDir(), 'cache', 'dwy')
}

async function resolveTemplateDirFromRepo(repoDir) {
  for (const segments of TEMPLATE_SOURCE_CANDIDATES) {
    const candidate = path.join(repoDir, ...segments)
    if (await fs.pathExists(candidate)) return candidate
  }

  throw new Error(`ai-tools templates not found in repo: ${repoDir}`)
}

async function readGitOriginUrl(repoDir) {
  try {
    return await runGit(['-C', repoDir, 'remote', 'get-url', 'origin'])
  } catch {
    return ''
  }
}

async function ensureTemplateRepoCache() {
  const repoDir = getTemplateRepoCacheDir()
  const repoRoot = path.dirname(repoDir)
  await fs.ensureDir(repoRoot)

  const hasGitDir = await fs.pathExists(path.join(repoDir, '.git'))
  if (hasGitDir) {
    const originUrl = await readGitOriginUrl(repoDir)
    if (!originUrl || originUrl !== DEFAULT_TEMPLATE_REPO_URL) {
      console.log(chalk.gray('缓存模板仓库 origin 已变更，重建缓存...'))
      await fs.remove(repoDir)
    }
  } else if (await fs.pathExists(repoDir)) {
    console.log(chalk.gray('缓存目录不是 git 仓库，重建缓存...'))
    await fs.remove(repoDir)
  }

  if (!await fs.pathExists(path.join(repoDir, '.git'))) {
    console.log(chalk.gray('拉取模板仓库...'))
    await runGit(['clone', DEFAULT_TEMPLATE_REPO_URL, repoDir])
    return repoDir
  }

  console.log(chalk.gray('更新模板仓库...'))
  await runGit(['-C', repoDir, 'pull', '--ff-only'])
  return repoDir
}

async function copyItems(items, targetDir) {
  for (const item of items) {
    const dest = path.join(targetDir, item.type + 's', item.name)
    await fs.ensureDir(path.dirname(dest))
    await fs.copy(item.sourcePath, dest, { overwrite: true, filter: copyFilter })
    logAction(`${item.type}s/${item.name}`)
  }
  return items.length
}

async function copyHooks(items, targetDir) {
  if (items.length === 0) return 0
  const hooksTargetDir = path.join(targetDir, 'hooks')
  await fs.ensureDir(hooksTargetDir)
  for (const hook of items) {
    if (!await fs.pathExists(hook.sourcePath)) {
      logAction(`hooks/${hook.name}`, 'yellow', '!')
      continue
    }
    const dest = path.join(hooksTargetDir, hook.name)
    await fs.copy(hook.sourcePath, dest, { overwrite: true, filter: copyFilter })
    if (!await fs.pathExists(dest)) {
      logAction(`hooks/${hook.name}`, 'yellow', '!')
      continue
    }
    await fs.chmod(dest, 0o755)
    logAction(`hooks/${hook.name}`)
  }
  return items.length
}

async function removeUnselected(typePlural, existingNames, selectedNames, templateNames, targetDir) {
  let count = 0
  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    // 项目独有(模板未提供过)的条目永不删除,保留用户自定义
    if (!templateNames.has(name)) continue
    const target = path.join(targetDir, typePlural, name)
    await fs.remove(target)
    logAction(`${typePlural}/${name}`, 'red', '×')
    count++
  }
  return count
}

function buildClaudeHooksSettings(manifests, selectedHookNames) {
  const grouped = new Map()

  for (const manifest of manifests) {
    if (!selectedHookNames.has(manifest.name)) continue
    if (manifest.platforms && !manifest.platforms.includes('claude')) continue

    const event = manifest.event || 'PreToolUse'
    const matcher = manifest.matcher || 'Bash'
    const key = `${event}::${matcher}`
    const hooks = grouped.get(key) || []
    hooks.push({
      type: 'command',
      command: `bash $CLAUDE_PROJECT_DIR/.claude/hooks/${manifest.name}`,
    })
    grouped.set(key, hooks)
  }

  if (grouped.size === 0) return {}

  const settings = { hooks: {} }
  for (const [key, hooks] of grouped.entries()) {
    const [event, matcher] = key.split('::')
    settings.hooks[event] ||= []
    settings.hooks[event].push({ matcher, hooks })
  }

  return settings
}

function isManagedClaudeHookCommand(command, managedHookNames) {
  if (typeof command !== 'string') return false
  const match = command.match(/\.claude\/hooks\/([^\s'"]+)/)
  return !!(match && managedHookNames.has(match[1]))
}

function mergeClaudeHooks(existingHooks, generatedHooks, managedHookNames) {
  const merged = {}
  const sourceEvents = new Set([
    ...Object.keys(existingHooks || {}),
    ...Object.keys(generatedHooks || {}),
  ])

  for (const event of sourceEvents) {
    const kept = []

    for (const cfg of existingHooks?.[event] || []) {
      const remainingHooks = (cfg.hooks || []).filter(hook => !isManagedClaudeHookCommand(hook.command, managedHookNames))
      if (remainingHooks.length > 0) kept.push({ ...cfg, hooks: remainingHooks })
    }

    for (const cfg of generatedHooks?.[event] || []) kept.push(cfg)
    if (kept.length > 0) merged[event] = kept
  }

  return Object.keys(merged).length > 0 ? merged : undefined
}

async function syncSettings(sourceDir, targetDir, selectedHookNames) {
  const settingsDest = path.join(targetDir, 'settings.json')
  const manifests = await loadHookManifests(sourceDir)
  const generatedSettings = buildClaudeHooksSettings(manifests, selectedHookNames)
  const managedHookNames = new Set(
    manifests
      .filter(manifest => !manifest.platforms || manifest.platforms.includes('claude'))
      .map(manifest => manifest.name),
  )

  let merged
  let action
  if (await fs.pathExists(settingsDest)) {
    const existing = await fs.readJson(settingsDest)
    merged = { ...existing }
    for (const [key, value] of Object.entries(generatedSettings)) {
      if (key === 'hooks') continue
      if (key in merged && typeof merged[key] === 'object' && !Array.isArray(merged[key])
          && typeof value === 'object' && !Array.isArray(value)) {
        merged[key] = { ...merged[key], ...value }
      } else {
        merged[key] = value
      }
    }
    const nextHooks = mergeClaudeHooks(existing.hooks, generatedSettings.hooks, managedHookNames)
    if (nextHooks) merged.hooks = nextHooks
    else delete merged.hooks
    action = 'merged'
  } else {
    merged = generatedSettings
    action = 'created'
  }

  await fs.writeJson(settingsDest, merged, { spaces: 2 })
  logAction(`settings.json — ${action}`)
  return 1
}

async function syncClaudeBaselineDoc(sourceDir, targetDir) {
  const baseline = await readBaselineDoc(sourceDir)
  if (!baseline) return 0

  const dest = path.join(targetDir, 'CLAUDE.md')
  const current = await fs.pathExists(dest) ? await fs.readFile(dest, 'utf-8') : ''
  if (current === baseline) return 0

  await fs.writeFile(dest, baseline)
  logAction('.claude/CLAUDE.md')
  return 1
}

export async function resolveSourceDir() {
  const explicitSourceDir = process.env.DWY_TEMPLATE_SOURCE_DIR
  if (explicitSourceDir) {
    if (!await fs.pathExists(explicitSourceDir)) {
      throw new Error(`DWY_TEMPLATE_SOURCE_DIR not found: ${explicitSourceDir}`)
    }
    return explicitSourceDir
  }

  const repoDir = await ensureTemplateRepoCache()
  return resolveTemplateDirFromRepo(repoDir)
}

export async function syncClaude({
  sourceDir: sourceDirOverride,
  projectDir,
  selected,
  staleRemovals = {},
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  console.log(chalk.blue('\nScanning available Claude configuration...\n'))
  const projectRoot = projectDir || process.cwd()
  const projectTargetDir = path.join(projectRoot, '.claude')

  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: await scanCommands(sourceDir),
    hooks: await scanHooks(sourceDir),
  }
  const availableHooks = []
  for (const hook of scans.hooks) {
    if (await fs.pathExists(hook.sourcePath)) {
      availableHooks.push(hook)
    }
  }
  if (availableHooks.length < scans.hooks.length) {
    const missing = scans.hooks
      .filter(h => !availableHooks.includes(h))
      .map(h => h.name)
      .join('、')
    logAction(`hooks skipped: ${missing}`, 'yellow', '!')
  }
  scans.hooks = availableHooks
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.rules.length} rules, ${scans.commands.length} commands, ${scans.hooks.length} hooks\n`))

  const existing = {
    skills: await scanExisting(projectTargetDir, 'skills'),
    rules: await scanExisting(projectTargetDir, 'rules'),
    commands: await scanExisting(projectTargetDir, 'commands'),
    hooks: await scanExisting(projectTargetDir, 'hooks'),
  }

  const selectedNames = key => new Set((selected[key] || []).map(item => item.name))
  const syncedSelection = {
    skills: scans.skills.filter(item => selectedNames('skills').has(item.name)),
    rules: scans.rules.filter(item => selectedNames('rules').has(item.name)),
    commands: scans.commands.filter(item => selectedNames('commands').has(item.name)),
    hooks: scans.hooks.filter(item => selectedNames('hooks').has(item.name)),
  }

  const selectedHookNames = new Set(syncedSelection.hooks.map(h => h.name))
  const approvedStaleSkills = staleRemovals.skills || new Set()
  const approvedStaleRules = staleRemovals.rules || new Set()
  const approvedStaleCommands = staleRemovals.commands || new Set()
  const approvedStaleHooks = staleRemovals.hooks || new Set()

  console.log(chalk.blue(`\nSyncing to ${projectTargetDir}...\n`))
  await fs.ensureDir(projectTargetDir)

  let syncedCount = 0
  let removedCount = 0

  syncedCount += await syncClaudeBaselineDoc(sourceDir, projectTargetDir)
  syncedCount += await copyItems(syncedSelection.skills, projectTargetDir)
  syncedCount += await copyItems(syncedSelection.rules, projectTargetDir)
  syncedCount += await copyItems(syncedSelection.commands, projectTargetDir)
  syncedCount += await syncSettings(sourceDir, projectTargetDir, selectedHookNames)
  syncedCount += await copyHooks(syncedSelection.hooks, projectTargetDir)

  const skillTemplateNames = new Set([...scans.skills.map(s => s.name), ...approvedStaleSkills])
  const ruleTemplateNames = new Set([...scans.rules.map(r => r.name), ...approvedStaleRules])
  const commandTemplateNames = new Set([...scans.commands.map(c => c.name), ...approvedStaleCommands])
  const hookTemplateNames = new Set([...scans.hooks.map(h => h.name), ...approvedStaleHooks])
  removedCount += await removeUnselected('skills', existing.skills, new Set(syncedSelection.skills.map(s => s.name)), skillTemplateNames, projectTargetDir)
  removedCount += await removeUnselected('rules', existing.rules, new Set(syncedSelection.rules.map(r => r.name)), ruleTemplateNames, projectTargetDir)
  removedCount += await removeUnselected('commands', existing.commands, new Set(syncedSelection.commands.map(c => c.name)), commandTemplateNames, projectTargetDir)
  removedCount += await removeUnselected('hooks', existing.hooks, selectedHookNames, hookTemplateNames, projectTargetDir)

  console.log(chalk.blue(`\nDone! ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Project config → ${projectTargetDir}`))
  console.log(chalk.gray(`  Hooks          → ${path.join(projectTargetDir, 'hooks')}`))
}
