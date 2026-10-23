import fs from 'fs-extra'
import path from 'path'
import { chalk } from './utils.js'
import {
  copyFilter,
  logAction,
  resolveSourceDir,
  scanExisting,
  scanSkills,
} from './sync.js'

async function copyItemsTo(baseDir, typeDir, items) {
  const targetDir = path.join(baseDir, typeDir)
  let count = 0

  for (const item of items) {
    const dest = path.join(targetDir, item.name)
    await fs.ensureDir(path.dirname(dest))
    await fs.copy(item.sourcePath, dest, { overwrite: true, filter: copyFilter(item.sourcePath) })
    logAction(`.opencode/${typeDir}/${item.name}`)
    count++
  }

  return count
}

async function removeUnselected(typeDir, existingNames, selectedNames, templateNames, baseDir) {
  const targetDir = path.join(baseDir, typeDir)
  let count = 0

  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    if (!templateNames.has(name)) continue
    await fs.remove(path.join(targetDir, name))
    logAction(`.opencode/${typeDir}/${name}`, 'red', '×')
    count++
  }

  return count
}

/** 同步 OpenCode 技能；基线和项目 Rules 由总同步入口分别处理。 */
export async function syncOpenCode({
  sourceDir: sourceDirOverride,
  projectDir,
  global = false,
  selected,
  staleRemovals = {},
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const proj = projectDir || process.cwd()
  const openCodeDir = global ? path.join(proj, '.config', 'opencode') : path.join(proj, '.opencode')
  await fs.ensureDir(openCodeDir)

  console.log(chalk.blue('\nSyncing OpenCode configuration...\n'))

  const scans = {
    skills: await scanSkills(sourceDir),
  }

  const selectedNames = key => new Set((selected[key] || []).map(item => item.name))
  const syncedSelection = {
    skills: scans.skills.filter(item => selectedNames('skills').has(item.name)),
  }

  const existing = {
    skills: await scanExisting(openCodeDir, 'skills'),
  }

  let syncedCount = 0
  let removedCount = 0

  syncedCount += await copyItemsTo(openCodeDir, 'skills', syncedSelection.skills)

  removedCount += await removeUnselected(
    'skills',
    existing.skills,
    new Set(syncedSelection.skills.map(item => item.name)),
    new Set([
      ...scans.skills.map(item => item.name),
      ...(staleRemovals.skills || new Set()),
    ]),
    openCodeDir,
  )
  console.log(chalk.blue(`\nDone! ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Skills   → ${path.join(openCodeDir, 'skills')}`))
  console.log(chalk.gray('  Hooks    → 当前适配未支持'))
}
