import fs from 'fs-extra'
import path from 'node:path'
import os from 'node:os'
import { confirm, isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import { normalizeSkillScope, resolveProjectSkillDir, resolveGlobalSkillDir, copySkillsToProjectPlatforms, deduplicateProjectSkills } from './sync-global-skills.js'
import { ensureSharedSkills, refreshSharedSkills } from './skill-store.js'
import { chalk } from './utils.js'
import { interactiveSelect, loadHookManifests, readBaselineDoc, resolveSourceDir, scanExisting, scanHooks, scanRules, scanSkills } from './sync.js'
import { hasManagedBaseline, parseManagedRuleNames, scanExistingCodexHooks, scanExistingCodexSkills } from './sync-codex.js'
import { scanExistingCursorRules } from './sync-cursor.js'
import { installSkills, refreshExternalSkills } from './skills-install.js'
import { selfUpgrade } from './self-upgrade.js'
import { buildSyncPlan, contentOptions, projectSkillChoices, PLATFORM_LABELS, PLATFORM_SYNC_TYPES } from './sync-plan.js'
import { assertConfigPath, baselineProviders, globalBaselinePath, globalHookNames, hasManagedHookConfig } from './sync-inheritance.js'

const PLATFORM_OPTIONS = [
  { value: 'claude', label: 'Claude Code', description: '支持 Skills、Hooks 和全局通用规范' },
  { value: 'codex', label: 'Codex', description: '支持 Skills、Hooks 和全局通用规范' },
  { value: 'opencode', label: 'OpenCode', description: '支持 Skills 和全局通用规范；不支持 Hooks' },
]
const SYNC_STATE_PATH = ['.dwy', 'sync-state.json']
/** 按显式选中的内容同步；保留已有脚本的模式标识。 */
export const SYNC_MODE_ALL = 'all'
/** 兼容已有脚本的仅 Skills 模式。 */
export const SYNC_MODE_SKILLS = 'skills'
export const DEFAULT_SYNC_MODE = SYNC_MODE_ALL
/** 交互式配置同步。 */
export const ACTION_SYNC = 'sync'
/** 安装产品流程依赖的外部 Skills；仅供已有脚本调用。 */
export const ACTION_INSTALL_SKILLS = 'install-skills'
/** 升级全局 CLI。 */
export const ACTION_UPGRADE = 'upgrade'

/** 兼容已有脚本的模式值，不从模式推导交互中的隐式写入。 */
export function normalizeSyncMode(raw) {
  return raw === SYNC_MODE_SKILLS ? SYNC_MODE_SKILLS : DEFAULT_SYNC_MODE
}

/** 兼容已有脚本的入口动作；未知动作进入正常交互。 */
export function normalizeAction(raw) {
  if (raw === ACTION_INSTALL_SKILLS) return ACTION_INSTALL_SKILLS
  if (raw === ACTION_UPGRADE) return ACTION_UPGRADE
  return ACTION_SYNC
}

function unionSets(...sets) {
  return new Set(sets.flatMap(set => [...set]))
}

/** 从点名的平台记录恢复选择；未传平台时保留历史调用约定。 */
export function buildSelectionDefaultsFromSyncState(existing, syncState, platforms = Object.keys(syncState?.platforms || {})) {
  const result = { skills: new Set(), rules: new Set(), commands: new Set(), hooks: new Set() }
  for (const platform of platforms) {
    const state = syncState?.platforms?.[platform] || {}
    for (const type of Object.keys(result)) for (const name of state[type] || []) result[type].add(name)
  }
  return Object.values(result).some(names => names.size) ? result : existing
}

/** Codex 默认选中；恢复当前范围的同步记录和有效旧托管入口，空目录不算已同步。 */
export async function buildPlatformDefaultsFromLocalState(projectDir, scope = 'project', codexHome = path.join(projectDir, '.codex')) {
  const defaults = ['codex']
  const state = await loadSyncState(projectDir)
  for (const platform of ['claude', 'opencode', ...(scope === 'project' ? ['cursor'] : [])]) {
    const root = scope === 'global' ? resolveGlobalSkillDir(platform, projectDir)
      : resolveProjectSkillDir(projectDir, platform)
    let managed = Boolean(state.platforms[platform])
    if (root && await fs.pathExists(root)) {
      for (const name of await fs.readdir(root)) {
        if (name.startsWith('dwy-') && await fs.pathExists(path.join(root, name, 'SKILL.md'))) managed = true
      }
    }
    if (platform === 'cursor') {
      if ([...await scanExistingCursorRules(projectDir)].some(name => name.startsWith('dwy-') || name === '00-dwy-global.mdc')) managed = true
    } else {
      const baseline = scope === 'global' ? globalBaselinePath(platform, projectDir, codexHome)
        : path.join(projectDir, platform === 'claude' ? '.claude' : '.opencode', 'AGENTS.md')
      if (await hasManagedBaseline(baseline)) managed = true
      if (platform === 'claude') {
        const configRoot = path.join(projectDir, '.claude')
        if (await hasManagedBaseline(path.join(configRoot, 'CLAUDE.md'))
          || await hasManagedHookConfig(platform, configRoot, await scanExisting(configRoot, 'hooks'))) managed = true
      }
    }
    if (managed) defaults.push(platform)
  }
  return defaults
}

async function selectPlatforms(root, scope, initialValues) {
  const state = await loadSyncState(root)
  const result = await searchableMultiselect({
    message: '选择要同步的平台',
    options: PLATFORM_OPTIONS.filter(option => scope === 'project' || option.value !== 'cursor')
      .map(option => ({ ...option, description: [state.platforms[option.value] ? '已有同步记录，将核对并修复本地配置' : '',
        contentOptions(scope, [option.value]).map(item => item.label).join('、')].filter(Boolean).join('；') })),
    initialValues: initialValues.filter(platform => PLATFORM_OPTIONS.some(option => option.value === platform)),
    required: true, maxItems: 6, placeholder: SEARCH_PLACEHOLDER,
  })
  return isCancel(result) ? null : result
}

function createEmptyPlatformState() {
  return { skills: [], rules: [], commands: [], hooks: [] }
}

async function loadSyncState(root) {
  const file = path.join(root, ...SYNC_STATE_PATH)
  if (!await fs.pathExists(file)) return { version: 1, platforms: {}, skillScope: normalizeSkillScope(undefined), syncMode: DEFAULT_SYNC_MODE }
  const state = await fs.readJson(file)
  return { version: 1, platforms: state.platforms || {}, skillScope: normalizeSkillScope(state.skillScope), syncMode: normalizeSyncMode(state.syncMode) }
}

async function saveSyncState(root, state) {
  const file = path.join(root, ...SYNC_STATE_PATH)
  await fs.ensureDir(path.dirname(file))
  await fs.writeJson(file, state, { spaces: 2 })
}

function buildCursorRuleName(name) {
  return `dwy-${name.replace(/\.md$/i, '')}.mdc`
}

async function managedNames(root, global, codexHome) {
  const projectFile = path.join(root, 'AGENTS.md')
  const projectRules = !global && await fs.pathExists(projectFile)
    ? parseManagedRuleNames(await fs.readFile(projectFile, 'utf8')) : new Set()
  const claude = path.join(root, '.claude')
  const opencode = path.join(root, ...(global ? ['.config', 'opencode'] : ['.opencode']))
  const codexSkills = await scanExistingCodexSkills(root)
  if (global && await fs.pathExists(path.join(codexHome, 'skills'))) {
    for (const name of await fs.readdir(path.join(codexHome, 'skills'))) codexSkills.add(name)
  }
  return {
    projectRules,
    claude: { skills: await scanExisting(claude, 'skills'), rules: unionSets(projectRules, await scanExisting(claude, 'rules')), hooks: await scanExisting(claude, 'hooks') },
    codex: { skills: codexSkills, rules: projectRules, hooks: await scanExistingCodexHooks(root, global ? codexHome : path.join(root, '.codex')) },
    opencode: { skills: await scanExisting(opencode, 'skills'), rules: projectRules, hooks: new Set() },
    cursor: { rules: await scanExistingCursorRules(root), skills: new Set(), hooks: new Set() },
  }
}

/** 刷新全局和当前项目已启用的托管内容；其他项目通过共享 Skills 链接生效，不扫描磁盘。 */
export async function refreshAll({
  sourceDir, projectDir = process.cwd(), homeDir = os.homedir(),
  codexHome = process.env.CODEX_HOME || path.join(homeDir, '.codex'),
} = {}) {
  sourceDir ||= await resolveSourceDir({ homeDir })
  const scans = { skills: await scanSkills(sourceDir), rules: await scanRules(sourceDir), hooks: await scanHooks(sourceDir), commands: [] }
  const baseline = await readBaselineDoc(sourceDir)
  let projectState = await loadSyncState(projectDir), globalState = await loadSyncState(homeDir)
  const isHome = await fs.realpath(projectDir) === await fs.realpath(homeDir)
  for (const scope of isHome ? ['global'] : ['global', 'project']) {
    const global = scope === 'global', root = global ? homeDir : projectDir
    const existing = await managedNames(root, global, codexHome)
    for (const platform of Object.keys(PLATFORM_SYNC_TYPES).filter(p => !global || p !== 'cursor')) {
      const state = (global ? globalState : projectState).platforms[platform]
      const names = type => new Set([...(state?.[type] || []), ...existing[platform][type]])
      const selected = { skills: scans.skills.filter(item => names('skills').has(item.name)),
        rules: scans.rules.filter(item => names('rules').has(platform === 'cursor' ? buildCursorRuleName(item.name) : item.name)
          || (state?.rules || []).includes(item.name)) }
      const hooks = scans.hooks.filter(item => names('hooks').has(item.name))
      const baselinePath = global ? globalBaselinePath(platform, homeDir, codexHome) : path.join(projectDir, 'AGENTS.md')
      const managedBaseline = platform !== 'cursor' && await hasManagedBaseline(baselinePath)
      const contentTypes = PLATFORM_SYNC_TYPES[platform].filter(type => type === 'baseline'
        ? baseline.trim() && (state?.baseline || managedBaseline)
        : type === 'hooks' ? hooks.length : selected[type]?.length)
      if (!contentTypes.length) continue
      const plan = await buildSyncPlan({ scope, platforms: [platform], contentTypes, selected,
        scans: { ...scans, hooks }, sourceDir, projectDir, homeDir, codexHome, projectState, globalState, baseline,
        installExternalDependencies: false,
        staleEntries: staleEntries(scans, global ? globalState : projectState, existing, [platform]),
      })
      for (const operation of plan.operations) await operation.run()
      projectState = plan.nextProject
      globalState = plan.nextGlobal
      if (plan.projectChanged) {
        await assertConfigPath(path.join(projectDir, ...SYNC_STATE_PATH), projectDir)
        await saveSyncState(projectDir, projectState)
      }
      if (plan.globalChanged) {
        await assertConfigPath(path.join(homeDir, ...SYNC_STATE_PATH), homeDir)
        await saveSyncState(homeDir, globalState)
      }
      console.log(chalk.green(`已刷新${global ? '全局' : '当前项目'} ${PLATFORM_LABELS[platform]}：${contentTypes.join('、')}`))
    }
  }
  await refreshSharedSkills({ sourceDir, homeDir })
  await refreshExternalSkills(path.join(process.env.DWY_HOME || path.join(homeDir, '.dwy'), 'skills'))
}

const RULE_SKILL_MIGRATIONS = {
  'dwy-python-core.md': ['dwy-python-development'],
  'dwy-python-testing.md': ['dwy-python-development'],
  'dwy-python-pitfalls.md': ['dwy-python-development'],
  'dwy-python-base-lib.md': ['dwy-python-development', 'dwy-eapi'],
  'dwy-python-backend.md': ['dwy-python-api'],
  'dwy-python-layering.md': ['dwy-python-architecture'],
  'dwy-vue-core.md': ['dwy-vue-development'],
  'dwy-vue-testing.md': ['dwy-vue-development'],
  'dwy-vue-pitfalls.md': ['dwy-vue-development'],
  'dwy-vue-pinia.md': ['dwy-vue-development'],
  'dwy-vue-base-lib.md': ['dwy-vue-development', 'dwy-eui', 'dwy-ekit'],
  'dwy-vue-layering.md': ['dwy-vue-architecture'],
  'dwy-swift-core.md': ['dwy-swift-development'],
  'dwy-apple-layering.md': ['dwy-apple-architecture'],
  'dwy-ios-layout-adaptation.md': ['dwy-ios-development'],
  'dwy-ios-pitfalls.md': ['dwy-ios-development'],
  'dwy-android-core.md': ['dwy-android-development'],
  'dwy-android-pitfalls.md': ['dwy-android-development'],
  'dwy-android-support-only.md': ['dwy-android-development'],
  'dwy-android-layering.md': ['dwy-android-architecture'],
  'dwy-android-mvp.md': ['dwy-android-architecture'],
  'dwy-flutter-core.md': ['dwy-flutter-development'],
  'dwy-flutter-network.md': ['dwy-flutter-development'],
  'dwy-flutter-router.md': ['dwy-flutter-development'],
  'dwy-flutter-testing.md': ['dwy-flutter-development'],
  'dwy-arkts-strict.md': ['dwy-harmony-development'],
  'dwy-arkts-ui-build.md': ['dwy-harmony-development'],
  'dwy-arkts-ui-design.md': ['dwy-harmony-development'],
  'dwy-harmony-pitfalls.md': ['dwy-harmony-development'],
  'dwy-postgres.md': ['dwy-postgres'],
  'dwy-redis.md': ['dwy-redis'],
  'dwy-db-migration.md': ['dwy-alembic'],
  'dwy-docker.md': ['dwy-docker'],
  'dwy-code-craft.md': ['dwy-development-review'],
  'dwy-dependency-freshness.md': ['dwy-dependency-choice'],
  'dwy-oss-commercial-license.md': ['dwy-dependency-choice'],
  'dwy-git-commit.md': ['dwy-git-commit'],
  'dwy-prod-branch.md': ['dwy-publish'],
}

function staleEntries(scans, state, existing, platforms) {
  const current = Object.fromEntries(['skills', 'rules', 'hooks'].map(type => [type, new Set(scans[type].map(item => item.name))]))
  const result = {}
  for (const platform of platforms) {
    result[platform] = {}
    for (const type of PLATFORM_SYNC_TYPES[platform].filter(type => current[type])) {
      const historical = state.platforms[platform]?.[type] || []
      const knownRules = type === 'rules' && platform !== 'cursor'
        ? [...existing.projectRules].filter(name => !scans.rules.length || RULE_SKILL_MIGRATIONS[name]) : []
      result[platform][type] = [...new Set([...historical, ...knownRules])].filter(name =>
        !current[type].has(name) && existing[platform][type].has(platform === 'cursor' && type === 'rules' ? buildCursorRuleName(name) : name))
    }
  }
  return result
}

function normalizeRemovals(raw) {
  return Object.fromEntries(Object.entries(raw).map(([platform, types]) => [platform,
    Object.fromEntries(Object.entries(types).map(([type, names]) => [type, new Set(names)]))]))
}

/** `dwy` 和 `dwy sync` 共用范围 → Skills → 规范 → Hooks → CLI → 确认。 */
export async function runDwy(opts = {}) {
  console.log(chalk.bold.cyan('\ndwy') + chalk.gray(' · AI 开发工具\n'))
  const action = normalizeAction(opts.action)
  if (action === ACTION_INSTALL_SKILLS) { await installSkills(); return }
  if (action === ACTION_UPGRADE) {
    try { await selfUpgrade() } catch (error) { console.error(error.message); process.exitCode = 1 }
    return
  }
  return syncAll(opts)
}

/**
 * 一键迁移当前项目已有的 CLI Skills，不进入选择流程、不补装其他平台、不修改 Rules / Hooks。
 * 仅当前模板或历史同步记录中的名称视为托管；已移除的历史模板和整个根目录链接保留并报告。
 */
export async function migrateSkills({
  sourceDir,
  projectDir = process.cwd(),
  homeDir = os.homedir(),
  codexHome = process.env.CODEX_HOME || path.join(homeDir, '.codex'),
} = {}) {
  const realProject = await fs.realpath(projectDir)
  if (await fs.pathExists(homeDir) && realProject === await fs.realpath(homeDir)) {
    throw new Error('当前目录是用户主目录，请使用全局同步或进入项目目录迁移')
  }
  const scans = await scanSkills(sourceDir || await resolveSourceDir({ homeDir }))
  const available = new Map(scans.map(skill => [skill.name, skill]))
  const state = await loadSyncState(projectDir)
  const existingByPlatform = {}
  const neededNames = new Set()
  const retained = []
  for (const platform of ['claude', 'codex', 'opencode']) {
    const root = resolveProjectSkillDir(projectDir, platform)
    if (!await fs.pathExists(root)) continue
    if (await fs.realpath(root) !== path.join(realProject, path.relative(projectDir, root))) {
      console.log(chalk.yellow(`${root} 已通过根目录链接共享内容，保留原链接，不迁移其目标。`))
      continue
    }
    const existing = await scanExisting(path.dirname(root), 'skills')
    const historical = new Set(state.platforms[platform]?.skills || [])
    const managed = [...existing].filter(name => available.has(name) || historical.has(name))
    if (managed.length === 0) continue
    existingByPlatform[platform] = managed
    for (const name of managed) {
      if (available.has(name)) neededNames.add(name)
      else {
        retained.push({ platform, name })
        console.log(chalk.yellow(`${platform}/${name} 已不在当前模板中，保留原目录。`))
      }
    }
  }
  const shared = await ensureSharedSkills({ skills: [...neededNames].map(name => available.get(name)), homeDir })
  let linked = 0
  let globalCount = 0
  for (const [platform, names] of Object.entries(existingByPlatform)) {
    const skills = shared.filter(skill => names.includes(skill.name))
    const duplicates = await deduplicateProjectSkills({ projectDir, platform, skills, homeDir, codexHome })
    const local = skills.filter(skill => !duplicates.has(skill.name))
    linked += await copySkillsToProjectPlatforms({ projectDir, platforms: [platform], skills: local, homeDir })
    globalCount += duplicates.size
    state.platforms[platform] = {
      ...(state.platforms[platform] || createEmptyPlatformState()),
      skills: names.filter(name => !duplicates.has(name)).sort(),
    }
  }
  if (Object.keys(existingByPlatform).length) await saveSyncState(projectDir, state)
  console.log(chalk.green(`迁移完成：${linked} 个项目链接，${globalCount} 个使用全局入口，${retained.length} 个历史条目保留。`))
  return { linked, global: globalCount, retained }
}


/**
 * 只执行点名范围和内容；测试/脚本可注入选择，确认前只读。
 * 主交互按内容顺序收集选择，CLI 后选，执行前重新核算继承；显式脚本仅处理点名的类型。
 */
export async function syncAll({
  sourceDir: sourceDirOverride, projectDir: projectDirOverride, selected: selectedOverride,
  selectedPlatforms: platformsOverride, contentTypes: typesOverride, staleRemovals: removalsOverride,
  skillScope: skillScopeOverride, syncMode: modeOverride, homeDir = os.homedir(),
  codexHome = process.env.CODEX_HOME || path.join(homeDir, '.codex'), scope: scopeOverride, confirmed,
  contentActions: actionsOverride,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir({ homeDir })
  if (!await fs.pathExists(sourceDir)) throw new Error('ai-tools templates not found in repo')
  const projectDir = projectDirOverride || process.cwd()
  const scope = scopeOverride || (selectedOverride || platformsOverride ? 'project' : await searchableSelect({
    message: '选择同步范围',
    options: [
      { value: 'project', label: '当前项目', description: '管理 Skills、Hooks 和通用规范；继承有效全局配置' },
      { value: 'global', label: '全局', description: '管理 Skills、Hooks 和通用规范；清理当前项目重复入口' },
    ], initialValue: 'project',
  }))
  if (isCancel(scope)) { console.log(chalk.yellow('已取消同步。')); return }
  if (!['project', 'global'].includes(scope)) throw new Error('无效同步范围')
  const global = scope === 'global', targetRoot = global ? homeDir : projectDir
  let platforms = platformsOverride || await buildPlatformDefaultsFromLocalState(targetRoot, scope, codexHome)
  if (!platformsOverride) platforms = platforms.filter(platform => PLATFORM_OPTIONS.some(option => option.value === platform))
  if (platforms.length === 0 || platforms.some(platform => !PLATFORM_SYNC_TYPES[platform] || (global && platform === 'cursor'))) throw new Error('所选平台不支持此同步范围')
  const projectState = await loadSyncState(projectDir), globalState = await loadSyncState(homeDir)
  const targetState = global ? globalState : projectState
  const scans = { skills: await scanSkills(sourceDir), rules: await scanRules(sourceDir), hooks: await scanHooks(sourceDir), commands: [] }
  const mainFlow = !typesOverride && !selectedOverride && modeOverride !== SYNC_MODE_SKILLS
  const availablePlatforms = PLATFORM_OPTIONS.filter(option => !global || option.value !== 'cursor').map(option => option.value)
  const allowed = new Set(contentOptions(scope, mainFlow ? availablePlatforms : platforms).map(option => option.value))
  let contentTypes = typesOverride
  if (!contentTypes && modeOverride === SYNC_MODE_SKILLS) contentTypes = ['skills']
  if (!contentTypes && selectedOverride) contentTypes = Object.keys(selectedOverride).filter(type => allowed.has(type))
  if (!contentTypes) {
    contentTypes = [...allowed]
    if (!await fs.pathExists(path.join(sourceDir, 'AGENTS.md'))) contentTypes = contentTypes.filter(type => type !== 'baseline')
    if (!scans.hooks.length) contentTypes = contentTypes.filter(type => type !== 'hooks')
  }
  if (contentTypes.some(type => !allowed.has(type))) throw new Error('所选范围或平台不支持此同步内容')
  if (contentTypes.length === 0) { console.log('未选择处理内容。'); return }
  const existing = await managedNames(targetRoot, global, codexHome)
  const cursorRules = new Set([...scans.rules.map(rule => rule.name), ...Object.keys(RULE_SKILL_MIGRATIONS)]
    .filter(name => existing.cursor.rules.has(buildCursorRuleName(name))))
  const current = Object.fromEntries(['skills', 'rules', 'hooks'].map(type => [type,
    unionSets(...platforms.map(platform => platform === 'cursor' && type === 'rules' ? cursorRules : existing[platform][type]))]))
  const defaults = buildSelectionDefaultsFromSyncState(current, targetState, platforms)
  for (const type of ['skills', 'rules', 'hooks']) defaults[type] = unionSets(defaults[type], current[type])
  const choices = !global && contentTypes.includes('skills')
    ? { ...scans, skills: await projectSkillChoices(scans.skills, platforms, { homeDir, codexHome }) } : scans
  const selected = selectedOverride
    ? { skills: selectedOverride.skills || [], rules: selectedOverride.rules || [], hooks: [], commands: [] }
    : await interactiveSelect(choices, defaults, { types: contentTypes })
  if (selected === null) { console.log(chalk.yellow('已取消同步。')); return }
  const contentActions = { ...actionsOverride }
  if (!selectedOverride) {
    for (const type of ['baseline', 'hooks'].filter(type => contentTypes.includes(type))) {
      if (contentActions[type]) continue
      const inherited = type === 'baseline' && !global ? await baselineProviders(platforms, { homeDir, codexHome }) : []
      const name = type === 'hooks' ? 'Hooks' : 'AGENTS.md 通用规范'
      let inheritedHooks = false
      if (type === 'hooks' && !global) {
        const manifests = await loadHookManifests(sourceDir)
        let total = 0, covered = 0
        for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('hooks'))) {
          const available = scans.hooks.filter(hook => manifests.some(manifest => manifest.name === hook.name && (!manifest.platforms || manifest.platforms.includes(platform))))
          const provided = await globalHookNames({ platform, sourceDir, homeDir, codexHome })
          total += available.length
          covered += available.filter(hook => provided.has(hook.name)).length
        }
        inheritedHooks = total > 0 && covered === total
      }
      if (inherited.length || inheritedHooks) {
        contentActions[type] = 'sync'
        continue
      }
      const action = await searchableSelect({
        message: `选择 ${name} 操作`, initialValue: 'sync',
        options: [
          { value: 'sync', label: '启用 / 更新',
            description: type === 'hooks' && !global ? '只为缺少有效全局注册的 Hook 安装项目配置，其他仅去重' : '执行清单会列出实际路径及清理项' },
          { value: 'remove', label: `移除当前范围的${name}`, description: '只移除 dwy 托管内容，保留个人配置和其他类型' },
        ],
      })
      if (isCancel(action)) { console.log(chalk.yellow('已取消同步。')); return }
      contentActions[type] = action
    }
  }
  if (!platformsOverride) {
    platforms = await selectPlatforms(targetRoot, scope, platforms)
    if (platforms === null) { console.log(chalk.yellow('已取消同步。')); return }
  }
  // 禁选的全局 Skills 仍处于启用状态；末步新增 CLI 时只补缺失入口，已有全局源保持原样。
  if (!selectedOverride && !global) selected.skills.push(...choices.skills.filter(skill => skill.disabled))
  const options = contentOptions(scope, platforms)
  if (mainFlow) contentTypes = contentTypes.filter(type => options.some(option => option.value === type))
  const stale = staleEntries(scans, targetState, existing, platforms)
  const removals = normalizeRemovals(removalsOverride || stale)
  if (!removalsOverride) {
    for (const platform of platforms) for (const name of removals[platform]?.rules || []) {
      const knownRule = RULE_SKILL_MIGRATIONS[name]
      if (!knownRule && !scans.rules.length) {
        removals[platform].rules.delete(name)
        continue
      }
      if (knownRule && platform === 'cursor') {
        removals[platform].rules.delete(name)
      }
    }
  }
  const baseline = contentTypes.some(type => type === 'rules' || type === 'baseline') ? await readBaselineDoc(sourceDir) : ''
  const plan = await buildSyncPlan({
    scope, platforms, contentTypes, selected, scans, sourceDir, projectDir, homeDir, codexHome,
    projectState, globalState, staleRemovals: removals, staleEntries: stale, baseline,
    migratedRuleSources: Object.fromEntries(Object.entries(RULE_SKILL_MIGRATIONS).flatMap(([name, skills]) => {
      const skill = scans.skills.find(item => item.name === skills[0])
      return skill ? [[name, path.join(skill.sourcePath, 'references', name)]] : []
    })),
    contentActions,
    refreshSkills: mainFlow,
    skillScope: normalizeSkillScope(skillScopeOverride),
  })
  const nextTarget = global ? plan.nextGlobal : plan.nextProject
  nextTarget.contentTypes = contentTypes
  nextTarget.syncMode = contentTypes.length === 1 && contentTypes[0] === 'skills' ? SYNC_MODE_SKILLS : SYNC_MODE_ALL
  nextTarget.skillScope = normalizeSkillScope(skillScopeOverride)
  const stateFile = path.join(targetRoot, ...SYNC_STATE_PATH)
  await assertConfigPath(stateFile, targetRoot)
  plan.operations.push({ kind: 'state', label: '更新当前范围同步记录', paths: [stateFile], run: async () => {
    await assertConfigPath(stateFile, targetRoot)
    await saveSyncState(targetRoot, nextTarget)
  } })
  if (global && plan.projectChanged) plan.operations.push({
    kind: 'state', label: '更新项目去重记录', paths: [path.join(projectDir, ...SYNC_STATE_PATH)],
    run: async () => { await assertConfigPath(path.join(projectDir, ...SYNC_STATE_PATH), projectDir); await saveSyncState(projectDir, plan.nextProject) },
  })
  if (global && plan.projectChanged) await assertConfigPath(path.join(projectDir, ...SYNC_STATE_PATH), projectDir)
  console.log(`\n同步范围：${global ? '全局' : '当前项目'}；平台：${platforms.map(p => PLATFORM_LABELS[p]).join('、')}`)
  console.log(`处理内容：${contentTypes.map(type => type === 'rules' && !scans.rules.length ? '旧规则迁移' : options.find(option => option.value === type).label).join('、')}`)
  if (contentTypes.includes('skills')) console.log(`Skills：${selected.skills.map(item => item.name).join('、') || '无项目安装选择；已有全局入口仅去重'}`)
  if (contentTypes.includes('rules')) console.log(scans.rules.length
    ? `Rules：${selected.rules.map(item => item.name).join('、') || '移除当前项目托管规则'}`
    : '旧 Rules：清理可识别的托管项，其他内容保留；Skills 自行选择')
  if (contentTypes.includes('baseline')) console.log(`通用规范：${contentActions.baseline === 'remove' ? '显式移除' : baseline.split('\n').filter(line => /^#/.test(line)).slice(0,3).join('；')}`)
  for (const operation of plan.operations) {
    console.log(operation.label)
    for (const dest of operation.paths) console.log(`  → ${dest}`)
  }
  if ((!selectedOverride && confirmed !== true) || confirmed === false) {
    const answer = confirmed === false ? false : await confirm({ message: '确认同步？' })
    if (isCancel(answer) || !answer) { console.log(chalk.yellow('已取消同步。')); return }
  }
  for (const operation of plan.operations) {
    await operation.run()
    if (!['state', 'inherit'].includes(operation.kind)) console.log(chalk.green(`已完成：${operation.label}`))
  }
  console.log(chalk.green('同步完成。'))
  return plan.operations.map(({ kind, label, paths }) => ({ kind, label, paths }))
}
