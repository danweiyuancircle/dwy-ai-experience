import fs from 'fs-extra'
import path from 'node:path'
import os from 'node:os'
import { confirm, isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import { normalizeSkillScope, resolveProjectSkillDir, resolveGlobalSkillDir, copySkillsToProjectPlatforms, deduplicateProjectSkills } from './sync-global-skills.js'
import { ensureSharedSkills } from './skill-store.js'
import { chalk } from './utils.js'
import { interactiveSelect, loadHookManifests, readBaselineDoc, resolveSourceDir, scanExisting, scanHooks, scanRules, scanSkills } from './sync.js'
import { parseManagedRuleNames, scanExistingCodexHooks, scanExistingCodexSkills } from './sync-codex.js'
import { scanExistingCursorRules } from './sync-cursor.js'
import { installSkills } from './skills-install.js'
import { selfUpgrade } from './self-upgrade.js'
import { buildSyncPlan, contentOptions, projectSkillChoices, PLATFORM_LABELS, PLATFORM_SYNC_TYPES } from './sync-plan.js'
import { assertConfigPath, baselineProviders, globalHookNames } from './sync-inheritance.js'

const PLATFORM_OPTIONS = [
  { value: 'claude', label: 'Claude Code', description: '支持 Skills、项目 Rules、Hooks 和全局通用规范' },
  { value: 'codex', label: 'Codex', description: '支持 Skills、项目 Rules、Hooks 和全局通用规范' },
  { value: 'opencode', label: 'OpenCode', description: '支持 Skills、项目 Rules 和全局通用规范；不支持 Hooks' },
  { value: 'cursor', label: 'Cursor', description: '只支持项目 Rules' },
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

/** 从当前范围的实际入口推导平台默认值；不读取另一个范围的配置。 */
export async function buildPlatformDefaultsFromLocalState(projectDir, scope = 'project', codexHome = path.join(projectDir, '.codex')) {
  const defaults = []
  if (await fs.pathExists(path.join(projectDir, '.claude'))) defaults.push('claude')
  if (await fs.pathExists(path.join(projectDir, '.codex'))
    || (scope === 'global' && await fs.pathExists(codexHome))
    || await fs.pathExists(path.join(projectDir, '.agents'))
    || (scope === 'project' && await fs.pathExists(path.join(projectDir, 'AGENTS.md')))) defaults.push('codex')
  if (scope === 'project' && await fs.pathExists(path.join(projectDir, '.cursor'))) defaults.push('cursor')
  if (await fs.pathExists(path.join(projectDir, ...(scope === 'global' ? ['.config', 'opencode'] : ['.opencode'])))) defaults.push('opencode')
  return defaults.length ? defaults : ['claude', 'codex']
}

async function selectPlatforms(root, scope, codexHome) {
  const result = await searchableMultiselect({
    message: '选择要同步的平台',
    options: PLATFORM_OPTIONS.filter(option => scope === 'project' || option.value !== 'cursor')
      .map(option => ({ ...option, description: contentOptions(scope, [option.value]).map(item => item.label).join('、') })),
    initialValues: await buildPlatformDefaultsFromLocalState(root, scope, codexHome),
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
    claude: { skills: await scanExisting(claude, 'skills'), rules: unionSets(projectRules, await scanExisting(claude, 'rules')), hooks: await scanExisting(claude, 'hooks') },
    codex: { skills: codexSkills, rules: projectRules, hooks: await scanExistingCodexHooks(root, global ? codexHome : path.join(root, '.codex')) },
    opencode: { skills: await scanExisting(opencode, 'skills'), rules: projectRules, hooks: new Set() },
    cursor: { rules: await scanExistingCursorRules(root), skills: new Set(), hooks: new Set() },
  }
}

function staleEntries(scans, state, existing, platforms) {
  const current = Object.fromEntries(['skills', 'rules', 'hooks'].map(type => [type, new Set(scans[type].map(item => item.name))]))
  const result = {}
  for (const platform of platforms) {
    result[platform] = {}
    for (const type of PLATFORM_SYNC_TYPES[platform].filter(type => current[type])) {
      result[platform][type] = (state.platforms[platform]?.[type] || []).filter(name =>
        !current[type].has(name) && existing[platform][type].has(platform === 'cursor' && type === 'rules' ? buildCursorRuleName(name) : name))
    }
  }
  return result
}

/** 全局首次默认管理基线；任一所选平台显式移除后不再整组默认开启。 */
export function defaultContentTypes(scope, platforms, state) {
  const allowed = new Set(contentOptions(scope, platforms).map(option => option.value))
  const result = allowed.has('skills') ? ['skills'] : []
  if (scope === 'global' && allowed.has('baseline') && platforms.every(platform => state.platforms[platform]?.baseline !== false)) result.push('baseline')
  return result
}

function normalizeRemovals(raw) {
  return Object.fromEntries(Object.entries(raw).map(([platform, types]) => [platform,
    Object.fromEntries(Object.entries(types).map(([type, names]) => [type, new Set(names)]))]))
}

/** `dwy` 和 `dwy sync` 共用范围 → 平台 → 内容 → 逐项选择 → 清单确认。 */
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
  const scans = await scanSkills(sourceDir || await resolveSourceDir())
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
 * contentTypes 未传时，已有脚本按 selected 中明确提供的字段处理；主交互默认只选 Skills。
 */
export async function syncAll({
  sourceDir: sourceDirOverride, projectDir: projectDirOverride, selected: selectedOverride,
  selectedPlatforms: platformsOverride, contentTypes: typesOverride, staleRemovals: removalsOverride,
  skillScope: skillScopeOverride, syncMode: modeOverride, homeDir = os.homedir(),
  codexHome = process.env.CODEX_HOME || path.join(homeDir, '.codex'), scope: scopeOverride, confirmed,
  contentActions: actionsOverride,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) throw new Error('ai-tools templates not found in repo')
  const projectDir = projectDirOverride || process.cwd()
  const scope = scopeOverride || (selectedOverride || platformsOverride ? 'project' : await searchableSelect({
    message: '选择同步范围',
    options: [
      { value: 'project', label: '当前项目', description: '管理 Skills、Hooks、Rules 和通用规范；继承有效全局配置' },
      { value: 'global', label: '全局', description: '管理 Skills、Hooks 和通用规范；清理当前项目重复入口' },
    ], initialValue: 'project',
  }))
  if (isCancel(scope)) { console.log(chalk.yellow('已取消同步。')); return }
  if (!['project', 'global'].includes(scope)) throw new Error('无效同步范围')
  const global = scope === 'global', targetRoot = global ? homeDir : projectDir
  const platforms = platformsOverride || await selectPlatforms(targetRoot, scope, codexHome)
  if (platforms === null) { console.log(chalk.yellow('已取消同步。')); return }
  if (platforms.length === 0 || platforms.some(platform => !PLATFORM_SYNC_TYPES[platform] || (global && platform === 'cursor'))) throw new Error('所选平台不支持此同步范围')
  const options = contentOptions(scope, platforms)
  const allowed = new Set(options.map(option => option.value))
  const projectState = await loadSyncState(projectDir), globalState = await loadSyncState(homeDir)
  const targetState = global ? globalState : projectState
  let contentTypes = typesOverride
  if (!contentTypes && modeOverride === SYNC_MODE_SKILLS) contentTypes = ['skills']
  if (!contentTypes && selectedOverride) contentTypes = Object.keys(selectedOverride).filter(type => allowed.has(type))
  if (!contentTypes) {
    const result = await searchableMultiselect({
      message: '选择本次处理内容（未勾选的类型保持原样）', options,
      initialValues: defaultContentTypes(scope, platforms, targetState), required: true, maxItems: 5,
    })
    if (isCancel(result)) { console.log(chalk.yellow('已取消同步。')); return }
    contentTypes = result
  }
  if (contentTypes.some(type => !allowed.has(type))) throw new Error('所选范围或平台不支持此同步内容')
  if (contentTypes.length === 0) { console.log('未选择处理内容。'); return }
  const scans = { skills: await scanSkills(sourceDir), rules: await scanRules(sourceDir), hooks: await scanHooks(sourceDir), commands: [] }
  const existing = await managedNames(targetRoot, global, codexHome)
  const current = Object.fromEntries(['skills', 'rules', 'hooks'].map(type => [type,
    unionSets(...platforms.map(platform => existing[platform][type]))]))
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
    for (const type of ['hooks', 'baseline'].filter(type => contentTypes.includes(type))) {
      if (contentActions[type]) continue
      const inherited = type === 'baseline' && !global ? await baselineProviders(platforms, { homeDir, codexHome }) : []
      const name = type === 'hooks' ? 'Hooks' : 'AGENTS.md 通用规范'
      if (inherited.length) console.log(chalk.yellow(`全局已启用通用规范：${inherited.map(p => PLATFORM_LABELS[p]).join('、')}；项目禁止重复安装，其他平台需补齐全局规范。`))
      let inheritedHooks = false
      if (type === 'hooks' && !global) {
        const manifests = await loadHookManifests(sourceDir)
        let total = 0, covered = 0
        for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('hooks'))) {
          const available = scans.hooks.filter(hook => manifests.some(manifest => manifest.name === hook.name && (!manifest.platforms || manifest.platforms.includes(platform))))
          const provided = await globalHookNames({ platform, sourceDir, homeDir, codexHome })
          total += available.length
          covered += available.filter(hook => provided.has(hook.name)).length
          if (provided.size) console.log(`${PLATFORM_LABELS[platform]} Hooks 全局已启用：${[...provided].join('、')}`)
        }
        inheritedHooks = total > 0 && covered === total
      }
      const action = await searchableSelect({
        message: `选择 ${name} 操作`, initialValue: 'sync',
        options: [
          { value: 'sync', label: inherited.length ? '使用全局，仅清理项目重复基线' : inheritedHooks ? '使用全局，仅清理项目重复 Hooks' : '启用 / 更新',
            description: type === 'hooks' && !global ? '只为缺少有效全局注册的 Hook 安装项目配置，其他仅去重' : '执行清单会列出实际路径及清理项' },
          { value: 'remove', label: `移除当前范围的${name}`, description: '只移除 dwy 托管内容，保留个人配置和其他类型' },
        ],
      })
      if (isCancel(action)) { console.log(chalk.yellow('已取消同步。')); return }
      contentActions[type] = action
    }
  }
  const stale = staleEntries(scans, targetState, existing, platforms)
  const removals = normalizeRemovals(removalsOverride || stale)
  const baseline = contentTypes.some(type => type === 'rules' || type === 'baseline') ? await readBaselineDoc(sourceDir) : ''
  const plan = await buildSyncPlan({
    scope, platforms, contentTypes, selected, scans, sourceDir, projectDir, homeDir, codexHome,
    projectState, globalState, staleRemovals: removals, staleEntries: stale, baseline,
    contentActions,
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
  console.log(`处理内容：${contentTypes.map(type => options.find(option => option.value === type).label).join('、')}`)
  if (contentTypes.includes('skills')) console.log(`Skills：${selected.skills.map(item => item.name).join('、') || '无项目安装选择；已有全局入口仅去重'}`)
  if (contentTypes.includes('rules')) console.log(`Rules：${selected.rules.map(item => item.name).join('、') || '移除当前项目托管规则'}`)
  if (contentTypes.includes('baseline')) console.log(`通用规范：${contentActions.baseline === 'remove' ? '显式移除' : baseline.split('\n').filter(line => /^#/.test(line)).slice(0,3).join('；')}`)
  for (const operation of plan.operations) {
    console.log(operation.label)
    for (const dest of operation.paths) console.log(`  → ${dest}`)
  }
  if ((!selectedOverride && confirmed !== true) || confirmed === false) {
    const answer = confirmed === false ? false : await confirm({ message: '确认同步？' })
    if (isCancel(answer) || !answer) { console.log(chalk.yellow('已取消同步。')); return }
  }
  for (const operation of plan.operations) await operation.run()
  console.log(chalk.green('同步完成。'))
  return plan.operations.map(({ kind, label, paths }) => ({ kind, label, paths }))
}
