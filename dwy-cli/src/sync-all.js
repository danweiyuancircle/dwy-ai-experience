import fs from 'fs-extra'
import path from 'path'
import { confirm, isCancel, multiselect } from '@clack/prompts'
import { chalk } from './utils.js'
import {
  interactiveSelect,
  loadHookManifests,
  logAction,
  readBaselineDoc,
  resolveSourceDir,
  scanCommands,
  scanExisting,
  scanHooks,
  scanRules,
  scanSkills,
  syncClaude,
} from './sync.js'
import {
  clearProjectAgentsMd,
  parseManagedRuleNames,
  scanExistingCodexHooks,
  scanExistingCodexSkills,
  syncCodex,
} from './sync-codex.js'
import { scanExistingCursorRules, syncCursor } from './sync-cursor.js'
import { syncOpenCode } from './sync-opencode.js'
import { ensureSkillsInstalled } from './skills-install.js'

const PLATFORM_OPTIONS = [
  { value: 'claude', label: 'Claude Code', hint: '支持 rules / skills / commands / hooks' },
  { value: 'codex', label: 'Codex', hint: '支持 rules / skills / hooks' },
  { value: 'cursor', label: 'Cursor', hint: '支持 rules' },
  { value: 'opencode', label: 'OpenCode', hint: '支持 rules / skills / commands' },
]

const CURSOR_BASELINE_RULE_NAME = '00-dwy-global.mdc'
const SYNC_STATE_PATH = ['.dwy', 'sync-state.json']
const PLATFORM_SYNC_TYPES = {
  claude: ['skills', 'rules', 'commands', 'hooks'],
  codex: ['skills', 'rules', 'hooks'],
  cursor: ['rules'],
  opencode: ['skills', 'rules', 'commands'],
}
const PLATFORM_LABELS = {
  claude: 'Claude Code',
  codex: 'Codex',
  cursor: 'Cursor',
  opencode: 'OpenCode',
}
const TYPE_LABELS = {
  skills: 'skills',
  rules: 'rules',
  commands: 'commands',
  hooks: 'hooks',
}

function unionSets(...sets) {
  return new Set(sets.flatMap(set => [...set]))
}

function hasSetItems(setsByType) {
  return setsByType.skills.size + setsByType.rules.size + setsByType.commands.size + setsByType.hooks.size > 0
}

export function buildSelectionDefaultsFromSyncState(existing, syncState) {
  const stateDefaults = {
    skills: new Set(),
    rules: new Set(),
    commands: new Set(),
    hooks: new Set(),
  }

  for (const platformState of Object.values(syncState?.platforms || {})) {
    for (const type of ['skills', 'rules', 'commands', 'hooks']) {
      for (const name of platformState?.[type] || []) {
        stateDefaults[type].add(name)
      }
    }
  }

  return hasSetItems(stateDefaults) ? stateDefaults : existing
}

async function scanCombinedExisting(projectDir) {
  const claudeDir = path.join(projectDir, '.claude')
  const agentsMdPath = path.join(projectDir, 'AGENTS.md')
  const agentsMdContent = await fs.pathExists(agentsMdPath) ? await fs.readFile(agentsMdPath, 'utf-8') : ''

  return {
    skills: unionSets(
      await scanExisting(claudeDir, 'skills'),
      await scanExistingCodexSkills(projectDir),
    ),
    rules: unionSets(
      await scanExisting(claudeDir, 'rules'),
      parseManagedRuleNames(agentsMdContent),
    ),
    commands: await scanExisting(claudeDir, 'commands'),
    hooks: unionSets(
      await scanExisting(claudeDir, 'hooks'),
      await scanExistingCodexHooks(projectDir),
    ),
  }
}

async function shouldInitialize(projectDir, existing) {
  const hasAnyExisting = hasSetItems(existing)
  if (hasAnyExisting) return true

  const hasConfigDir = await fs.pathExists(path.join(projectDir, '.claude'))
    || await fs.pathExists(path.join(projectDir, '.codex'))
    || await fs.pathExists(path.join(projectDir, '.agents'))

  if (hasConfigDir) return true

  const ok = await confirm({
    message: `当前目录 ${chalk.yellow(projectDir)} 尚无 Claude Code/Codex 配置，是否在此初始化？`,
    initialValue: false,
  })
  return !isCancel(ok) && ok
}

