import fs from 'fs-extra'
import path from 'path'
import os from 'os'
import inquirer from 'inquirer'
import { ensureRepoCache, copyDir, chalk, PACKAGE_ROOT } from './utils.js'

/**
 * 从 YAML frontmatter 中提取 description 字段
 */
function extractDescription(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return ''
  const frontmatter = match[1]
  const descMatch = frontmatter.match(/description:\s*(.+)/)
  return descMatch ? descMatch[1].trim().replace(/^["']|["']$/g, '') : ''
}

/**
 * 扫描 skills 目录，返回 { name, description, sourcePath } 列表
 */
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

/**
 * 扫描 rules 目录，返回 { name, description, sourcePath } 列表
 */
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

/**
 * 扫描 commands 目录
 */
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

/**
 * 用 inquirer 做交互式多选
 */
async function promptSelection(items, category) {
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
      })),
      pageSize: 15,
    },
  ])

  return selected
}

/**
 * 同步选中的文件到目标目录
 */
async function syncSelectedItems(items, targetDir) {
  let syncedCount = 0

  for (const item of items) {
    const dest = path.join(targetDir, item.type + 's', item.name)
    await fs.ensureDir(path.dirname(dest))
    await fs.copy(item.sourcePath, dest, { overwrite: true })
    syncedCount++
    console.log(chalk.green(`  ✓ ${item.type}s/${item.name}`))
  }

  return syncedCount
}

/**
 * 同步 settings.json（智能合并）
 */
async function syncSettings(sourceDir, targetDir) {
  const settingsSrc = path.join(sourceDir, 'settings.json')
  if (!await fs.pathExists(settingsSrc)) return 0

  const settingsDest = path.join(targetDir, 'settings.json')
  const newSettings = await fs.readJson(settingsSrc)

  if (await fs.pathExists(settingsDest)) {
    const existing = await fs.readJson(settingsDest)
    const merged = { ...existing }
    for (const [key, value] of Object.entries(newSettings)) {
      if (key in merged && typeof merged[key] === 'object' && !Array.isArray(merged[key])
          && typeof value === 'object' && !Array.isArray(value)) {
        merged[key] = { ...merged[key], ...value }
      } else {
        merged[key] = value
      }
    }
    await fs.writeJson(settingsDest, merged, { spaces: 2 })
    console.log(chalk.green('  ✓ settings.json — merged'))
  } else {
    await fs.writeJson(settingsDest, newSettings, { spaces: 2 })
    console.log(chalk.green('  ✓ settings.json — created'))
  }

  return 1
}

/**
 * 同步 CLAUDE.md
 */
async function syncClaudeMd(sourceDir, targetDir) {
  const claudeMdSrc = path.join(sourceDir, 'CLAUDE.md')
  if (!await fs.pathExists(claudeMdSrc)) return 0

  await fs.copy(claudeMdSrc, path.join(targetDir, 'CLAUDE.md'), { overwrite: true })
  console.log(chalk.green('  ✓ CLAUDE.md'))
  return 1
}

/**
 * 检测本地模板目录：如果当前是 dwy-shared monorepo，直接用本地模板
 */
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
 * 主同步函数：交互式选择 + 同步到当前目录 .claude/（不含 CLAUDE.md）
 * CLAUDE.md 同步到全局 ~/.claude/
 */
export async function syncClaude() {
  console.log(chalk.blue('\nScanning available Claude configuration...\n'))

  const sourceDir = await resolveSourceDir()
  const projectTargetDir = path.join(process.cwd(), '.claude')
  const globalTargetDir = path.join(os.homedir(), '.claude')

  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  // 如果当前目录没有 .claude，先确认是否在此创建
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

  // 扫描可用资源
  const skills = await scanSkills(sourceDir)
  const rules = await scanRules(sourceDir)
  const commands = await scanCommands(sourceDir)

  console.log(chalk.yellow(`Found ${skills.length} skills, ${rules.length} rules, ${commands.length} commands\n`))

  // 交互式选择
  const selectedSkills = await promptSelection(skills, 'Skills')
  const selectedRules = await promptSelection(rules, 'Rules')
  const selectedCommands = await promptSelection(commands, 'Commands')

  const totalSelected = selectedSkills.length + selectedRules.length + selectedCommands.length
  if (totalSelected === 0) {
    console.log(chalk.yellow('\nNo skills/rules/commands selected.'))
  }

  console.log(chalk.blue(`\nSyncing to ${projectTargetDir}...\n`))

  await fs.ensureDir(projectTargetDir)

  let syncedCount = 0
  if (totalSelected > 0) {
    syncedCount += await syncSelectedItems(selectedSkills, projectTargetDir)
    syncedCount += await syncSelectedItems(selectedRules, projectTargetDir)
    syncedCount += await syncSelectedItems(selectedCommands, projectTargetDir)
  }
  syncedCount += await syncSettings(sourceDir, projectTargetDir)

  // CLAUDE.md 同步到全局
  await fs.ensureDir(globalTargetDir)
  syncedCount += await syncClaudeMd(sourceDir, globalTargetDir)

  console.log(chalk.blue(`\nDone! Synced ${syncedCount} items.`))
  console.log(chalk.gray(`  Project config → ${projectTargetDir}`))
  console.log(chalk.gray(`  CLAUDE.md      → ${globalTargetDir}`))
}

/**
 * 单独同步 CLAUDE.md 到当前项目 .claude/
 */
export async function syncProjectClaudeMd() {
  const sourceDir = await resolveSourceDir()
  const targetDir = path.join(process.cwd(), '.claude')

  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  await fs.ensureDir(targetDir)
  const synced = await syncClaudeMd(sourceDir, targetDir)

  if (synced) {
    console.log(chalk.blue(`\nDone! CLAUDE.md synced to ${targetDir}`))
  } else {
    console.log(chalk.yellow('\nCLAUDE.md not found in templates, nothing to sync.'))
  }
}


