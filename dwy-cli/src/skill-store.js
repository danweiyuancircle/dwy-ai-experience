import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { randomUUID } from 'node:crypto'
import { copyFilter, resolveSourceDir, scanSkills } from './sync.js'
import { chalk } from './utils.js'

function validateName(name) {
  if (!/^[\p{L}\p{N}_-]+$/u.test(name)) throw new Error(`无效 Skill 名称：${name}`)
}

async function readInstalledNames(homeDir) {
  const file = path.join(homeDir, '.dwy', 'skill-store.json')
  if (!await fs.pathExists(file)) return []
  const names = await fs.readJson(file)
  if (!Array.isArray(names) || names.some(name => typeof name !== 'string')) {
    throw new Error(`共享 Skills 清单格式无效：${file}`)
  }
  names.forEach(validateName)
  return names
}

/**
 * 将包内 Skills 准备到稳定用户目录，返回指向共享副本的条目。
 * 同一用户的刷新互斥；完整副本准备失败时不替换旧内容。外部 Skills 缓存不纳入本模块清单。
 */
export async function prepareSharedSkills({ skills, homeDir = os.homedir() }) {
  if (skills.length === 0) return []
  for (const skill of skills) {
    validateName(skill.name)
    if (!(await fs.stat(path.join(skill.sourcePath, 'SKILL.md'))).isFile()) {
      throw new Error(`Skill 缺少有效 SKILL.md：${skill.sourcePath}`)
    }
  }
  const root = path.join(homeDir, '.dwy')
  const store = path.join(root, 'skills')
  await fs.ensureDir(store)
  const lockPath = path.join(root, 'skill-store.lock')
  let lock
  try {
    lock = await fs.open(lockPath, 'wx')
  } catch (error) {
    if (error.code === 'EEXIST') throw new Error(`另一个进程正在刷新 Skills；若前次异常退出，请移除 ${lockPath} 后重试`)
    throw error
  }
  let staging
  let preserveStaging = false
  try {
    staging = await fs.mkdtemp(path.join(root, '.skills-'))
    const installed = new Set(await readInstalledNames(homeDir))
    const prepared = []
    const replacements = []
    for (const skill of skills) {
      const dest = path.join(store, skill.name)
      const next = path.join(staging, skill.name)
      if (path.resolve(skill.sourcePath) !== path.resolve(dest)) {
        await fs.copy(skill.sourcePath, next, { dereference: true, filter: copyFilter(skill.sourcePath) })
        replacements.push({ dest, next, old: path.join(staging, `${skill.name}.old`), saved: false, replaced: false })
      }
      installed.add(skill.name)
      prepared.push({ ...skill, sourcePath: dest })
    }
    const manifest = path.join(staging, 'skill-store.json')
    await fs.writeJson(manifest, [...installed].sort(), { spaces: 2 })
    try {
      for (const entry of replacements) {
        const existing = await fs.lstat(entry.dest).catch(error => {
          if (error.code === 'ENOENT') return null
          throw error
        })
        if (existing) {
          await fs.rename(entry.dest, entry.old)
          entry.saved = true
        }
        await fs.rename(entry.next, entry.dest)
        entry.replaced = true
      }
      await fs.rename(manifest, path.join(root, 'skill-store.json'))
    } catch (error) {
      const errors = [error]
      for (const entry of [...replacements].reverse()) {
        try {
          if (entry.replaced) await fs.remove(entry.dest)
          if (entry.saved) await fs.rename(entry.old, entry.dest)
        } catch (restoreError) {
          errors.push(restoreError)
        }
      }
      if (errors.length > 1) {
        preserveStaging = true
        throw new AggregateError(errors, `刷新失败且自动恢复未完成，旧副本保留在 ${staging}`)
      }
      throw error
    }
    return prepared
  } finally {
    try {
      if (staging && !preserveStaging) await fs.remove(staging)
    } finally {
      await fs.close(lock)
      await fs.remove(lockPath)
    }
  }
}