export async function buildPlatformDefaultsFromLocalState(projectDir) {
  const defaults = []

  if (await fs.pathExists(path.join(projectDir, '.claude'))) {
    defaults.push('claude')
  }
  if (
    await fs.pathExists(path.join(projectDir, '.codex'))
    || await fs.pathExists(path.join(projectDir, '.agents'))
    || await fs.pathExists(path.join(projectDir, 'AGENTS.md'))
  ) {
    defaults.push('codex')
  }
  if (await fs.pathExists(path.join(projectDir, '.cursor'))) {
    defaults.push('cursor')
  }
  if (await fs.pathExists(path.join(projectDir, '.opencode'))) {
    defaults.push('opencode')
  }

  return defaults.length > 0 ? defaults : ['claude', 'codex']
}

async function selectPlatforms(projectDir) {
  const initialValues = await buildPlatformDefaultsFromLocalState(projectDir)

  console.log(chalk.gray('\n平台能力预览：'))
  console.log(chalk.gray('  Claude Code → rules / skills / commands / hooks'))
  console.log(chalk.gray('  Codex       → rules / skills / hooks'))
  console.log(chalk.gray('  Cursor      → rules'))
  console.log(chalk.gray('  OpenCode    → rules / skills / commands\n'))

  const result = await multiselect({
    message: '选择要同步的平台',
    options: PLATFORM_OPTIONS,
    initialValues,
    required: true,
    maxItems: 6,
  })
  if (isCancel(result)) return null
  return result
}

function buildCursorRuleName(ruleName) {
  return `dwy-${ruleName.replace(/\.md$/i, '')}.mdc`
}

function buildCursorBaselineContent(baseline) {
  return [
    '---',
    `description: ${JSON.stringify('[dwy] Global baseline')}`,
    'alwaysApply: true',
    '---',
    '',
    baseline.trim(),
    '',
  ].join('\n')
}

function createEmptyPlatformState() {
  return {
    skills: [],
    rules: [],
    commands: [],
    hooks: [],
  }
}

async function loadSyncState(projectDir) {
  const statePath = path.join(projectDir, ...SYNC_STATE_PATH)
  if (!await fs.pathExists(statePath)) {
    return {
      version: 1,
      platforms: {},
    }
  }

  const state = await fs.readJson(statePath)
  return {
    version: 1,
    platforms: state.platforms || {},
  }
}

async function saveSyncState(projectDir, state) {
  const statePath = path.join(projectDir, ...SYNC_STATE_PATH)
  await fs.ensureDir(path.dirname(statePath))
  await fs.writeJson(statePath, state, { spaces: 2 })
}

function getCurrentTemplateNames(scans) {
  return {
    skills: new Set(scans.skills.map(item => item.name)),
    rules: new Set(scans.rules.map(item => item.name)),
    commands: new Set(scans.commands.map(item => item.name)),
    hooks: new Set(scans.hooks.map(item => item.name)),
  }
}

async function collectCurrentManagedNames(projectDir) {
  const claudeDir = path.join(projectDir, '.claude')
  const openCodeDir = path.join(projectDir, '.opencode')
  const agentsMdPath = path.join(projectDir, 'AGENTS.md')
  const agentsMdContent = await fs.pathExists(agentsMdPath) ? await fs.readFile(agentsMdPath, 'utf-8') : ''

  return {
    claude: {
      skills: await scanExisting(claudeDir, 'skills'),
      rules: await scanExisting(claudeDir, 'rules'),
      commands: await scanExisting(claudeDir, 'commands'),
      hooks: await scanExisting(claudeDir, 'hooks'),
    },
    codex: {
      skills: await scanExistingCodexSkills(projectDir),
      rules: parseManagedRuleNames(agentsMdContent),
      hooks: await scanExistingCodexHooks(projectDir),
    },
    cursor: {
      rules: await scanExistingCursorRules(projectDir),
    },
    opencode: {
      skills: await scanExisting(openCodeDir, 'skills'),
      rules: parseManagedRuleNames(agentsMdContent),
      commands: await scanExisting(openCodeDir, 'commands'),
    },
  }
}

