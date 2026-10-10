import fs from 'fs-extra'
import path from 'path'
import os from 'node:os'
import { confirm, isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import {
  copySkillsToGlobalDirs,
  copySkillsToProjectPlatforms,
  normalizeSkillScope,
  resolveProjectSkillDir,
} from './sync-global-skills.js'
import { chalk } from './utils.js'
import {
  interactiveSelect,
  logAction,
  resolveSourceDir,
  scanExisting,
  scanHooks,
  scanRules,
  scanSkills,
  syncClaude,
} from './sync.js'
import {
  parseManagedRuleNames,
  scanExistingCodexHooks,
  scanExistingCodexSkills,
  syncCodex,
} from './sync-codex.js'
import { scanExistingCursorRules, syncCursor } from './sync-cursor.js'
import { syncOpenCode } from './sync-opencode.js'
import { ensureSkillsInstalled, installSkills } from './skills-install.js'
import { selfUpgrade } from './self-upgrade.js'

const PLATFORM_OPTIONS = [
  { value: 'claude', label: 'Claude Code', description: '支持 rules / skills / hooks' },
  { value: 'codex', label: 'Codex', description: '支持 rules / skills / hooks' },
  { value: 'cursor', label: 'Cursor', description: '支持 rules' },
  { value: 'opencode', label: 'OpenCode', description: '支持 rules / skills' },
]

const SYNC_STATE_PATH = ['.dwy', 'sync-state.json']
const PLATFORM_SYNC_TYPES = {
  claude: ['skills', 'rules', 'hooks'],
  codex: ['skills', 'rules', 'hooks'],
  cursor: ['rules'],
  opencode: ['skills', 'rules'],
}
const PLATFORM_LABELS = {
  claude: 'Claude Code',
  codex: 'Codex',
  cursor: 'Cursor',
  opencode: 'OpenCode',
}
/** 完整同步：逐项选择 skills / rules，hooks 自动启用。 */
export const SYNC_MODE_ALL = 'all'
/** 仅 Skills：不写、不删 rules / commands / hooks */
export const SYNC_MODE_SKILLS = 'skills'
export const DEFAULT_SYNC_MODE = SYNC_MODE_ALL

/** 同步项目配置（skills / rules / hooks） */
export const ACTION_SYNC = 'sync'
/** 强制刷新 ~/.dwy/skills 外部 skill */
export const ACTION_INSTALL_SKILLS = 'install-skills'
/** 把全局 create-dwy 升到 npm latest */
export const ACTION_UPGRADE = 'upgrade'

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
  return Object.values(setsByType).some(items => items.size > 0)
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
    hooks: unionSets(
      await scanExisting(claudeDir, 'hooks'),
      await scanExistingCodexHooks(projectDir),
    ),
  }
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
 * 仅 Skills 模式：只写项目/全局 skill，并清理未选中的模板 skill。
 * 禁止调用完整平台 sync，否则空 rules/hooks 会删掉项目已有项。
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