async function entryParent(dest, backupRoot) {
  const parent = await fs.realpath(path.dirname(dest))
  const boundary = path.resolve(backupRoot, '..', '..')
  const realBoundary = await fs.realpath(boundary)
  const expected = path.join(realBoundary, path.relative(boundary, path.dirname(dest)))
  if (parent !== expected) throw new Error(`Skills 根目录链接指向外部位置，保留原入口，不修改目标：${path.dirname(dest)}`)
  return parent
}

/**
 * 清理托管入口：真实目录移到备份根，软链接仅移除入口，不遍历其目标。
 * 返回真实目录的备份路径；入口不存在或原为链接时返回 null。
 */
export async function removeSkillEntry({ dest, backupRoot }) {
  const stat = await fs.lstat(dest).catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (!stat) return null
  await entryParent(dest, backupRoot)
  if (stat.isSymbolicLink()) {
    await fs.unlink(dest)
    return null
  }
  await fs.ensureDir(backupRoot)
  const backup = path.join(backupRoot, `${path.basename(dest)}-${randomUUID()}`)
  await fs.rename(dest, backup)
  console.log(chalk.gray(`已备份 ${dest} → ${backup}`))
  return backup
}

/** 将整个 Skill 目录链接到共享副本；原真实目录先备份，链接失败时恢复原入口。 */
export async function linkSkill({ skill, dest, backupRoot }) {
  if (!(await fs.stat(path.join(skill.sourcePath, 'SKILL.md'))).isFile()) {
    throw new Error(`Skill 缺少有效 SKILL.md：${skill.sourcePath}`)
  }
  await fs.ensureDir(path.dirname(dest))
  const actualParent = await fs.realpath(path.dirname(dest))
  // 整个全局 skills 根可能已链接到共享目录；此时入口就是源目录，不能把它再改为自链。
  if (path.join(actualParent, path.basename(dest)) === await fs.realpath(skill.sourcePath)) return null
  await entryParent(dest, backupRoot)
  const stat = await fs.lstat(dest).catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  const previousLink = stat?.isSymbolicLink() ? await fs.readlink(dest) : null
  if (previousLink && path.resolve(path.dirname(dest), previousLink) === path.resolve(skill.sourcePath)) return null
  const temporary = path.join(path.dirname(dest), `.${path.basename(dest)}.link-${randomUUID()}`)
  await fs.symlink(path.resolve(skill.sourcePath), temporary, process.platform === 'win32' ? 'junction' : 'dir')
  let backup
  try {
    backup = await removeSkillEntry({ dest, backupRoot })
    try {
      await fs.rename(temporary, dest)
    } catch (error) {
      if (backup) await fs.rename(backup, dest)
      else if (previousLink) await fs.symlink(previousLink, dest, process.platform === 'win32' ? 'junction' : 'dir')
      throw error
    }
    return backup
  } finally {
    await fs.remove(temporary)
  }
}

/** 使用当前 CLI 包内模板刷新已有共享副本；新包移除的条目保留，避免其他项目坏链。 */
export async function refreshSharedSkills({ sourceDir, homeDir = os.homedir() } = {}) {
  const names = await readInstalledNames(homeDir)
  const scans = await scanSkills(sourceDir || await resolveSourceDir())
  const available = new Map(scans.map(skill => [skill.name, skill]))
  const updated = names.filter(name => available.has(name))
  const retained = names.filter(name => !available.has(name))
  await prepareSharedSkills({ skills: updated.map(name => available.get(name)), homeDir })
  for (const name of retained) console.log(chalk.yellow(`当前 CLI 已移除 ${name}，保留共享旧副本以免其他项目链接失效。`))
  console.log(chalk.green(`已刷新 ${updated.length} 个共享 Skills，保留 ${retained.length} 个旧副本。`))
  return { updated, retained }
}