function normalizeRemovalInput(removals = {}) {
  const normalized = {}
  for (const [platform, types] of Object.entries(removals)) {
    normalized[platform] = {}
    for (const [type, names] of Object.entries(types || {})) {
      normalized[platform][type] = new Set(Array.isArray(names) ? names : [...names])
    }
  }
  return normalized
}

function createEmptyRemovalState() {
  return Object.fromEntries(
    Object.keys(PLATFORM_SYNC_TYPES).map(platform => [platform, {}]),
  )
}

async function collectStaleEntries(projectDir, scans, syncState, selectedPlatforms) {
  const currentTemplateNames = getCurrentTemplateNames(scans)
  const currentManaged = await collectCurrentManagedNames(projectDir)
  const staleEntries = createEmptyRemovalState()

  for (const platform of selectedPlatforms) {
    const previous = syncState.platforms?.[platform] || {}
    const platformManaged = currentManaged[platform] || {}

    for (const type of PLATFORM_SYNC_TYPES[platform] || []) {
      const previousNames = previous[type] || []
      const currentNames = currentTemplateNames[type] || new Set()
      const managedNames = platformManaged[type] || new Set()
      const staleNames = []

      for (const name of previousNames) {
        if (currentNames.has(name)) continue
        if (type === 'rules' && platform === 'cursor') {
          if (!managedNames.has(buildCursorRuleName(name))) continue
        } else if (!managedNames.has(name)) {
          continue
        }
        staleNames.push(name)
      }

      if (staleNames.length > 0) staleEntries[platform][type] = staleNames.sort((a, b) => a.localeCompare(b, 'zh'))
    }
  }

  return staleEntries
}

async function promptStaleRemovals(staleEntries) {
  const approvals = createEmptyRemovalState()

  for (const platform of Object.keys(PLATFORM_SYNC_TYPES)) {
    for (const type of PLATFORM_SYNC_TYPES[platform]) {
      const names = staleEntries[platform]?.[type] || []
      if (names.length === 0) continue

      console.log(chalk.yellow(`\n检测到 ${PLATFORM_LABELS[platform]} 已同步但模板仓库已移除的 ${TYPE_LABELS[type]}：`))
      for (const name of names) {
        console.log(chalk.gray(`  - ${name}`))
      }

      const selected = await multiselect({
        message: `选择要删除的 ${PLATFORM_LABELS[platform]} ${TYPE_LABELS[type]}`,
        options: names.map(name => ({ value: name, label: name })),
        initialValues: names,
        required: false,
      })
      if (isCancel(selected)) return null
      approvals[platform][type] = new Set(selected)
    }
  }

  return approvals
}

function getPreservedStaleNames(staleEntries, approvedRemovals, platform, type) {
  const staleNames = staleEntries[platform]?.[type] || []
  const approvedNames = approvedRemovals[platform]?.[type] || new Set()
  return new Set(staleNames.filter(name => !approvedNames.has(name)))
}

function buildNextPlatformState(selected, staleEntries, approvedRemovals, platform) {
  const state = createEmptyPlatformState()

  for (const type of PLATFORM_SYNC_TYPES[platform] || []) {
    const selectedNames = new Set((selected[type] || []).map(item => item.name))
    for (const name of staleEntries[platform]?.[type] || []) {
      const approvedNames = approvedRemovals[platform]?.[type] || new Set()
      if (!approvedNames.has(name)) selectedNames.add(name)
    }
    state[type] = [...selectedNames].sort((a, b) => a.localeCompare(b, 'zh'))
  }

  return state
}

async function removeManagedItems(targetDir, existingNames, managedNames, labelPrefix) {
  let removedCount = 0

  for (const name of existingNames) {
    if (!managedNames.has(name)) continue
    await fs.remove(path.join(targetDir, name))
    logAction(`${labelPrefix}/${name}`, 'red', '×')
    removedCount++
  }

  return removedCount
}

async function removeManagedFileIfExact(filePath, managedContent, label) {
  if (!managedContent || !await fs.pathExists(filePath)) return 0
  const current = await fs.readFile(filePath, 'utf-8')
  if (current !== managedContent) return 0
  await fs.remove(filePath)
  logAction(label, 'red', '×')
  return 1
}

