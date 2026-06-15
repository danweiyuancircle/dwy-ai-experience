import fs from 'fs-extra'
import path from 'path'
import { chalk } from './utils.js'
import {
  copyFilter,
  logAction,
  resolveSourceDir,
  scanCommands,
  scanExisting,
  scanRules,
  scanSkills,
} from './sync.js'
import { syncProjectAgentsMd } from './sync-codex.js'

async function copyItemsTo(baseDir, typeDir, items) {
  const targetDir = path.join(baseDir, typeDir)
  let count = 0

  for (const item of items) {
    const dest = path.join(targetDir, item.name)
    await fs.ensureDir(path.dirname(dest))
    await fs.copy(item.sourcePath, dest, { overwrite: true, filter: copyFilter })
    logAction(`.opencode/${typeDir}/${item.name}`)
    count++
  }

  return count
}

async function removeUnselected(typeDir, existingNames, selectedNames, templateNames, projectDir) {
  const targetDir = path.join(projectDir, '.opencode', typeDir)
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

export async function syncOpenCode({
  sourceDir: sourceDirOverride,
  projectDir,
  selected,
  staleRemovals = {},
  preserveMissingRules = new Set(),
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const proj = projectDir || process.cwd()
  const openCodeDir = path.join(proj, '.opencode')
  await fs.ensureDir(openCodeDir)

  console.log(chalk.blue('\nSyncing OpenCode configuration...\n'))

  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: await scanCommands(sourceDir),
  }

  const selectedNames = key => new Set((selected[key] || []).map(item => item.name))
  const syncedSelection = {
    skills: scans.skills.filter(item => selectedNames('skills').has(item.name)),
    rules: scans.rules.filter(item => selectedNames('rules').has(item.name)),
    commands: scans.commands.filter(item => selectedNames('commands').has(item.name)),
  }

  const existing = {
    skills: await scanExisting(openCodeDir, 'skills'),
    commands: await scanExisting(openCodeDir, 'commands'),
  }

  let syncedCount = 0
  let removedCount = 0

  const agentsPath = path.join(proj, 'AGENTS.md')
  syncedCount += await syncProjectAgentsMd(sourceDir, proj, syncedSelection.rules, {
    preservedRuleNames: preserveMissingRules,
  })

  syncedCount += await copyItemsTo(openCodeDir, 'skills', syncedSelection.skills)
  syncedCount += await copyItemsTo(openCodeDir, 'commands', syncedSelection.commands)

  removedCount += await removeUnselected(
    'skills',
    existing.skills,
    new Set(syncedSelection.skills.map(item => item.name)),
    new Set([
      ...scans.skills.map(item => item.name),
      ...(staleRemovals.skills || new Set()),
    ]),
    proj,
  )
  removedCount += await removeUnselected(
    'commands',
    existing.commands,
    new Set(syncedSelection.commands.map(item => item.name)),
    new Set([
      ...scans.commands.map(item => item.name),
      ...(staleRemovals.commands || new Set()),
    ]),
    proj,
  )

  console.log(chalk.blue(`\nDone! ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Rules    → ${agentsPath}`))
  console.log(chalk.gray(`  Skills   → ${path.join(openCodeDir, 'skills')}`))
  console.log(chalk.gray(`  Commands → ${path.join(openCodeDir, 'commands')}`))
  console.log(chalk.gray('  Hooks    → 当前适配未支持'))
}
