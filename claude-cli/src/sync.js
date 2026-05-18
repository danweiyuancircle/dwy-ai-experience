import fs from 'fs-extra'
import path from 'path'
import os from 'os'
import inquirer from 'inquirer'
import { ensureRepoCache, chalk } from './utils.js'
import { groupedCheckbox } from './prompts/grouped-checkbox.js'

const CATEGORIES = [
  { key: 'skills', label: 'Skills' },
  { key: 'rules', label: 'Rules' },
  { key: 'commands', label: 'Commands' },
  { key: 'hooks', label: 'Hooks' },
]

function extractDescription(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return ''
  const lines = match[1].split('\n')
  let i = 0
  while (i < lines.length) {
    const kv = lines[i].match(/^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$/)
    if (!kv) { i++; continue }
    if (kv[1] === 'description') {
      const trimmed = kv[2].trim()
      if (trimmed === '>' || trimmed === '|') {
        i++
        const parts = []
        while (i < lines.length && (lines[i].startsWith('  ') || lines[i].trim() === '')) {
          parts.push(lines[i].trim())
          i++
        }
        return parts.filter(Boolean).join(' ')
      }
      return trimmed.replace(/^["']|["']$/g, '')
    }
    i++
  }
  return ''
}

async function scanSkills(sourceDir) {
  const skillsDir = path.join(sourceDir, 'skills')
  if (!await fs.pathExists(skillsDir)) return []

  const skills = []
  for (const cat of await fs.readdir(skillsDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(skillsDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue
      const skillPath = path.join(catDir, entry.name)
      const skillMd = path.join(skillPath, 'SKILL.md')
      if (!await fs.pathExists(skillMd)) continue
      const content = await fs.readFile(skillMd, 'utf-8')
      skills.push({
        name: entry.name,
        description: extractDescription(content) || '（无描述）',
        category: cat.name,
        sourcePath: skillPath,
        type: 'skill',
      })
    }
  }
  return skills.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanRules(sourceDir) {
  const rulesDir = path.join(sourceDir, 'rules')
  if (!await fs.pathExists(rulesDir)) return []

  const rules = []
  for (const cat of await fs.readdir(rulesDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(rulesDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (!entry.isFile() || !entry.name.endsWith('.md')) continue
      const rulePath = path.join(catDir, entry.name)
      const content = await fs.readFile(rulePath, 'utf-8')
      rules.push({
        name: entry.name,
        description: extractDescription(content) || '（无描述）',
        category: cat.name,
        sourcePath: rulePath,
        type: 'rule',
      })
    }
  }
  return rules.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanCommands(sourceDir) {
  const commandsDir = path.join(sourceDir, 'commands')
  if (!await fs.pathExists(commandsDir)) return []

  const entries = await fs.readdir(commandsDir, { withFileTypes: true })
  return entries
    .filter(e => e.name !== '.gitkeep')
    .map(e => ({
      name: e.name,
      description: e.isDirectory() ? '命令目录' : '命令文件',
      category: '其他',
      sourcePath: path.join(commandsDir, e.name),
      type: 'command',
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
}

async function scanHooks(sourceDir) {
  const hooksDir = path.join(sourceDir, 'hooks')
  if (!await fs.pathExists(hooksDir)) return []

  const hooks = []
  for (const cat of await fs.readdir(hooksDir, { withFileTypes: true })) {
    if (!cat.isDirectory()) continue
    const catDir = path.join(hooksDir, cat.name)
    for (const entry of await fs.readdir(catDir, { withFileTypes: true })) {
      if (entry.name === '.gitkeep') continue
      hooks.push({
        name: entry.name,
        description: entry.isDirectory() ? '钩子目录' : '钩子脚本',
        category: cat.name,
        sourcePath: path.join(catDir, entry.name),
        type: 'hook',
      })
    }
  }
  return hooks.sort((a, b) => a.name.localeCompare(b.name))
}

async function scanExisting(projectTargetDir, typePlural) {
  const dir = path.join(projectTargetDir, typePlural)
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir)
  return new Set(entries.filter(name => name !== '.gitkeep' && name !== '.DS_Store'))
}

async function promptSelection(items, label, defaultNames) {
  if (items.length === 0) return []
  return groupedCheckbox({
    message: `选择 ${label}`,
    items,
    defaultSelected: defaultNames,
    pageSize: 15,
  })
}

/**
 * 交互式选择：每步可回退到上一步，最后总览支持任意类别重选。
 * 返回 { skills, rules, commands, hooks } 或 null（取消）。
 */
async function interactiveSelect(scans, existing) {
  const sel = {}

  // 第一轮：顺序遍历，每步给导航
  let i = 0
  while (i < CATEGORIES.length) {
    const { key, label } = CATEGORIES[i]
    const defaultNames = sel[key]
      ? new Set(sel[key].map(x => x.name))
      : existing[key]
    sel[key] = await promptSelection(scans[key], label, defaultNames)

    if (i === CATEGORIES.length - 1) break

    const nextLabel = CATEGORIES[i + 1].label
    const prevLabel = i > 0 ? CATEGORIES[i - 1].label : null
    const { nav } = await inquirer.prompt([{
      type: 'list',
      name: 'nav',
      message: `${label} 已选 ${sel[key].length} 项。下一步：`,
      choices: [
        { name: `→ 继续选 ${nextLabel}`, value: 'next' },
        ...(prevLabel ? [{ name: `← 返回重选 ${prevLabel}`, value: 'back' }] : []),
        { name: '✗ 取消同步', value: 'cancel' },
      ],
      default: 'next',
    }])
    if (nav === 'cancel') return null
    i = nav === 'back' ? i - 1 : i + 1
  }

  // 第二轮：总览 + 任意重选
  while (true) {
    console.log(chalk.gray('\n选择汇总：'))
    for (const { key, label } of CATEGORIES) {
      console.log(chalk.gray(`  ${label.padEnd(10)} ${sel[key].length} 项`))
    }
    const { final } = await inquirer.prompt([{
      type: 'list',
      name: 'final',
      message: '确认提交还是重选？',
      choices: [
        { name: '✓ 确认提交', value: 'confirm' },
        ...CATEGORIES.map(c => ({ name: `重选 ${c.label}`, value: c.key })),
        { name: '✗ 取消同步', value: 'cancel' },
      ],
      default: 'confirm',
    }])
    if (final === 'confirm') return sel
    if (final === 'cancel') return null
    const cat = CATEGORIES.find(c => c.key === final)
    sel[final] = await promptSelection(scans[final], cat.label, new Set(sel[final].map(x => x.name)))
  }
}

function logAction(dryRun, label, color = 'green', prefix = '✓') {
  console.log(chalk[color](`  ${dryRun ? '[dry-run] ' : prefix + ' '}${label}`))
}

async function copyItems(items, targetDir, dryRun) {
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

async function copyHooks(items, targetDir, dryRun) {
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

async function removeUnselected(typePlural, existingNames, selectedNames, templateNames, targetDir, dryRun) {
  let count = 0
  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    // 项目独有(模板未提供过)的条目永不删除,保留用户自定义
    if (!templateNames.has(name)) continue
    const target = path.join(targetDir, typePlural, name)
    if (!dryRun) await fs.remove(target)
    logAction(dryRun, `${typePlural}/${name}`, 'red', '×')
    count++
  }
  return count
}

/**
 * 过滤模板 settings.json 中未选中 hooks 的引用。
 * 识别规则：command 字段中匹配 $CLAUDE_PROJECT_DIR/.claude/hooks/<name> 的项。
 */
function filterSettingsByHooks(newSettings, selectedHookNames) {
  if (!newSettings.hooks) return newSettings
  const cloned = JSON.parse(JSON.stringify(newSettings))
  const hookPathRegex = /\.claude\/hooks\/([^\s'"]+)/

  for (const event of Object.keys(cloned.hooks)) {
    const configs = cloned.hooks[event] || []
    const kept = []
    for (const cfg of configs) {
      const remainingHooks = (cfg.hooks || []).filter(h => {
        const m = h.command?.match(hookPathRegex)
        if (!m) return true
        return selectedHookNames.has(m[1])
      })
      if (remainingHooks.length > 0) kept.push({ ...cfg, hooks: remainingHooks })
    }
    if (kept.length > 0) cloned.hooks[event] = kept
    else delete cloned.hooks[event]
  }

  if (Object.keys(cloned.hooks).length === 0) delete cloned.hooks
  return cloned
}

async function syncSettings(sourceDir, targetDir, selectedHookNames, dryRun) {
  const settingsSrc = path.join(sourceDir, 'settings.json')
  if (!await fs.pathExists(settingsSrc)) return 0

  const settingsDest = path.join(targetDir, 'settings.json')
  const newSettings = await fs.readJson(settingsSrc)
  const filteredNew = filterSettingsByHooks(newSettings, selectedHookNames)

  let merged
  let action
  if (await fs.pathExists(settingsDest)) {
    const existing = await fs.readJson(settingsDest)
    merged = { ...existing }
    for (const [key, value] of Object.entries(filteredNew)) {
      if (key === 'hooks') continue
      if (key in merged && typeof merged[key] === 'object' && !Array.isArray(merged[key])
          && typeof value === 'object' && !Array.isArray(value)) {
        merged[key] = { ...merged[key], ...value }
      } else {
        merged[key] = value
      }
    }
    // hooks 字段由模板独占：模板有则覆盖，模板没有则删除
    if (filteredNew.hooks) merged.hooks = filteredNew.hooks
    else delete merged.hooks
    action = 'merged'
  } else {
    merged = filteredNew
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
 *   target=undefined  同步项目 .claude/（不动全局 CLAUDE.md）
 *   target='md'       仅同步 CLAUDE.md → 全局 ~/.claude/
 */
export async function syncClaude({ target, reselect = false, dryRun = false } = {}) {
  const sourceDir = await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  if (target === 'md') {
    const globalTargetDir = path.join(os.homedir(), '.claude')
    if (!dryRun) await fs.ensureDir(globalTargetDir)
    console.log(chalk.blue(`\nSyncing CLAUDE.md to ${globalTargetDir}...\n`))
    const synced = await syncClaudeMd(sourceDir, globalTargetDir, dryRun)
    if (!synced) console.log(chalk.yellow('CLAUDE.md not found in templates, nothing to sync.'))
    else console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done.'}`))
    return
  }

  if (target !== undefined) {
    console.error(chalk.red(`Error: unknown sync target "${target}". Supported: (none) | md`))
    process.exit(2)
  }

  console.log(chalk.blue('\nScanning available Claude configuration...\n'))
  const projectTargetDir = path.join(process.cwd(), '.claude')

  if (!await fs.pathExists(projectTargetDir)) {
    const { shouldCreate } = await inquirer.prompt([{
      type: 'confirm',
      name: 'shouldCreate',
      message: `当前目录 ${chalk.yellow(process.cwd())} 未找到 .claude 目录，是否在此创建？`,
      default: false,
    }])
    if (!shouldCreate) {
      console.log(chalk.yellow('\n已取消同步。'))
      return
    }
  }

  const scans = {
    skills: await scanSkills(sourceDir),
    rules: await scanRules(sourceDir),
    commands: await scanCommands(sourceDir),
    hooks: await scanHooks(sourceDir),
  }
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.rules.length} rules, ${scans.commands.length} commands, ${scans.hooks.length} hooks\n`))

  const existing = {
    skills: await scanExisting(projectTargetDir, 'skills'),
    rules: await scanExisting(projectTargetDir, 'rules'),
    commands: await scanExisting(projectTargetDir, 'commands'),
    hooks: await scanExisting(projectTargetDir, 'hooks'),
  }
  const hasAnyExisting = existing.skills.size + existing.rules.size + existing.commands.size + existing.hooks.size > 0

  let selected

  if (!reselect && hasAnyExisting) {
    // 缓存模式：模板 ∩ 已选
    selected = {
      skills: scans.skills.filter(s => existing.skills.has(s.name)),
      rules: scans.rules.filter(r => existing.rules.has(r.name)),
      commands: scans.commands.filter(c => existing.commands.has(c.name)),
      hooks: existing.hooks.size > 0
        ? scans.hooks.filter(h => existing.hooks.has(h.name))
        : scans.hooks,
    }
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

  const selectedHookNames = new Set(selected.hooks.map(h => h.name))

  console.log(chalk.blue(`\n${dryRun ? '[dry-run] ' : ''}Syncing to ${projectTargetDir}...\n`))
  if (!dryRun) await fs.ensureDir(projectTargetDir)

  let syncedCount = 0
  let removedCount = 0

  syncedCount += await copyItems(selected.skills, projectTargetDir, dryRun)
  syncedCount += await copyItems(selected.rules, projectTargetDir, dryRun)
  syncedCount += await copyItems(selected.commands, projectTargetDir, dryRun)
  syncedCount += await syncSettings(sourceDir, projectTargetDir, selectedHookNames, dryRun)
  syncedCount += await copyHooks(selected.hooks, projectTargetDir, dryRun)

  // 删除已存在但本次未勾选的(仅 reselect 模式:缓存模式默认 selected ⊇ existing 不会触发)
  // 删除范围限定在模板提供过的条目内,项目自定义条目(scans 里没有的)始终保留
  if (reselect) {
    const skillTemplateNames = new Set(scans.skills.map(s => s.name))
    const ruleTemplateNames = new Set(scans.rules.map(r => r.name))
    const commandTemplateNames = new Set(scans.commands.map(c => c.name))
    const hookTemplateNames = new Set(scans.hooks.map(h => h.name))
    removedCount += await removeUnselected('skills', existing.skills, new Set(selected.skills.map(s => s.name)), skillTemplateNames, projectTargetDir, dryRun)
    removedCount += await removeUnselected('rules', existing.rules, new Set(selected.rules.map(r => r.name)), ruleTemplateNames, projectTargetDir, dryRun)
    removedCount += await removeUnselected('commands', existing.commands, new Set(selected.commands.map(c => c.name)), commandTemplateNames, projectTargetDir, dryRun)
    removedCount += await removeUnselected('hooks', existing.hooks, selectedHookNames, hookTemplateNames, projectTargetDir, dryRun)
  }

  console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done!'} ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Project config → ${projectTargetDir}`))
  console.log(chalk.gray(`  Hooks          → ${path.join(projectTargetDir, 'hooks')}`))
  console.log(chalk.gray('  CLAUDE.md      → 跳过（用 `dwy claude sync md` 单独同步到 ~/.claude/）'))
}