function isManagedClaudeHookCommand(command, managedHookNames) {
  if (typeof command !== 'string') return false
  const match = command.match(/\.claude\/hooks\/([^\s'"]+)/)
  return !!(match && managedHookNames.has(match[1]))
}

function isManagedCodexHookCommand(command, managedHookNames) {
  if (typeof command !== 'string') return false
  const match = command.match(/\.codex\/hooks\/([^\s'"]+)/)
  return !!(match && managedHookNames.has(match[1]))
}

function pruneManagedClaudeHooks(existingHooks, managedHookNames) {
  const merged = {}

  for (const [event, configs] of Object.entries(existingHooks || {})) {
    const kept = []
    for (const cfg of configs || []) {
      if (isManagedClaudeHookCommand(cfg.command, managedHookNames)) continue
      kept.push(cfg)
    }
    if (kept.length > 0) merged[event] = kept
  }

  return Object.keys(merged).length > 0 ? merged : undefined
}

function pruneManagedCodexHooks(existingHooks, managedHookNames) {
  const merged = {}

  for (const [event, configs] of Object.entries(existingHooks || {})) {
    const keptConfigs = []
    for (const cfg of configs || []) {
      const keptHooks = (cfg.hooks || []).filter(hook => !isManagedCodexHookCommand(hook.command, managedHookNames))
      if (keptHooks.length > 0) keptConfigs.push({ ...cfg, hooks: keptHooks })
    }
    if (keptConfigs.length > 0) merged[event] = keptConfigs
  }

  return Object.keys(merged).length > 0 ? merged : undefined
}

async function cleanupClaudeSettings(projectDir, managedHookNames) {
  const settingsPath = path.join(projectDir, '.claude', 'settings.json')
  if (!await fs.pathExists(settingsPath)) return 0

  const existing = await fs.readJson(settingsPath)
  if (!existing.hooks) return 0

  const nextHooks = pruneManagedClaudeHooks(existing.hooks, managedHookNames)
  if (!nextHooks) {
    const { hooks, ...rest } = existing
    if (Object.keys(rest).length === Object.keys(existing).length) return 0
    if (Object.keys(rest).length === 0) {
      await fs.remove(settingsPath)
      logAction('.claude/settings.json — removed', 'red', '×')
      return 1
    }
    await fs.writeJson(settingsPath, rest, { spaces: 2 })
    logAction('.claude/settings.json — cleaned', 'red', '×')
    return 1
  }

  const next = { ...existing, hooks: nextHooks }
  if (JSON.stringify(next) === JSON.stringify(existing)) return 0
  await fs.writeJson(settingsPath, next, { spaces: 2 })
  logAction('.claude/settings.json — cleaned', 'red', '×')
  return 1
}

async function cleanupCodexHooksJson(projectDir, managedHookNames) {
  const hooksPath = path.join(projectDir, '.codex', 'hooks.json')
  if (!await fs.pathExists(hooksPath)) return 0

  const existing = await fs.readJson(hooksPath)
  if (!existing.hooks) return 0

  const nextHooks = pruneManagedCodexHooks(existing.hooks, managedHookNames)
  if (!nextHooks) {
    const { hooks, ...rest } = existing
    if (Object.keys(rest).length === Object.keys(existing).length) return 0
    if (Object.keys(rest).length === 0) {
      await fs.remove(hooksPath)
      logAction('.codex/hooks.json — removed', 'red', '×')
      return 1
    }
    await fs.writeJson(hooksPath, rest, { spaces: 2 })
    logAction('.codex/hooks.json — cleaned', 'red', '×')
    return 1
  }

  const next = { ...existing, hooks: nextHooks }
  if (JSON.stringify(next) === JSON.stringify(existing)) return 0
  await fs.writeJson(hooksPath, next, { spaces: 2 })
  logAction('.codex/hooks.json — cleaned', 'red', '×')
  return 1
}

async function cleanupClaudePlatform(projectDir, scans, managedHookNames, baseline) {
  const claudeDir = path.join(projectDir, '.claude')
  const existing = {
    skills: await scanExisting(claudeDir, 'skills'),
    rules: await scanExisting(claudeDir, 'rules'),
    commands: await scanExisting(claudeDir, 'commands'),
    hooks: await scanExisting(claudeDir, 'hooks'),
  }

  let removedCount = 0
  removedCount += await removeManagedItems(path.join(claudeDir, 'skills'), existing.skills, new Set(scans.skills.map(item => item.name)), '.claude/skills')
  removedCount += await removeManagedItems(path.join(claudeDir, 'rules'), existing.rules, new Set(scans.rules.map(item => item.name)), '.claude/rules')
  removedCount += await removeManagedItems(path.join(claudeDir, 'commands'), existing.commands, new Set(scans.commands.map(item => item.name)), '.claude/commands')
  removedCount += await removeManagedItems(path.join(claudeDir, 'hooks'), existing.hooks, new Set(scans.hooks.map(item => item.name)), '.claude/hooks')
  removedCount += await cleanupClaudeSettings(projectDir, managedHookNames)
  removedCount += await removeManagedFileIfExact(
    path.join(claudeDir, 'CLAUDE.md'),
    baseline,
    '.claude/CLAUDE.md',
  )
  return removedCount
}

async function cleanupCursorPlatform(projectDir, scans, baseline) {
  const rulesDir = path.join(projectDir, '.cursor', 'rules')
  if (!await fs.pathExists(rulesDir)) return 0

  const entries = await fs.readdir(rulesDir, { withFileTypes: true })
  const existingManagedNames = new Set(
    entries
      .filter(entry => entry.isFile())
      .map(entry => entry.name)
      .filter(name => name === CURSOR_BASELINE_RULE_NAME || scans.rules.some(rule => buildCursorRuleName(rule.name) === name)),
  )

  let removedCount = 0
  for (const name of existingManagedNames) {
    if (name === CURSOR_BASELINE_RULE_NAME) continue
    await fs.remove(path.join(rulesDir, name))
    logAction(`.cursor/rules/${name}`, 'red', '×')
    removedCount++
  }
  removedCount += await removeManagedFileIfExact(
    path.join(rulesDir, CURSOR_BASELINE_RULE_NAME),
    baseline ? buildCursorBaselineContent(baseline) : '',
    `.cursor/rules/${CURSOR_BASELINE_RULE_NAME}`,
  )
  return removedCount
}

async function cleanupCodexPlatform(projectDir, scans, managedHookNames) {
  let removedCount = 0
  removedCount += await removeManagedItems(
    path.join(projectDir, '.agents', 'skills'),
    await scanExistingCodexSkills(projectDir),
    new Set(scans.skills.map(item => item.name)),
    '.agents/skills',
  )
  removedCount += await removeManagedItems(
    path.join(projectDir, '.codex', 'hooks'),
    await scanExistingCodexHooks(projectDir),
    new Set(scans.hooks.map(item => item.name)),
    '.codex/hooks',
  )
  removedCount += await cleanupCodexHooksJson(projectDir, managedHookNames)
  return removedCount
}

async function cleanupOpenCodePlatform(projectDir, scans) {
  const openCodeDir = path.join(projectDir, '.opencode')
  const existing = {
    skills: await scanExisting(openCodeDir, 'skills'),
    commands: await scanExisting(openCodeDir, 'commands'),
  }

  let removedCount = 0
  removedCount += await removeManagedItems(path.join(openCodeDir, 'skills'), existing.skills, new Set(scans.skills.map(item => item.name)), '.opencode/skills')
  removedCount += await removeManagedItems(path.join(openCodeDir, 'commands'), existing.commands, new Set(scans.commands.map(item => item.name)), '.opencode/commands')
  return removedCount
}

export async function syncAll({
  sourceDir: sourceDirOverride,
  projectDir: projectDirOverride,
  selected: selectedOverride,
  selectedPlatforms: selectedPlatformsOverride,
  staleRemovals: staleRemovalsOverride,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const projectDir = projectDirOverride || process.cwd()

  // 开头无条件自检全局外部 skill：未装 / 清单变更（cli 加了 skill 或改了 tag）则自动更新，
  // 已装且清单一致则零开销跳过。失败不阻塞 sync（离线/网络故障，下次再来）。
  // 这样用户跑一次 `dwy` 就把 skill 更新到位，无需另记 `dwy skills install`。
  console.log(chalk.gray('检查全局外部 skill 更新...'))
  await ensureSkillsInstalled()

  console.log(chalk.blue('\nScanning available Claude Code/Codex configuration...\n'))
  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: await scanCommands(sourceDir),
    hooks: await scanHooks(sourceDir),
  }
  const baseline = await readBaselineDoc(sourceDir)
  const hookManifests = await loadHookManifests(sourceDir)
  const claudeManagedHookNames = new Set(
    hookManifests
      .filter(manifest => !manifest.platforms || manifest.platforms.includes('claude'))
      .map(manifest => manifest.name),
  )
  const codexManagedHookNames = new Set(
    hookManifests
      .filter(manifest => !manifest.platforms || manifest.platforms.includes('codex'))
      .map(manifest => manifest.name),
  )
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.rules.length} rules, ${scans.commands.length} commands, ${scans.hooks.length} hooks\n`))

  const existing = await scanCombinedExisting(projectDir)
  const syncState = await loadSyncState(projectDir)
  const selectionDefaults = buildSelectionDefaultsFromSyncState(existing, syncState)
  const skipInitPrompt = !!(selectedOverride || selectedPlatformsOverride)
  if (!skipInitPrompt && !await shouldInitialize(projectDir, existing)) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const hasAnyExisting = hasSetItems(existing)
  if (!hasAnyExisting && !selectedOverride) {
    console.log(chalk.gray('首次同步，进入交互式选择...\n'))
  }

  const selected = selectedOverride || await interactiveSelect(scans, selectionDefaults)
  if (selected === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const selectedPlatforms = selectedPlatformsOverride || await selectPlatforms(projectDir)
  if (selectedPlatforms === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const staleEntries = await collectStaleEntries(projectDir, scans, syncState, selectedPlatforms)
  const approvedStaleRemovals = staleRemovalsOverride
    ? normalizeRemovalInput(staleRemovalsOverride)
    : await promptStaleRemovals(staleEntries)
  if (approvedStaleRemovals === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  let syncedAnySupportedPlatform = false

  if (selectedPlatforms.includes('claude')) {
    syncedAnySupportedPlatform = true
    console.log(chalk.blue('\nSyncing Claude Code configuration...\n'))
    await syncClaude({
      sourceDir,
      projectDir,
      selected,
      staleRemovals: approvedStaleRemovals.claude,
    })
  }

  if (selectedPlatforms.includes('codex')) {
    syncedAnySupportedPlatform = true
    console.log(chalk.blue('\nSyncing Codex configuration...\n'))
    await syncCodex({
      sourceDir,
      projectDir,
      selected,
      staleRemovals: approvedStaleRemovals.codex,
      preserveMissingRules: getPreservedStaleNames(staleEntries, approvedStaleRemovals, 'codex', 'rules'),
    })
  }

  if (selectedPlatforms.includes('cursor')) {
    syncedAnySupportedPlatform = true
    await syncCursor({
      sourceDir,
      projectDir,
      selected,
      staleRemovals: approvedStaleRemovals.cursor,
    })
  }

  if (selectedPlatforms.includes('opencode')) {
    syncedAnySupportedPlatform = true
    await syncOpenCode({
      sourceDir,
      projectDir,
      selected,
      staleRemovals: approvedStaleRemovals.opencode,
      preserveMissingRules: getPreservedStaleNames(staleEntries, approvedStaleRemovals, 'opencode', 'rules'),
    })
  }

  if (!selectedPlatforms.includes('codex') && !selectedPlatforms.includes('opencode')) {
    await clearProjectAgentsMd(projectDir)
  }

  if (!selectedPlatforms.includes('claude')) {
    await cleanupClaudePlatform(projectDir, scans, claudeManagedHookNames, baseline)
  }

  if (!selectedPlatforms.includes('cursor')) {
    await cleanupCursorPlatform(projectDir, scans, baseline)
  }

  if (!selectedPlatforms.includes('codex')) {
    await cleanupCodexPlatform(projectDir, scans, codexManagedHookNames)
  }

  if (!selectedPlatforms.includes('opencode')) {
    await cleanupOpenCodePlatform(projectDir, scans)
  }

  for (const platform of Object.keys(PLATFORM_SYNC_TYPES)) {
    if (selectedPlatforms.includes(platform)) {
      syncState.platforms[platform] = buildNextPlatformState(selected, staleEntries, approvedStaleRemovals, platform)
    } else {
      syncState.platforms[platform] = createEmptyPlatformState()
    }
  }
  await saveSyncState(projectDir, syncState)

  if (!syncedAnySupportedPlatform) {
    console.log(chalk.yellow('未选择已接入平台，本次未执行同步。'))
  }
}
