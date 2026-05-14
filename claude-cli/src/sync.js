import fs from 'fs-extra'
import path from 'path'
import os from 'os'
import inquirer from 'inquirer'
import { ensureRepoCache, chalk } from './utils.js'

function extractDescription(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return ''
  const frontmatter = match[1]
  const descMatch = frontmatter.match(/description:\s*(.+)/)
  return descMatch ? descMatch[1].trim().replace(/^["']|["']$/g, '') : ''
}

async function scanSkills(sourceDir) {
  const skillsDir = path.join(sourceDir, 'skills')
  if (!await fs.pathExists(skillsDir)) return []

  const entries = await fs.readdir(skillsDir, { withFileTypes: true })
  const skills = []

  for (const entry of entries) {
    if (!entry.isDirectory()) continue
    const skillPath = path.join(skillsDir, entry.name)
    const skillMd = path.join(skillPath, 'SKILL.md')
    if (!await fs.pathExists(skillMd)) continue

    const content = await fs.readFile(skillMd, 'utf-8')
    const description = extractDescription(content)
    skills.push({
      name: entry.name,
      description: description || '（无描述）',
      sourcePath: skillPath,
      type: 'skill',
    })
  }

  return skills.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanRules(sourceDir) {
  const rulesDir = path.join(sourceDir, 'rules')
  if (!await fs.pathExists(rulesDir)) return []

  const entries = await fs.readdir(rulesDir, { withFileTypes: true })
  const rules = []

  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith('.md')) continue
    const rulePath = path.join(rulesDir, entry.name)
    const content = await fs.readFile(rulePath, 'utf-8')
    const description = extractDescription(content)
    rules.push({
      name: entry.name,
      description: description || '（无描述）',
      sourcePath: rulePath,
      type: 'rule',
    })
  }

  return rules.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanCommands(sourceDir) {
  const commandsDir = path.join(sourceDir, 'commands')
  if (!await fs.pathExists(commandsDir)) return []

  const entries = await fs.readdir(commandsDir, { withFileTypes: true })
  const commands = []

  for (const entry of entries) {
    if (entry.name === '.gitkeep') continue
    commands.push({
      name: entry.name,
      description: entry.isDirectory() ? '命令目录' : '命令文件',
      sourcePath: path.join(commandsDir, entry.name),
      type: 'command',
    })
  }

  return commands.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanHooks(sourceDir) {
  const hooksDir = path.join(sourceDir, 'hooks')
  if (!await fs.pathExists(hooksDir)) return []

  const entries = await fs.readdir(hooksDir, { withFileTypes: true })
  const hooks = []

  for (const entry of entries) {
    if (entry.name === '.gitkeep') continue
    hooks.push({
      name: entry.name,
      description: entry.isDirectory() ? '钩子目录' : '钩子脚本',
      sourcePath: path.join(hooksDir, entry.name),
      type: 'hook',
    })
  }

  return hooks.sort((a, b) => a.name.localeCompare(b.name))
}

async function promptSelection(items, category, existingNames = new Set()) {
  if (items.length === 0) return []

  const { selected } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'selected',
      message: `选择要同步的 ${category}（空格勾选，回车确认）：`,
      choices: items.map(item => ({
        name: `${chalk.cyan(item.name)} ${chalk.gray('- ' + item.description.slice(0, 60))}${item.description.length > 60 ? '...' : ''}`,
        value: item,
        short: item.name,
        checked: existingNames.has(item.name),
      })),
      pageSize: 15,
    },
  ])

  return selected
}

async function scanExisting(projectTargetDir, typePlural) {
  const dir = path.join(projectTargetDir, typePlural)
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir)
  return new Set(entries.filter(name => name !== '.gitkeep' && name !== '.DS_Store'))
}

function logAction(dryRun, label) {
  console.log(chalk.green(`  ${dryRun ? '[dry-run] ' : '✓ '}${label}`))
}

async function syncSelectedItems(items, targetDir, dryRun) {
  for (const item of items) {
    const dest = path.join(targetDir, item.type + 's', item.name)
    if (!dryRun) {
      await fs.ensureDir(path.dirname(dest))
      await fs.copy(item.sourcePath, dest, { overwrite: true })
    }
    logAction(dryRun, `${item.type}s/${item.name}`)
  }
  return items.length
}

async function syncSettings(sourceDir, targetDir, dryRun) {
  const settingsSrc = path.join(sourceDir, 'settings.json')
  if (!await fs.pathExists(settingsSrc)) return 0

  const settingsDest = path.join(targetDir, 'settings.json')
  const newSettings = await fs.readJson(settingsSrc)

  let merged
  let action
  if (await fs.pathExists(settingsDest)) {
    const existing = await fs.readJson(settingsDest)
    merged = { ...existing }
    for (const [key, value] of Object.entries(newSettings)) {
      if (key in merged && typeof merged[key] === 'object' && !Array.isArray(merged[key])
          && typeof value === 'object' && !Array.isArray(value)) {
        merged[key] = { ...merged[key], ...value }
      } else {
        merged[key] = value
      }
    }
    action = 'merged'
  } else {
    merged = newSettings
    action = 'created'
  }

  if (!dryRun) await fs.writeJson(settingsDest, merged, { spaces: 2 })
  logAction(dryRun, `settings.json — ${action}`)
  return 1
}

async function syncClaudeMd(sourceDir, targetDir, dryRun) {
  const claudeMdSrc = path.join(sourceDir, 'CLAUDE.md')
  if (!await fs.pathExists(claudeMdSrc)) return 0

  if (!dryRun) await fs.copy(claudeMdSrc, path.join(targetDir, 'CLAUDE.md'), { overwrite: true })
  logAction(dryRun, 'CLAUDE.md')
  return 1
}

