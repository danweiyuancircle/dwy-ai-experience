import fs from 'fs-extra'
import path from 'node:path'
import { ensureSharedSkills, prepareSharedSkills, linkSkill, removeSkillEntry } from './skill-store.js'
import { findGlobalSkill, globalSkillRoots, resolveGlobalSkillDir, resolveProjectSkillDir } from './sync-global-skills.js'
import { loadHookManifests, syncClaude } from './sync.js'
import { hasManagedBaseline, removeLegacyBaseline, syncBaselineDoc, syncCodex, syncProjectAgentsMd } from './sync-codex.js'
import { syncCursor } from './sync-cursor.js'
import { assertConfigPath, assertHooksEnabled, baselineProviders, globalBaselinePath, globalHookNames, hasManagedHookConfig, hookConfigFile, removeManagedHooks } from './sync-inheritance.js'

/** 平台显示名，交互和变更清单共用。 */
export const PLATFORM_LABELS = { claude: 'Claude Code', codex: 'Codex', opencode: 'OpenCode', cursor: 'Cursor' }
/** 平台能力；全局不提供 Rules，Cursor 仅提供项目 Rules。 */
export const PLATFORM_SYNC_TYPES = {
  claude: ['skills', 'rules', 'hooks', 'baseline'], codex: ['skills', 'rules', 'hooks', 'baseline'],
  opencode: ['skills', 'rules', 'baseline'], cursor: ['rules'],
}

/** 只提供所选范围和平台支持的内容；未勾选类型不进入清理或状态更新。 */
export function contentOptions(scope, platforms) {
  const supports = type => platforms.some(platform => PLATFORM_SYNC_TYPES[platform]?.includes(type))
  return [
    ...(supports('skills') ? [{ value: 'skills', label: 'Skills', description: '管理当前范围的启用入口；已有共享内容不刷新' }] : []),
    ...(scope === 'project' && supports('rules') ? [{ value: 'rules', label: '项目规则（Rules）', description: '只更新当前项目的托管规则' }] : []),
    ...(supports('baseline') ? [{ value: 'baseline', label: 'AGENTS.md 通用规范', description: scope === 'global'
      ? '管理原生全局指令入口；首次默认启用，可显式移除' : '管理项目基线块；已有全局规范时仅可清理重复项' }] : []),
    ...(supports('hooks') ? [{ value: 'hooks', label: 'Hooks', description: '独立启用或移除整组；项目继承有效全局注册' }] : []),
  ]
}

/** 为项目 Skills 标注平台覆盖；只有全部适用平台已全局提供时才禁止重复选择。 */
export async function projectSkillChoices(skills, platforms, { homeDir, codexHome }) {
  const applicable = platforms.filter(platform => PLATFORM_SYNC_TYPES[platform]?.includes('skills'))
  return Promise.all(skills.map(async skill => {
    const covered = []
    for (const platform of applicable) {
      if (await findGlobalSkill({ name: skill.name, platform, homeDir, codexHome })) covered.push(platform)
    }
    const disabled = applicable.length > 0 && covered.length === applicable.length
    const missing = applicable.filter(platform => !covered.includes(platform))
    const status = disabled ? '全局已启用' : covered.length ? `${missing.map(p => PLATFORM_LABELS[p]).join('、')} 可安装到项目` : ''
    return { ...skill, disabled, inherited: covered.length > 0, label: status ? `${skill.name}（${status}）` : skill.name,
      description: [covered.length ? `全局已提供：${covered.map(p => PLATFORM_LABELS[p]).join('、')}` : '', skill.description].filter(Boolean).join('；') }
  }))
}

const safeName = name => typeof name === 'string' && name.length > 0 && name !== '.' && name !== '..' && path.basename(name) === name && !/[\\/]/.test(name)
const cursorRuleName = name => `dwy-${name.replace(/\.md$/i, '')}.mdc`

