import fs from 'fs-extra'
import path from 'node:path'
import { ensureSharedSkills, linkSkill, removeSkillEntry } from './skill-store.js'
import { findGlobalSkill, globalSkillRoots, resolveGlobalSkillDir, resolveProjectSkillDir } from './sync-global-skills.js'
import { loadHookManifests, syncClaude } from './sync.js'
import { removeLegacyBaseline, syncCodex, syncGlobalBaselineDoc, syncProjectAgentsMd } from './sync-codex.js'
import { syncCursor } from './sync-cursor.js'
import { planMissingExternalSkills } from './skills-install.js'

/** 平台显示名，交互和变更清单共用。 */
export const PLATFORM_LABELS = { claude: 'Claude Code', codex: 'Codex', opencode: 'OpenCode', cursor: 'Cursor' }
/** 项目范围的平台能力；全局范围用通用规范替代项目 Rules，且不支持 Cursor。 */
export const PLATFORM_SYNC_TYPES = {
  claude: ['skills', 'rules', 'hooks'], codex: ['skills', 'rules', 'hooks'],
  opencode: ['skills', 'rules'], cursor: ['rules'],
}

/** 只提供所选范围和平台支持的内容；未勾选类型不进入清理或状态更新。 */
export function contentOptions(scope, platforms) {
  const supports = type => platforms.some(platform => PLATFORM_SYNC_TYPES[platform]?.includes(type))
  return [
    ...(supports('skills') ? [{ value: 'skills', label: 'Skills', description: '管理当前范围的启用入口；已有共享内容不刷新' }] : []),
    ...(scope === 'project' && supports('rules') ? [{ value: 'rules', label: '项目规则（Rules）', description: '只更新当前项目的托管规则' }] : []),
    ...(scope === 'global' ? [{ value: 'baseline', label: '全局通用规范', description: '更新所选工具的原生全局指令入口，不修改项目规则' }] : []),
    ...(supports('hooks') ? [{ value: 'hooks', label: 'Hooks（按平台自动同步）', description: '仅选择此类型后，自动同步所选平台支持的 Hooks' }] : []),
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
    return { ...skill, disabled, label: status ? `${skill.name}（${status}）` : skill.name,
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
 * Skills 的入口与内容刷新分离；项目去重只删除项目入口，不改写全局提供者。
 */
export async function buildSyncPlan({
  scope, platforms, contentTypes, selected, scans, sourceDir, projectDir, homeDir, codexHome,
  projectState, globalState, staleRemovals = {}, staleEntries = {}, baseline,
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
  if (active.has('baseline') && !baseline.trim()) throw new Error('没有可同步的全局通用规范')
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
  const add = (kind, label, paths, run) => operations.push({ kind, label, paths, run })
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
      operations.unshift({ kind: 'ensure-skills', label: '准备缺失的共享副本；已有内容不刷新',
        paths: [...skills.map(skill => path.join(homeDir, '.dwy', 'skills', skill.name)), path.join(homeDir, '.dwy', 'skill-store.json')],
        run: () => ensureSharedSkills({ skills, homeDir }) })
    }
    if ([...neededSkills.values()].some(skill => skill.category === '产品0到1')) {
      const target = path.join(process.env.DWY_HOME || path.join(homeDir, '.dwy'), 'skills')
      const external = await planMissingExternalSkills(target)
      if (external.paths.length) add('external-skills', '补齐产品流程外部 Skills（联网拉取固定版本，保留已有内容）', external.paths, external.run)
    }
  }

  const cliPlatforms = platforms.filter(platform => platform !== 'cursor')
  if (active.has('rules')) {
    const selectedNames = new Set(selected.rules.map(item => item.name))
    const rules = scans.rules.filter(rule => selectedNames.has(rule.name))
    const preserved = new Set(cliPlatforms.flatMap(platform => retained(platform, 'rules')))
    if (cliPlatforms.length) {
      add('rules', '更新项目 Rules（保留手写内容）', [path.join(projectDir, 'AGENTS.md')],
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
        const dest = path.join(projectDir, '.claude', 'rules', name)
        if (safeName(name) && await existsEntry(dest)) add('legacy-rule', '清理旧项目规则入口', [dest], () => fs.remove(dest))
      }
      for (const name of ['AGENTS.md', 'CLAUDE.md']) {
        const dest = path.join(projectDir, '.claude', name)
        if (await fs.pathExists(dest)) {
          const text = await fs.readFile(dest, 'utf8')
          if (text.trim() === baseline.trim() || /<!-- DWY-BASELINE:START[\s\S]*?DWY-BASELINE:END -->/.test(text)) {
            add('legacy-baseline', '清理旧项目基线托管内容', [dest], () => removeLegacyBaseline(baseline, dest))
          }
        }
      }
    }
  }
  if (active.has('baseline')) {
    const paths = { claude: path.join(homeDir, '.claude', 'CLAUDE.md'), codex: path.join(codexHome, 'AGENTS.md'), opencode: path.join(homeDir, '.config', 'opencode', 'AGENTS.md') }
    for (const platform of cliPlatforms) {
      const dest = paths[platform]
      add('baseline', `更新 ${PLATFORM_LABELS[platform]} 全局通用规范（保留手写内容）`, [dest], () => syncGlobalBaselineDoc(baseline, dest))
      platformState(platform).rules = []
    }
    if (platforms.includes('claude')) {
      const dest = path.join(homeDir, '.claude', 'AGENTS.md')
      if (await fs.pathExists(dest)) {
        const text = await fs.readFile(dest, 'utf8')
        if (text.trim() === baseline.trim() || /<!-- DWY-BASELINE:START[\s\S]*?DWY-BASELINE:END -->/.test(text)) {
          add('legacy-baseline', '清理旧全局基线托管内容', [dest], () => removeLegacyBaseline(baseline, dest))
        }
      }
    }
  }
  if (active.has('hooks')) {
    const manifests = await loadHookManifests(sourceDir)
    for (const platform of platforms.filter(p => PLATFORM_SYNC_TYPES[p].includes('hooks'))) {
      const hooks = scans.hooks.filter(hook => manifests.some(manifest => manifest.name === hook.name && (!manifest.platforms || manifest.platforms.includes(platform))))
      const root = global && platform === 'codex' ? codexHome : path.join(targetRoot, platform === 'claude' ? '.claude' : '.codex')
      const paths = hooks.map(hook => path.join(root, 'hooks', hook.name))
      const selectedNames = new Set(hooks.map(hook => hook.name))
      const managedNames = new Set([...scans.hooks.map(hook => hook.name), ...approved(platform, 'hooks')])
      const removedNames = []
      const hookDir = path.join(root, 'hooks')
      if (await fs.pathExists(hookDir)) {
        for (const name of await fs.readdir(hookDir)) {
          if (managedNames.has(name) && !selectedNames.has(name)) {
            paths.push(path.join(hookDir, name))
            removedNames.push(name)
          }
        }
      }
      paths.push(path.join(root, platform === 'claude' ? 'settings.json' : 'hooks.json'))
      const sync = platform === 'claude' ? syncClaude : syncCodex
      const cleanup = removedNames.length ? `；清理旧托管脚本：${removedNames.join('、')}` : ''
      add('hooks', `同步 ${PLATFORM_LABELS[platform]} ${global ? '全局' : '项目'} Hooks${cleanup}`, paths,
        () => sync({ sourceDir, projectDir: targetRoot, global, homeDir, codexHome, selected: { skills: [], hooks }, syncTypes: ['hooks'], staleRemovals: staleRemovals[platform] }))
      platformState(platform).hooks = [...new Set([...hooks.map(hook => hook.name), ...retained(platform, 'hooks')])].sort()
    }
  }
  return { operations, nextProject, nextGlobal, projectChanged, globalChanged: global && contentTypes.length > 0 }
}