async function syncHooks(items, targetDir, dryRun) {
  if (items.length === 0) return 0
  const hooksTargetDir = path.join(targetDir, 'hooks')
  if (!dryRun) await fs.ensureDir(hooksTargetDir)
  for (const hook of items) {
    const dest = path.join(hooksTargetDir, hook.name)
    if (!dryRun) {
      await fs.copy(hook.sourcePath, dest, { overwrite: true })
      await fs.chmod(dest, 0o755)
    }
    logAction(dryRun, `hooks/${hook.name}`)
  }
  return items.length
}

async function resolveSourceDir() {
  const localTemplate = path.join(process.cwd(), 'claude-cli', 'templates', 'claude-global')
  if (await fs.pathExists(localTemplate)) {
    console.log(chalk.gray('Using local templates from current project...'))
    return localTemplate
  }
  const repoDir = await ensureRepoCache()
  return path.join(repoDir, 'claude-cli', 'templates', 'claude-global')
}

/**
 * 入口：`dwy claude sync [target]`
 *   target=undefined  全量同步：项目 .claude/ + 全局 CLAUDE.md
 *   target='md'       仅同步 CLAUDE.md → 全局 ~/.claude/
 */
export async function syncClaude({ target, reselect = false, dryRun = false } = {}) {
  const sourceDir = await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  const globalTargetDir = path.join(os.homedir(), '.claude')

  if (target === 'md') {
    if (!dryRun) await fs.ensureDir(globalTargetDir)
    console.log(chalk.blue(`\nSyncing CLAUDE.md to ${globalTargetDir}...\n`))
    const synced = await syncClaudeMd(sourceDir, globalTargetDir, dryRun)
    if (!synced) {
      console.log(chalk.yellow('CLAUDE.md not found in templates, nothing to sync.'))
    } else {
      console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done.'}`))
    }
    return
  }

  if (target !== undefined) {
    console.error(chalk.red(`Error: unknown sync target "${target}". Supported: (none) | md`))
    process.exit(2)
  }

  console.log(chalk.blue('\nScanning available Claude configuration...\n'))
  const projectTargetDir = path.join(process.cwd(), '.claude')

  if (!await fs.pathExists(projectTargetDir)) {
    const { shouldCreate } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'shouldCreate',
        message: `当前目录 ${chalk.yellow(process.cwd())} 未找到 .claude 目录，是否在此创建？`,
        default: false,
      },
    ])
    if (!shouldCreate) {
      console.log(chalk.yellow('\n已取消同步。'))
      return
    }
  }

  const skills = await scanSkills(sourceDir)
  const rules = await scanRules(sourceDir)
  const commands = await scanCommands(sourceDir)
  const hooks = await scanHooks(sourceDir)

  console.log(chalk.yellow(`Found ${skills.length} skills, ${rules.length} rules, ${commands.length} commands, ${hooks.length} hooks\n`))

  const existingSkills = await scanExisting(projectTargetDir, 'skills')
  const existingRules = await scanExisting(projectTargetDir, 'rules')
  const existingCommands = await scanExisting(projectTargetDir, 'commands')
  const existingHooks = await scanExisting(projectTargetDir, 'hooks')
  const hasAnyExisting = existingSkills.size + existingRules.size + existingCommands.size + existingHooks.size > 0

  let selectedSkills, selectedRules, selectedCommands, selectedHooks

  if (!reselect && hasAnyExisting) {
    selectedSkills = skills.filter(s => existingSkills.has(s.name))
    selectedRules = rules.filter(r => existingRules.has(r.name))
    selectedCommands = commands.filter(c => existingCommands.has(c.name))
    // hooks 与 settings.json 引用配套：未装过则装全部模板，已装过则按已选覆盖
    selectedHooks = existingHooks.size > 0
      ? hooks.filter(h => existingHooks.has(h.name))
      : hooks
    console.log(chalk.gray(`使用已选覆盖同步（如需调整请加 -i / --reselect）：`))
    console.log(chalk.gray(`  ${selectedSkills.length} skills, ${selectedRules.length} rules, ${selectedCommands.length} commands, ${selectedHooks.length} hooks\n`))
  } else {
    if (!reselect && !hasAnyExisting) {
      console.log(chalk.gray('首次同步，进入交互式选择...\n'))
    }
    selectedSkills = await promptSelection(skills, 'Skills', existingSkills)
    selectedRules = await promptSelection(rules, 'Rules', existingRules)
    selectedCommands = await promptSelection(commands, 'Commands', existingCommands)
    selectedHooks = await promptSelection(hooks, 'Hooks', existingHooks)
  }

  console.log(chalk.blue(`\n${dryRun ? '[dry-run] ' : ''}Syncing to ${projectTargetDir}...\n`))

  if (!dryRun) await fs.ensureDir(projectTargetDir)

  let syncedCount = 0
  syncedCount += await syncSelectedItems(selectedSkills, projectTargetDir, dryRun)
  syncedCount += await syncSelectedItems(selectedRules, projectTargetDir, dryRun)
  syncedCount += await syncSelectedItems(selectedCommands, projectTargetDir, dryRun)
  syncedCount += await syncSettings(sourceDir, projectTargetDir, dryRun)
  syncedCount += await syncHooks(selectedHooks, projectTargetDir, dryRun)

  if (!dryRun) await fs.ensureDir(globalTargetDir)
  syncedCount += await syncClaudeMd(sourceDir, globalTargetDir, dryRun)

  console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done!'} ${syncedCount} items.`))
  console.log(chalk.gray(`  Project config → ${projectTargetDir}`))
  console.log(chalk.gray(`  Hooks          → ${path.join(projectTargetDir, 'hooks')}`))
  console.log(chalk.gray(`  CLAUDE.md      → ${globalTargetDir}`))
}