async function selectPlatforms(projectDir, global) {
  const initialValues = await buildPlatformDefaultsFromLocalState(projectDir)

  if (global) console.log(chalk.gray('Cursor 全局规则通过应用设置管理，本次不提供文件同步。'))
  // 可搜索多选 + 底部说明区
  const result = await searchableMultiselect({
    message: '选择要同步的平台',
    options: PLATFORM_OPTIONS.filter(option => !global || option.value !== 'cursor'),
    initialValues: initialValues.filter(value => !global || value !== 'cursor'),
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
    }
  }

  const state = await fs.readJson(statePath)
  return {
    version: 1,
    platforms: state.platforms || {},
    skillScope: normalizeSkillScope(state.skillScope),
    syncMode: normalizeSyncMode(state.syncMode),
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

async function collectCurrentManagedNames(projectDir, global = false) {
  const claudeDir = path.join(projectDir, '.claude')
  const openCodeDir = global ? path.join(projectDir, '.config', 'opencode') : path.join(projectDir, '.opencode')
  const agentsMdPath = global ? path.join(projectDir, '.codex', 'AGENTS.md') : path.join(projectDir, 'AGENTS.md')
  const agentsMdContent = await fs.pathExists(agentsMdPath) ? await fs.readFile(agentsMdPath, 'utf-8') : ''

  return {
    claude: {
      skills: await scanExisting(claudeDir, 'skills'),
      rules: await scanExisting(claudeDir, 'rules'),
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
      rules: global ? parseManagedRuleNames(await fs.pathExists(path.join(openCodeDir, 'AGENTS.md')) ? await fs.readFile(path.join(openCodeDir, 'AGENTS.md'), 'utf-8') : '') : parseManagedRuleNames(agentsMdContent),
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

async function collectStaleEntries(projectDir, scans, syncState, selectedPlatforms, global = false) {
  const currentTemplateNames = getCurrentTemplateNames(scans)
  const currentManaged = await collectCurrentManagedNames(projectDir, global)
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

/**
 * `dwy` / `dwy sync` 直接进入内容选择，再选位置和平台。
 * action 仅供已有脚本调用；主交互不再显示动作菜单。
 *
 * @param {object} [opts]
 */
export async function runDwy(opts = {}) {
  console.log(chalk.bold.cyan('\ndwy') + chalk.gray(' · AI 开发工具\n'))
  const action = normalizeAction(opts.action)
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
  // 兼容已有脚本；主交互只选择整套配置的位置。
  skillScope: skillScopeOverride,
  // all = 完整同步；skills = 只写 skill，测试/脚本可注入
  syncMode: syncModeOverride,
  // 全局配置根目录；测试必须注入临时用户目录。
  homeDir = os.homedir(),
  scope: scopeOverride,
  confirmed,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const projectDir = projectDirOverride || process.cwd()

  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: [],
    hooks: await scanHooks(sourceDir),
  }
  const existing = await scanCombinedExisting(projectDir)
  const syncState = await loadSyncState(projectDir)
  const globalState = await loadSyncState(homeDir)
  const projectDefaults = buildSelectionDefaultsFromSyncState(existing, syncState)
  const globalDefaults = buildSelectionDefaultsFromSyncState({ skills: new Set(), rules: new Set(), hooks: new Set() }, globalState)
  const selectionDefaults = Object.fromEntries(['skills', 'rules', 'hooks'].map(type => [type, unionSets(projectDefaults[type], globalDefaults[type])]))
  const syncMode = normalizeSyncMode(syncModeOverride)
  const selected = selectedOverride || await interactiveSelect(scans, selectionDefaults, {
    skillsOnly: syncMode === SYNC_MODE_SKILLS,
  })
  if (selected === null) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  if (syncMode === SYNC_MODE_ALL) selected.hooks = scans.hooks

  const scopeResult = scopeOverride || (selectedOverride || selectedPlatformsOverride ? 'project' : await searchableSelect({
    message: '选择同步位置',
    options: [
      { value: 'project', label: '当前项目', description: '仅当前项目生效' },
      { value: 'global', label: '全局', description: '所有项目生效' },
    ],
    initialValue: 'project',
  }))
  if (isCancel(scopeResult)) { console.log(chalk.yellow('已取消同步。')); return }
  if (!['project', 'global'].includes(scopeResult)) throw new Error('无效同步位置')
  const global = scopeResult === 'global'
  const targetRoot = global ? homeDir : projectDir
  const targetState = global ? await loadSyncState(homeDir) : syncState
  const selectedPlatforms = selectedPlatformsOverride || await selectPlatforms(targetRoot, global)
  if (selectedPlatforms === null) { console.log(chalk.yellow('已取消同步。')); return }
  if (selectedPlatforms.some(platform => !PLATFORM_SYNC_TYPES[platform] || (global && platform === 'cursor'))) {
    throw new Error('所选平台不支持此同步位置')
  }
  const staleEntriesRaw = await collectStaleEntries(targetRoot, scans, targetState, selectedPlatforms, global)
  const staleEntries = syncMode === SYNC_MODE_SKILLS ? retainSkillStaleEntries(staleEntriesRaw) : staleEntriesRaw
  const approvedStaleRemovals = normalizeRemovalInput(staleRemovalsOverride || staleEntries)
  const skillScope = normalizeSkillScope(skillScopeOverride)
  if ((!selectedOverride && confirmed !== true) || confirmed === false) {
    const currentManaged = await collectCurrentManagedNames(targetRoot, global)
    const templateNames = getCurrentTemplateNames(scans)
    console.log(`\nSkills：${selected.skills.map(item => item.name).join('、') || '未选择'}`)
    console.log(`Rules：${selected.rules.map(item => item.name).join('、') || '未选择'}`)
    console.log(`位置：${global ? '全局' : '当前项目'}；平台：${selectedPlatforms.map(platform => PLATFORM_LABELS[platform]).join('、')}`)
    console.log('Hooks 按支持的平台自动启用。')
    for (const platform of selectedPlatforms) {
      for (const type of PLATFORM_SYNC_TYPES[platform]) {
        const existingNames = currentManaged[platform]?.[type] || new Set()
        const previous = [...new Set([...templateNames[type], ...(targetState.platforms[platform]?.[type] || [])])]
          .filter(name => existingNames.has(platform === 'cursor' && type === 'rules' ? buildCursorRuleName(name) : name))
        const names = new Set((selected[type] || []).map(item => item.name))
        const removed = previous.filter(name => !names.has(name))
        const changed = [...names].filter(name => existingNames.has(platform === 'cursor' && type === 'rules' ? buildCursorRuleName(name) : name))
        if (changed.length) console.log(`更新 ${PLATFORM_LABELS[platform]} ${type}：${changed.join('、')}`)
        if (removed.length) console.log(`删除 ${PLATFORM_LABELS[platform]} ${type}：${removed.join('、')}`)
      }
    }
    const answer = confirmed === false ? false : await confirm({ message: '确认同步？' })
    if (isCancel(answer) || !answer) { console.log(chalk.yellow('已取消同步。')); return }
  }
  if (!selectedOverride && selected.skills.some(item => item.category === '产品0到1')) await ensureSkillsInstalled()

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
        projectDir: targetRoot,
        global,
        selected,
        staleRemovals: approvedStaleRemovals.claude,
      })
    }

    if (selectedPlatforms.includes('codex')) {
      syncedAnySupportedPlatform = true
      console.log(chalk.blue('\nSyncing Codex configuration...\n'))
      await syncCodex({
        sourceDir,
        projectDir: targetRoot,
        global,
        selected,
        staleRemovals: approvedStaleRemovals.codex,
        preserveMissingRules: getPreservedStaleNames(staleEntries, approvedStaleRemovals, 'codex', 'rules'),
      })
    }

    if (selectedPlatforms.includes('cursor')) {
      syncedAnySupportedPlatform = true
      await syncCursor({
        sourceDir,
        projectDir: targetRoot,
        global,
        selected,
        staleRemovals: approvedStaleRemovals.cursor,
      })
    }

    if (selectedPlatforms.includes('opencode')) {
      syncedAnySupportedPlatform = true
      await syncOpenCode({
        sourceDir,
        projectDir: targetRoot,
        global,
        selected,
        staleRemovals: approvedStaleRemovals.opencode,
        preserveMissingRules: getPreservedStaleNames(staleEntries, approvedStaleRemovals, 'opencode', 'rules'),
      })
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
      targetState.platforms[platform] = {
        ...previous,
        skills: buildNextPlatformState(skillsOnlySelected, staleEntries, approvedStaleRemovals, platform).skills,
      }
    }
  } else {
    for (const platform of selectedPlatforms) {
      targetState.platforms[platform] = buildNextPlatformState(selected, staleEntries, approvedStaleRemovals, platform)
    }
  }
  targetState.skillScope = skillScope
  targetState.syncMode = syncMode
  await saveSyncState(targetRoot, targetState)

  if (!syncedAnySupportedPlatform) {
    console.log(chalk.yellow('未选择已接入平台，本次未执行同步。'))
  }
}
