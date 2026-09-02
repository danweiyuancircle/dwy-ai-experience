import fs from 'fs-extra'
import path from 'path'
import { confirm, isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import {
  DEFAULT_SKILL_DESTINATIONS,
  copySkillsToGlobalDirs,
  copySkillsToProjectPlatforms,
  listSkillDestOptions,
  normalizeSkillScope,
  resolveProjectSkillDir,
} from './sync-global-skills.js'
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
import { ensureSkillsInstalled, installSkills } from './skills-install.js'
import { selfUpgrade } from './self-upgrade.js'
import { normalizePacks } from './sync-packs.js'
import { interactiveSelectByPacks } from './sync-scene.js'

const PLATFORM_OPTIONS = [
  { value: 'claude', label: 'Claude Code', description: '支持 rules / skills / commands / hooks' },
  { value: 'codex', label: 'Codex', description: '支持 rules / skills / hooks' },
  { value: 'cursor', label: 'Cursor', description: '支持 rules' },
  { value: 'opencode', label: 'OpenCode', description: '支持 rules / skills / commands' },
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

/** 完整同步：skills / rules / commands / hooks 都走平台写入 */
export const SYNC_MODE_ALL = 'all'
/** 仅 Skills：不写、不删 rules / commands / hooks */
export const SYNC_MODE_SKILLS = 'skills'
export const DEFAULT_SYNC_MODE = SYNC_MODE_ALL

/** 按条目勾选 Skills / Rules / Hooks */
export const SELECTION_STYLE_ITEMS = 'items'
/** 按技术栈包 + 场景包勾选 */
export const SELECTION_STYLE_PACKS = 'packs'
export const DEFAULT_SELECTION_STYLE = SELECTION_STYLE_PACKS

/** 同步项目配置（skills / rules / hooks） */
export const ACTION_SYNC = 'sync'
/** 强制刷新 ~/.dwy/skills 外部 skill */
export const ACTION_INSTALL_SKILLS = 'install-skills'
/** 把全局 create-dwy 升到 npm latest */
export const ACTION_UPGRADE = 'upgrade'

const SKILL_ONLY_CATEGORIES = [{ key: 'skills', label: 'Skills' }]

/**
 * 规范化同步范围。未知值回退完整同步，避免误进仅 Skills 删不该删的东西。
 *
 * @param {unknown} raw
 * @returns {'all' | 'skills'}
 */
export function normalizeSyncMode(raw) {
  return raw === SYNC_MODE_SKILLS ? SYNC_MODE_SKILLS : DEFAULT_SYNC_MODE
}

/**
 * 规范化勾选方式。未知值回退按包，避免新用户落到 80+ 条逐项勾选。
 *
 * @param {unknown} raw
 * @returns {'items' | 'packs'}
 */
export function normalizeSelectionStyle(raw) {
  return raw === SELECTION_STYLE_ITEMS ? SELECTION_STYLE_ITEMS : DEFAULT_SELECTION_STYLE
}

/**
 * 规范化入口动作。未知值回退同步，避免误进强制重装。
 *
 * @param {unknown} raw
 * @returns {'sync' | 'install-skills' | 'upgrade'}
 */
export function normalizeAction(raw) {
  if (raw === ACTION_INSTALL_SKILLS) return ACTION_INSTALL_SKILLS
  if (raw === ACTION_UPGRADE) return ACTION_UPGRADE
  return ACTION_SYNC
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

/**
 * dwy 入口第一问：同步全局 skills，或同步项目配置。
 * 自升级只走 `dwy upgrade`，不出现在这张菜单。
 *
 * @returns {Promise<'sync' | 'install-skills' | null>}
 */
async function promptAction() {
  const result = await searchableSelect({
    message: '选择要做的事',
    options: [
      {
        value: ACTION_INSTALL_SKILLS,
        label: '同步全局 skills',
        description: '强制重装 ~/.dwy/skills（pm-skills / superpowers）',
      },
      {
        value: ACTION_SYNC,
        label: '同步项目配置',
        description: '按场景和技术栈，或一条条勾选，写入当前项目',
      },
    ],
    initialValue: ACTION_SYNC,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(result)) return null
  return normalizeAction(result)
}

/**
 * 开头选同步范围。仅 Skills 时后面不再问 rules / commands / hooks。
 *
 * @param {'all' | 'skills'} initialValue
 * @returns {Promise<'all' | 'skills' | null>}
 */
async function promptSyncMode(initialValue) {
  const result = await searchableSelect({
    message: '选择同步范围',
    options: [
      {
        value: SYNC_MODE_ALL,
        label: '完整同步',
        description: '同步 Skills / Rules / Commands / Hooks',
      },
      {
        value: SYNC_MODE_SKILLS,
        label: '仅 Skills',
        description: '只处理 skill，不改动已有 Rules / Commands / Hooks',
      },
    ],
    initialValue,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(result)) return null
  return normalizeSyncMode(result)
}

/**
 * 选勾选方式。按包是默认推荐；按条目保留原来的逐项勾选。
 *
 * @param {'items' | 'packs'} initialValue
 * @returns {Promise<'items' | 'packs' | null>}
 */
async function promptSelectionStyle(initialValue) {
  const result = await searchableSelect({
    message: '项目配置怎么勾',
    options: [
      {
        value: SELECTION_STYLE_PACKS,
        label: '按场景和技术栈（推荐）',
        description: '先选栈和场景包，再展示已勾子条目，可取消',
      },
      {
        value: SELECTION_STYLE_ITEMS,
        label: '一个一个选',
        description: '一条条勾选 Skills / Rules / Hooks',
      },
    ],
    initialValue,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(result)) return null
  return normalizeSelectionStyle(result)
}

/**
 * 仅 Skills 模式：只写项目/全局 skill，并清理未选中的模板 skill。
 * 禁止调用完整平台 sync，否则空 rules/commands 会删掉项目已有项。
 *
 * @param {{ projectDir: string, selectedPlatforms: string[], skills: Array<{ name: string, sourcePath: string }>, templateSkillNames: Set<string>, staleSkillNames: Set<string>, skillScope: { destinations: string[] } }} opts
 */
async function syncSkillsOnly({
  projectDir,
  selectedPlatforms,
  skills,
  templateSkillNames,
  staleSkillNames,
  skillScope,
}) {
  const writeProject = skillScope.destinations.includes('project')
  if (!writeProject) return

  const skillPlatforms = selectedPlatforms.filter(platform => resolveProjectSkillDir(projectDir, platform))
  if (skillPlatforms.length === 0) {
    console.log(chalk.yellow('已选平台不支持项目内 skills，跳过项目写入。'))
    return
  }

  console.log(chalk.blue('\nSyncing skills only (rules / commands / hooks untouched)...\n'))
  await copySkillsToProjectPlatforms({
    projectDir,
    platforms: skillPlatforms,
    skills,
  })

  const selectedNames = new Set(skills.map(item => item.name))
  const toRemove = new Set(
    [...templateSkillNames, ...staleSkillNames].filter(name => !selectedNames.has(name)),
  )
  for (const platform of skillPlatforms) {
    const destRoot = resolveProjectSkillDir(projectDir, platform)
    const existingNames = await scanExisting(path.dirname(destRoot), 'skills')
    await removeManagedItems(
      destRoot,
      existingNames,
      toRemove,
      path.relative(projectDir, destRoot),
    )
  }
}

/**
 * 交互最后一步：选 skill 同步位置，默认仅项目。
 * 勾了全局 dest 后再问哪些 skill 额外拷到全局；不删用户 home 里其它 skill。
 *
 * @param {{ selectedSkills: Array<{ name: string }>, syncState: { skillScope?: object } }} args
 * @returns {Promise<{ destinations: string[], globalSkills: string[] } | null>}
 */
async function promptSkillScope({ selectedSkills, syncState }) {
  const previous = normalizeSkillScope(syncState.skillScope)
  const destInitial = previous.destinations.length > 0
    ? previous.destinations
    : [...DEFAULT_SKILL_DESTINATIONS]

  console.log(chalk.gray('\nSkill 默认同步到项目目录。勾选全局目录可把部分 skill 额外拷到本机 home。'))

  const destResult = await searchableMultiselect({
    message: '选择 skill 同步位置（默认项目）',
    options: listSkillDestOptions(),
    initialValues: destInitial,
    required: true,
    maxItems: 8,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(destResult)) return null

  const destinations = destResult
  const globalDests = destinations.filter(id => id !== 'project')
  if (globalDests.length === 0 || selectedSkills.length === 0) {
    return { destinations, globalSkills: [] }
  }

  const selectedNames = selectedSkills.map(item => item.name)
  const globalInitial = previous.globalSkills.filter(name => selectedNames.includes(name))
  const globalResult = await searchableMultiselect({
    message: '哪些 skill 额外同步到全局？',
    options: selectedSkills.map(item => ({
      value: item.name,
      label: item.name,
      description: item.description,
    })),
    initialValues: globalInitial,
    required: false,
    placeholder: SEARCH_PLACEHOLDER,
  })
  if (isCancel(globalResult)) return null

  return {
    destinations,
    globalSkills: globalResult,
  }
}

async function selectPlatforms(projectDir) {
  const initialValues = await buildPlatformDefaultsFromLocalState(projectDir)

  console.log(chalk.gray('\n平台能力预览：'))
  console.log(chalk.gray('  Claude Code → rules / skills / commands / hooks'))
  console.log(chalk.gray('  Codex       → rules / skills / hooks'))
  console.log(chalk.gray('  Cursor      → rules'))
  console.log(chalk.gray('  OpenCode    → rules / skills / commands\n'))

  // 可搜索多选 + 底部说明区
  const result = await searchableMultiselect({
    message: '选择要同步的平台',
    options: PLATFORM_OPTIONS,
    initialValues,
    required: true,
    maxItems: 6,
    placeholder: SEARCH_PLACEHOLDER,
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
      skillScope: normalizeSkillScope(undefined),
      syncMode: DEFAULT_SYNC_MODE,
      selectionStyle: DEFAULT_SELECTION_STYLE,
      packs: normalizePacks(undefined),
    }
  }

  const state = await fs.readJson(statePath)
  return {
    version: 1,
    platforms: state.platforms || {},
    skillScope: normalizeSkillScope(state.skillScope),
    syncMode: normalizeSyncMode(state.syncMode),
    selectionStyle: normalizeSelectionStyle(state.selectionStyle),
    packs: normalizePacks(state.packs),
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

      const selected = await searchableMultiselect({
        message: `选择要删除的 ${PLATFORM_LABELS[platform]} ${TYPE_LABELS[type]}`,
        options: names.map(name => ({ value: name, label: name })),
        initialValues: names,
        required: false,
        placeholder: SEARCH_PLACEHOLDER,
      })
      if (isCancel(selected)) return null
      approvals[platform][type] = new Set(selected)
    }
  }

  return approvals
}

/**
 * 仅 Skills 模式：陈旧项提示只保留 skills，避免问 rules/commands/hooks。
 *
 * @param {Record<string, Record<string, string[]>>} staleEntries
 */
function retainSkillStaleEntries(staleEntries) {
  const next = createEmptyRemovalState()
  for (const [platform, types] of Object.entries(staleEntries)) {
    if (types.skills?.length) next[platform] = { skills: types.skills }
  }
  return next
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

/**
 * `dwy` / `dwy sync` 入口。先选动作再分支：同步全局 skills / 同步项目配置。
 * 自升级只走 `dwy upgrade`。测试注入 selected / action 时跳过动作菜单。
 *
 * @param {object} [opts]
 */
export async function runDwy(opts = {}) {
  const skipMenu = !!(opts.selected || opts.selectedPlatforms || opts.action)
  const action = opts.action != null
    ? normalizeAction(opts.action)
    : (skipMenu ? ACTION_SYNC : await promptAction())
  if (action === null) {
    console.log(chalk.yellow('\n已取消。'))
    return
  }
  if (action === ACTION_INSTALL_SKILLS) {
    await installSkills()
    return
  }
  if (action === ACTION_UPGRADE) {
    try {
      await selfUpgrade()
    } catch (error) {
      console.error(error.message)
      process.exitCode = 1
    }
    return
  }
  await syncAll(opts)
}

export async function syncAll({
  sourceDir: sourceDirOverride,
  projectDir: projectDirOverride,
  selected: selectedOverride,
  selectedPlatforms: selectedPlatformsOverride,
  staleRemovals: staleRemovalsOverride,
  // 测试/脚本可注入；交互模式在平台选择之后再问
  skillScope: skillScopeOverride,
  // all = 完整同步；skills = 只写 skill，测试/脚本可注入
  syncMode: syncModeOverride,
  // 全局 skill 写入的 home，测试注入假目录，禁止默认写真实 $HOME
  homeDir,
  // 测试注入勾选方式；交互模式在同步范围之后再问
  selectionStyle: selectionStyleOverride,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const projectDir = projectDirOverride || process.cwd()

  // 开头无条件自检全局外部 skill：未装 / 清单变更（cli 加了 skill 或改了 tag）则自动更新，
  // 已装且清单一致则零开销跳过。失败不阻塞 sync（离线/网络故障，下次再来）。
  // 这样用户跑一次同步就把 skill 更新到位；强制重装走入口「刷新全局外部 skill」。
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

  const skipInteractive = !!(selectedOverride || selectedPlatformsOverride)
  const syncMode = syncModeOverride
    ? normalizeSyncMode(syncModeOverride)
    : (skipInteractive
      ? normalizeSyncMode(syncState.syncMode)
      : await promptSyncMode(normalizeSyncMode(syncState.syncMode)))
  if (syncMode === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const selectionStyle = selectionStyleOverride
    ? normalizeSelectionStyle(selectionStyleOverride)
    : (skipInteractive
      ? normalizeSelectionStyle(syncState.selectionStyle)
      : await promptSelectionStyle(normalizeSelectionStyle(syncState.selectionStyle)))
  if (selectionStyle === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const selected = selectedOverride || (
    selectionStyle === SELECTION_STYLE_PACKS
      ? await interactiveSelectByPacks(scans, syncState, { skillsOnly: syncMode === SYNC_MODE_SKILLS })
      : await interactiveSelect(scans, selectionDefaults, {
        categories: syncMode === SYNC_MODE_SKILLS ? SKILL_ONLY_CATEGORIES : undefined,
      })
  )
  if (selected === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const selectedPlatforms = selectedPlatformsOverride || await selectPlatforms(projectDir)
  if (selectedPlatforms === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const staleEntriesRaw = await collectStaleEntries(projectDir, scans, syncState, selectedPlatforms)
  const staleEntries = syncMode === SYNC_MODE_SKILLS
    ? retainSkillStaleEntries(staleEntriesRaw)
    : staleEntriesRaw
  const approvedStaleRemovals = staleRemovalsOverride
    ? normalizeRemovalInput(staleRemovalsOverride)
    : await promptStaleRemovals(staleEntries)
  if (approvedStaleRemovals === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const skillScope = skillScopeOverride
    ? normalizeSkillScope(skillScopeOverride)
    : (selectedOverride
      ? normalizeSkillScope(syncState.skillScope)
      : await promptSkillScope({ selectedSkills: selected.skills || [], syncState }))
  if (skillScope === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const selectedSkillNames = new Set((selected.skills || []).map(item => item.name))
  const skillsToWrite = scans.skills.filter(item => selectedSkillNames.has(item.name))
  let syncedAnySupportedPlatform = false

  if (syncMode === SYNC_MODE_SKILLS) {
    const staleSkillNames = new Set()
    for (const platform of selectedPlatforms) {
      for (const name of approvedStaleRemovals[platform]?.skills || []) staleSkillNames.add(name)
    }
    await syncSkillsOnly({
      projectDir,
      selectedPlatforms,
      skills: skillsToWrite,
      templateSkillNames: new Set(scans.skills.map(item => item.name)),
      staleSkillNames,
      skillScope,
    })
    syncedAnySupportedPlatform = selectedPlatforms.some(platform => resolveProjectSkillDir(projectDir, platform))
      || skillScope.destinations.some(id => id !== 'project')
  } else {
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
  }

  const globalSkillNameSet = new Set(skillScope.globalSkills)
  const globalSkills = scans.skills.filter(item => globalSkillNameSet.has(item.name))
  if (globalSkills.length > 0 && skillScope.destinations.some(id => id !== 'project')) {
    console.log(chalk.blue('\nSyncing selected skills to global directories...\n'))
    await copySkillsToGlobalDirs({
      skills: globalSkills,
      destIds: skillScope.destinations,
      homeDir,
    })
  }

  if (syncMode === SYNC_MODE_SKILLS) {
    for (const platform of selectedPlatforms) {
      const previous = syncState.platforms[platform] || createEmptyPlatformState()
      const skillsOnlySelected = { skills: selected.skills || [], rules: [], commands: [], hooks: [] }
      syncState.platforms[platform] = {
        ...previous,
        skills: buildNextPlatformState(skillsOnlySelected, staleEntries, approvedStaleRemovals, platform).skills,
      }
    }
  } else {
    for (const platform of Object.keys(PLATFORM_SYNC_TYPES)) {
      if (selectedPlatforms.includes(platform)) {
        syncState.platforms[platform] = buildNextPlatformState(selected, staleEntries, approvedStaleRemovals, platform)
      } else {
        syncState.platforms[platform] = createEmptyPlatformState()
      }
    }
  }
  syncState.skillScope = skillScope
  syncState.syncMode = syncMode
  syncState.selectionStyle = selectionStyle
  // 按条目同步不覆盖上次按包选择，方便下次再走按包
  if (selectionStyle === SELECTION_STYLE_PACKS) {
    syncState.packs = normalizePacks(selected.packs)
  }
  await saveSyncState(projectDir, syncState)

  if (!syncedAnySupportedPlatform) {
    console.log(chalk.yellow('未选择已接入平台，本次未执行同步。'))
  }
}
