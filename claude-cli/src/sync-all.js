import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import { chalk } from './utils.js'
import {
  interactiveSelect,
  resolveSourceDir,
  scanCommands,
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

function unionSets(...sets) {
  return new Set(sets.flatMap(set => [...set]))
}

function selectFromExisting(scans, existing) {
  return {
    skills: scans.skills.filter(item => existing.skills.has(item.name)),
    rules: scans.rules.filter(item => existing.rules.has(item.name)),
    commands: scans.commands.filter(item => existing.commands.has(item.name)),
    hooks: existing.hooks.size > 0
      ? scans.hooks.filter(item => existing.hooks.has(item.name))
      : scans.hooks,
  }
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
  const hasAnyExisting = existing.skills.size + existing.rules.size + existing.commands.size + existing.hooks.size > 0
  if (hasAnyExisting) return true

  const hasConfigDir = await fs.pathExists(path.join(projectDir, '.claude'))
    || await fs.pathExists(path.join(projectDir, '.codex'))
    || await fs.pathExists(path.join(projectDir, '.agents'))

  if (hasConfigDir) return true

  const { ok } = await inquirer.prompt([{
    type: 'confirm',
    name: 'ok',
    message: `当前目录 ${chalk.yellow(projectDir)} 尚无 Claude Code/Codex 配置，是否在此初始化？`,
    default: false,
  }])
  return ok
}

export async function syncAll({
  target,
  reselect = false,
  dryRun = false,
  sourceDir: sourceDirOverride,
  projectDir: projectDirOverride,
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  if (target === 'md') {
    await syncClaude({ target, dryRun, sourceDir })
    await syncCodex({ target, dryRun, sourceDir })
    return
  }

  if (target !== undefined) {
    console.error(chalk.red(`Error: unknown sync target "${target}". Supported: (none) | md`))
    process.exit(2)
  }

  const projectDir = projectDirOverride || process.cwd()

  console.log(chalk.blue('\nScanning available Claude Code/Codex configuration...\n'))
  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: await scanCommands(sourceDir),
    hooks: await scanHooks(sourceDir),
  }
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.rules.length} rules, ${scans.commands.length} commands, ${scans.hooks.length} hooks\n`))

  const existing = await scanCombinedExisting(projectDir)
  if (!await shouldInitialize(projectDir, existing)) {
    console.log(chalk.yellow('\n已取消同步。'))
    return
  }

  const hasAnyExisting = existing.skills.size + existing.rules.size + existing.commands.size + existing.hooks.size > 0
  let selected
  if (!reselect && hasAnyExisting) {
    selected = selectFromExisting(scans, existing)
    console.log(chalk.gray('使用已选覆盖同步（如需调整请加 -i / --reselect）：'))
    console.log(chalk.gray(`  ${selected.skills.length} skills, ${selected.rules.length} rules, ${selected.commands.length} commands, ${selected.hooks.length} hooks\n`))
  } else {
    if (!reselect && !hasAnyExisting) console.log(chalk.gray('首次同步，进入交互式选择...\n'))
    const result = await interactiveSelect(scans, existing)
    if (result === null) {
      console.log(chalk.yellow('\n已取消同步。'))
      return
    }
    selected = result
  }

  console.log(chalk.blue('\nSyncing Claude Code configuration...\n'))
  await syncClaude({
    sourceDir,
    projectDir,
    selected,
    reselect,
    dryRun,
    skipInitPrompt: true,
  })

  console.log(chalk.blue('\nSyncing Codex configuration...\n'))
  await syncCodex({
    sourceDir,
    projectDir,
    selected,
    reselect,
    dryRun,
    skipInitPrompt: true,
  })
}