async function existsEntry(dest) {
  return fs.lstat(dest).then(() => true).catch(error => {
    if (error.code === 'ENOENT') return false
    throw error
  })
}

async function validSkill(dest) {
  const stat = await fs.stat(path.join(dest, 'SKILL.md')).catch(error => {
    if (['ENOENT', 'ENOTDIR', 'ELOOP'].includes(error.code)) return null
    throw error
  })
  return Boolean(stat?.isFile())
}

function ownedGlobalRoots(platform, homeDir, codexHome) {
  if (platform === 'codex') return globalSkillRoots(platform, homeDir, codexHome)
  return [resolveGlobalSkillDir(platform, homeDir)]
}

/**
 * 只读计算本次全部操作和下一份状态；run 回调只在确认后执行。
 * 主交互可在确认后刷新所选共享内容；显式脚本默认仅补缺，项目去重不改写全局提供者。
 */
export async function buildSyncPlan({
  scope, platforms, contentTypes, selected, scans, sourceDir, projectDir, homeDir, codexHome,
  projectState, globalState, staleRemovals = {}, staleEntries = {}, baseline,
  migratedRuleSources = {},
  contentActions = {},
  refreshSkills = false,
  skillScope = { destinations: ['project'], globalSkills: [] },
}) {
  const global = scope === 'global'
  const isHome = path.resolve(projectDir) === path.resolve(homeDir)
    || (await fs.pathExists(projectDir) && await fs.pathExists(homeDir)
      && await fs.realpath(projectDir) === await fs.realpath(homeDir))
  if (!global && isHome) {
    throw new Error('当前目录是用户主目录，请选择全局范围或进入项目目录')
  }
  const allowed = new Set(contentOptions(scope, platforms).map(option => option.value))
  if (platforms.some(platform => !PLATFORM_SYNC_TYPES[platform] || (global && platform === 'cursor'))
    || contentTypes.some(type => !allowed.has(type))) throw new Error('所选范围或平台不支持此同步内容')
  const active = new Set(contentTypes)
  for (const [type, action] of Object.entries(contentActions)) {
    if (!['baseline', 'hooks'].includes(type) || !['sync', 'remove'].includes(action)) throw new Error('无效的内容操作')
  }
  if (active.has('baseline') && contentActions.baseline !== 'remove' && !baseline.trim()) throw new Error('没有可同步的通用规范')
  const operations = []
  const nextProject = structuredClone(projectState), nextGlobal = structuredClone(globalState)
  const targetState = global ? nextGlobal : nextProject
  const targetRoot = global ? homeDir : projectDir
  const selectedSkillNames = new Set(selected.skills.map(item => item.name))
  const skillSources = new Map(scans.skills.map(item => [item.name, item]))
  const neededSkills = new Map()
  const addedGlobalPaths = new Set(), removedGlobalPaths = new Set()
  const localCleanup = new Set()
  let projectChanged = !global && contentTypes.length > 0
  const add = (kind, label, paths, run) => {
    // 无标记旧基线须在 Rules 追加前识别，否则原文会变成无法确认归属的混合内容。
    const beforeRules = ['baseline', 'remove-baseline'].includes(kind) ? operations.findIndex(operation => operation.kind === 'rules') : -1
    operations.splice(beforeRules < 0 ? operations.length : beforeRules, 0, { kind, label, paths, run })
  }
  const addConfig = async (kind, label, paths, boundary, run) => {
    for (const dest of paths) await assertConfigPath(dest, boundary)
    add(kind, label, paths, async () => {
      for (const dest of paths) await assertConfigPath(dest, boundary)
      await run()
    })
  }
  const platformState = platform => targetState.platforms[platform] ||= { skills: [], rules: [], hooks: [], commands: [] }
  const approved = (platform, type) => [...(staleRemovals[platform]?.[type] || [])].filter(safeName)
  const retained = (platform, type) => (staleEntries[platform]?.[type] || []).filter(name => safeName(name) && !approved(platform, type).includes(name))
  const backupRoot = path.join(targetRoot, '.dwy', 'skill-backups')
  const providedToProject = async (name, platform) => globalSkillRoots(platform, homeDir, codexHome)
    .some(root => addedGlobalPaths.has(path.join(root, name))) || Boolean(await findGlobalSkill({ name, platform, homeDir, codexHome }))

  if (active.has('skills')) {
    for (const destination of skillScope.destinations.filter(id => id !== 'project')) {
      const root = resolveGlobalSkillDir(destination, homeDir)
      if (!root) continue
      for (const name of skillScope.globalSkills) {
        const skill = skillSources.get(name)
        if (!skill) continue
        neededSkills.set(name, skill)
        const dest = path.join(root, name), shared = { ...skill, sourcePath: path.join(homeDir, '.dwy', 'skills', name) }
        add('link-skill', `显式脚本配置的额外全局入口：${name}`, [dest],
          () => linkSkill({ skill: shared, dest, backupRoot: path.join(homeDir, '.dwy', 'skill-backups') }))
        addedGlobalPaths.add(dest)
      }
    }
    for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('skills'))) {
      if (!global && !skillScope.destinations.includes('project')) continue
      const roots = global ? ownedGlobalRoots(platform, homeDir, codexHome) : [resolveProjectSkillDir(projectDir, platform)]
      const managed = new Set([...skillSources.keys(), ...approved(platform, 'skills')])
      const names = new Set([...selectedSkillNames, ...retained(platform, 'skills')])
      const actualNames = new Set()
      for (const skill of scans.skills) {
        if (!global && await providedToProject(skill.name, platform)) continue
        if (!names.has(skill.name)) continue
        let dest = path.join(roots[0], skill.name)
        if (global) {
          for (const root of roots) {
            if (await validSkill(path.join(root, skill.name))) { dest = path.join(root, skill.name); break }
          }
        }
        neededSkills.set(skill.name, skill)
        const shared = { ...skill, sourcePath: path.join(homeDir, '.dwy', 'skills', skill.name) }
        add('link-skill', `启用 ${PLATFORM_LABELS[platform]} Skill ${skill.name}（原真实目录先备份）`, [dest],
          () => linkSkill({ skill: shared, dest, backupRoot }))
        actualNames.add(skill.name)
        if (global) addedGlobalPaths.add(dest)
      }
      for (const root of roots) {
        if (!await fs.pathExists(root)) continue
        for (const name of await fs.readdir(root)) {
          if (!safeName(name) || !managed.has(name)) continue
          const dest = path.join(root, name)
          if (global ? names.has(name) : actualNames.has(name)) continue
          const globallyProvided = !global && await providedToProject(name, platform)
          add('remove-skill', `${globallyProvided ? '全局优先，清理项目重复入口' : '移除托管 Skill 入口'}：${name}（原真实目录先备份）`, [dest],
            () => removeSkillEntry({ dest, backupRoot }))
          if (global) removedGlobalPaths.add(dest)
        }
      }
      platformState(platform).skills = [...new Set([...actualNames, ...retained(platform, 'skills')])].sort()
    }
    if (global) {
      for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('skills'))) {
        const root = resolveProjectSkillDir(projectDir, platform)
        if (isHome || !await fs.pathExists(root)) continue
        for (const name of await fs.readdir(root)) {
          if (!skillSources.has(name)) continue
          let provided = false
          for (const globalRoot of globalSkillRoots(platform, homeDir, codexHome)) {
            const candidate = path.join(globalRoot, name)
            if (addedGlobalPaths.has(candidate) || (!removedGlobalPaths.has(candidate) && await validSkill(candidate))) { provided = true; break }
          }
          const dest = path.join(root, name)
          if (!provided || localCleanup.has(dest)) continue
          localCleanup.add(dest)
          add('remove-skill', `全局优先，清理当前项目重复入口：${name}（原真实目录先备份）`, [dest],
            () => removeSkillEntry({ dest, backupRoot: path.join(projectDir, '.dwy', 'skill-backups') }))
          if (nextProject.platforms[platform]) {
            nextProject.platforms[platform].skills = (nextProject.platforms[platform].skills || []).filter(item => item !== name)
            projectChanged = true
          }
        }
      }
    }
    if (neededSkills.size) {
      const skills = [...neededSkills.values()]
      const preserved = []
      if (refreshSkills && !global) {
        for (let i = 0; i < skills.length; i++) {
          const skill = skills[i], shared = path.join(homeDir, '.dwy', 'skills', skill.name)
          if (!await validSkill(shared)) continue
          for (const platform of ['claude', 'codex', 'opencode']) {
            if (!await findGlobalSkill({ name: skill.name, platform, homeDir, codexHome })) continue
            // 补项目入口不能间接刷新其他 CLI 正在使用的全局共享副本。
            skills[i] = { ...skill, sourcePath: shared }
            preserved.push(skill.name)
            break
          }
        }
      }
      const label = refreshSkills ? `更新所选共享 Skills（所有同名链接生效）${preserved.length ? `；保留全局共享内容：${preserved.join('、')}` : ''}`
        : '准备缺失的共享副本；已有内容不刷新'
      operations.unshift({ kind: 'ensure-skills', label,
        paths: [...skills.map(skill => path.join(homeDir, '.dwy', 'skills', skill.name)), path.join(homeDir, '.dwy', 'skill-store.json')],
        run: () => (refreshSkills ? prepareSharedSkills : ensureSharedSkills)({ skills, homeDir }) })
    }
  }

  const cliPlatforms = platforms.filter(platform => platform !== 'cursor')
  if (active.has('rules')) {
    const selectedNames = new Set(selected.rules.map(item => item.name))
    const rules = scans.rules.filter(rule => selectedNames.has(rule.name))
    const preserved = new Set(cliPlatforms.flatMap(platform => retained(platform, 'rules')))
    const removed = [...new Set(cliPlatforms.flatMap(platform => approved(platform, 'rules')))]
    if (cliPlatforms.length) {
      await addConfig('rules', `更新项目 Rules（保留通用规范和手写内容）${removed.length ? `；移除旧托管项：${removed.join('、')}` : ''}`, [path.join(projectDir, 'AGENTS.md')], projectDir,
        () => syncProjectAgentsMd(projectDir, rules, { preservedRuleNames: preserved }))
      const names = [...new Set([...rules.map(rule => rule.name), ...preserved])].sort()
      for (const platform of ['claude', 'codex', 'opencode']) {
        if (platforms.includes(platform) || nextProject.platforms[platform]) {
          nextProject.platforms[platform] ||= { skills: [], rules: [], hooks: [], commands: [] }
          nextProject.platforms[platform].rules = names
        }
      }
    }
    if (platforms.includes('cursor')) {
      const paths = rules.map(rule => path.join(projectDir, '.cursor', 'rules', cursorRuleName(rule.name)))
      const root = path.join(projectDir, '.cursor', 'rules')
      const managed = new Set([...scans.rules.map(rule => cursorRuleName(rule.name)), ...approved('cursor', 'rules').map(cursorRuleName), '00-dwy-global.mdc'])
      if (await fs.pathExists(root)) for (const name of await fs.readdir(root)) if (managed.has(name)) paths.push(path.join(root, name))
      add('rules', '同步 Cursor 项目 Rules', [...new Set(paths)], () => syncCursor({ sourceDir, projectDir, selected: { rules }, staleRemovals: staleRemovals.cursor }))
      platformState('cursor').rules = [...new Set([...rules.map(rule => rule.name), ...retained('cursor', 'rules')])].sort()
    }
    if (platforms.includes('claude')) {
      const names = new Set([...scans.rules.map(rule => rule.name), ...approved('claude', 'rules')])
      for (const name of names) {
        if (!scans.rules.some(rule => rule.name === name) && !(projectState.platforms.claude?.rules || []).includes(name)) continue
        const dest = path.join(projectDir, '.claude', 'rules', name)
        if (migratedRuleSources[name] && await existsEntry(dest)) {
          const reference = migratedRuleSources[name]
          if (!(await fs.lstat(dest)).isFile()) continue
          if (!await fs.pathExists(reference) || await fs.readFile(dest, 'utf8') !== await fs.readFile(reference, 'utf8')) continue
        }
        if (safeName(name) && await existsEntry(dest)) add('legacy-rule', '清理旧项目规则入口', [dest], () => fs.remove(dest))
      }
    }
  }
  if (active.has('baseline')) {
    const remove = contentActions.baseline === 'remove'
    const providers = global ? [] : await baselineProviders(cliPlatforms, { homeDir, codexHome })
    const inherited = providers.length > 0
    const markProject = enabled => {
      for (const platform of ['claude', 'codex', 'opencode']) {
        if ((!global && platforms.includes(platform)) || nextProject.platforms[platform]) {
          nextProject.platforms[platform] ||= { skills: [], rules: [], hooks: [], commands: [] }
          nextProject.platforms[platform].baseline = enabled
          if (global) projectChanged = true
        }
      }
    }
    const cleanBaseline = async (dest, boundary, label) => {
      if (!await fs.pathExists(dest)) return false
      const text = await fs.readFile(dest, 'utf8')
      if (!await hasManagedBaseline(dest) && (!baseline.trim() || text.trim() !== baseline.trim())) return false
      await addConfig('remove-baseline', label, [dest], boundary, () => text.trim() === baseline.trim()
        ? removeLegacyBaseline(baseline, dest) : syncBaselineDoc('', dest))
      return true
    }
    if (global) {
      for (const platform of cliPlatforms) {
        const dest = globalBaselinePath(platform, homeDir, codexHome)
        if (remove) await cleanBaseline(dest, platform === 'codex' ? codexHome : homeDir, `移除 ${PLATFORM_LABELS[platform]} 全局通用规范（保留 Rules 和手写内容）`)
        else await addConfig('baseline', `启用/更新 ${PLATFORM_LABELS[platform]} 全局通用规范（保留其他内容）`, [dest], platform === 'codex' ? codexHome : homeDir, () => syncBaselineDoc(baseline, dest))
        platformState(platform).baseline = !remove
      }
      if (platforms.includes('claude')) await cleanBaseline(path.join(homeDir, '.claude', 'AGENTS.md'), homeDir, '清理旧全局基线托管内容')
    } else {
      const dest = path.join(projectDir, 'AGENTS.md')
      if (remove || inherited) {
        await cleanBaseline(dest, projectDir, inherited ? '全局已启用，清理项目重复基线' : '移除项目通用规范（保留 Rules 和手写内容）')
        const missing = cliPlatforms.filter(platform => !providers.includes(platform))
        if (inherited) add('inherit', `通用规范使用全局：${providers.map(p => PLATFORM_LABELS[p]).join('、')}；项目禁止重复安装${missing.length ? `；${missing.map(p => PLATFORM_LABELS[p]).join('、')} 缺少全局规范，请另行选择全局范围补齐` : ''}`,
          providers.map(p => globalBaselinePath(p, homeDir, codexHome)), async () => {})
      } else await addConfig('baseline', '启用/更新项目 AGENTS.md 通用规范（保留 Rules 和手写内容）', [dest], projectDir, () => syncBaselineDoc(baseline, dest))
      markProject(!remove && !inherited)
    }
    if ((!global || !remove) && !isHome) {
      if (global && await cleanBaseline(path.join(projectDir, 'AGENTS.md'), projectDir, '全局优先，清理当前项目重复基线')) markProject(false)
      if (platforms.includes('claude')) {
        for (const name of ['AGENTS.md', 'CLAUDE.md']) {
          await cleanBaseline(path.join(projectDir, '.claude', name), projectDir, '清理旧项目基线托管内容')
        }
      }
    }
  }
  if (active.has('hooks')) {
    const manifests = await loadHookManifests(sourceDir)
    const remove = contentActions.hooks === 'remove'
    const removeHooks = async (platform, root, boundary, names, label) => {
      const paths = []
      for (const name of names) {
        const dest = path.join(root, 'hooks', name)
        if (await existsEntry(dest)) paths.push(dest)
      }
      if (await hasManagedHookConfig(platform, root, names)) paths.push(hookConfigFile(platform, root))
      if (!paths.length) return false
      await addConfig('remove-hooks', label, paths, boundary, () => removeManagedHooks(platform, root, names, paths))
      return true
    }
    for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('hooks'))) {
      const available = scans.hooks.filter(hook => manifests.some(manifest => manifest.name === hook.name && (!manifest.platforms || manifest.platforms.includes(platform))))
      const provided = !global && !remove ? await globalHookNames({ platform, sourceDir, homeDir, codexHome }) : new Set()
      const hooks = remove ? [] : available.filter(hook => !provided.has(hook.name))
      const root = global && platform === 'codex' ? codexHome : path.join(targetRoot, platform === 'claude' ? '.claude' : '.codex')
      const boundary = global && platform === 'codex' ? codexHome : targetRoot
      const historical = (targetState.platforms[platform]?.hooks || []).filter(safeName)
      const allManaged = new Set([...scans.hooks.map(hook => hook.name), ...(remove ? historical : []), ...approved(platform, 'hooks')])
      if (remove || hooks.length === 0) {
        await removeHooks(platform, root, boundary, allManaged, `${remove ? '移除' : '全局已启用，清理重复'} ${PLATFORM_LABELS[platform]} ${global ? '全局' : '项目'} 托管 Hooks`)
      } else {
        await assertHooksEnabled(platform, root)
        const paths = hooks.map(hook => path.join(root, 'hooks', hook.name))
        const selectedNames = new Set(hooks.map(hook => hook.name))
        const removedNames = []
        const hookDir = path.join(root, 'hooks')
        if (await fs.pathExists(hookDir)) {
          for (const name of await fs.readdir(hookDir)) {
            if (allManaged.has(name) && !selectedNames.has(name)) {
              paths.push(path.join(hookDir, name))
              removedNames.push(name)
            }
          }
        }
        paths.push(hookConfigFile(platform, root))
        const sync = platform === 'claude' ? syncClaude : syncCodex
        const cleanup = removedNames.length ? `；清理旧托管脚本：${removedNames.join('、')}` : ''
        await addConfig('hooks', `同步 ${PLATFORM_LABELS[platform]} ${global ? '全局' : '项目'} Hooks${cleanup}`, paths, boundary,
          () => sync({ sourceDir, projectDir: targetRoot, global, homeDir, codexHome, selected: { skills: [], hooks }, syncTypes: ['hooks'], staleRemovals: staleRemovals[platform] }))
      }
      if (provided.size) add('inherit', `${PLATFORM_LABELS[platform]} Hooks 使用全局：${[...provided].join('、')}；项目不重复安装`, [], async () => {})
      platformState(platform).hooks = remove ? [] : [...new Set([...hooks.map(hook => hook.name), ...retained(platform, 'hooks')])].sort()
      if (global && !remove && !isHome) {
        const local = path.join(projectDir, platform === 'claude' ? '.claude' : '.codex')
        const duplicates = new Set(available.map(hook => hook.name))
        if (await removeHooks(platform, local, projectDir, duplicates, `全局优先，清理当前项目 ${PLATFORM_LABELS[platform]} 重复 Hooks`)
          && nextProject.platforms[platform]) {
          nextProject.platforms[platform].hooks = (nextProject.platforms[platform].hooks || []).filter(name => !duplicates.has(name))
          projectChanged = true
        }
      }
    }
  }
  return { operations, nextProject, nextGlobal, projectChanged, globalChanged: global && contentTypes.length > 0 }
}
