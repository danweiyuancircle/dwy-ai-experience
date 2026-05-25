import fs from 'fs-extra'
import path from 'path'
import os from 'os'
import inquirer from 'inquirer'
import { chalk } from './utils.js'
import { groupedCheckbox } from './prompts/grouped-checkbox.js'
import {
  extractDescription,
  scanSkills,
  scanRules,
  scanHooks,
  resolveSourceDir,
  copyFilter,
  logAction,
} from './sync.js'

const CATEGORIES = [
  { key: 'skills', label: 'Skills' },
  { key: 'rules', label: 'Rules' },
  { key: 'hooks', label: 'Hooks' },
]

const BLOCK_START = '<!-- DWY-RULES:START 由 dwy codex sync 生成，请勿手动编辑此区块 -->'
const BLOCK_END = '<!-- DWY-RULES:END -->'
const BLOCK_RE = /<!-- DWY-RULES:START[\s\S]*?DWY-RULES:END -->/

// ---------- rules → AGENTS.md ----------

function parseRulePaths(frontmatter) {
  const m = frontmatter.match(/^paths:\s*\n((?:\s*-\s*.*\n?)+)/m)
  if (!m) return []
  return m[1].split('\n')
    .map(l => l.trim())
    .filter(l => l.startsWith('-'))
    .map(l => l.replace(/^-\s*/, '').replace(/^["']|["']$/g, '').trim())
    .filter(Boolean)
}

async function ruleToSection(ruleItem) {
  const raw = await fs.readFile(ruleItem.sourcePath, 'utf-8')
  const fm = raw.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/)
  const frontmatter = fm ? fm[1] : ''
  let body = (fm ? raw.slice(fm[0].length) : raw).trim()
  // 去掉 body 开头的 H1 标题行（与下方生成的 ## 标题重复），不动其余内容
  body = body.replace(/^#\s+.*\n+/, '')

  const description = extractDescription(raw) || ruleItem.name
  const paths = parseRulePaths(frontmatter)
  const marker = `<!-- dwy-rule: ${ruleItem.name} -->`
  const title = `## [dwy] ${description}`
  const scopeLine = paths.length
    ? `*适用范围（Codex 无路径作用域，仅供模型参考）：${paths.map(p => '`' + p + '`').join('、')}*`
    : ''
  return [marker, title, scopeLine, body].filter(Boolean).join('\n\n')
}

function parseManagedRuleNames(content) {
  const block = content.match(BLOCK_RE)
  if (!block) return new Set()
  const names = new Set()
  const re = /<!-- dwy-rule:\s*(.+?)\s*-->/g
  let m
  while ((m = re.exec(block[0]))) names.add(m[1])
  return names
}

function upsertManagedBlock(content, blockBody) {
  if (!blockBody.trim()) {
    if (!BLOCK_RE.test(content)) return content
    const next = content.replace(BLOCK_RE, '').replace(/\n{3,}/g, '\n\n').trimEnd()
    return next ? next + '\n' : ''
  }
  const block = `${BLOCK_START}\n\n${blockBody}\n\n${BLOCK_END}`
  if (BLOCK_RE.test(content)) return content.replace(BLOCK_RE, block)
  const base = content.trimEnd()
  return base ? `${base}\n\n${block}\n` : `${block}\n`
}

async function syncRulesToAgentsMd(selectedRules, proj, dryRun) {
  const dest = path.join(proj, 'AGENTS.md')
  const current = await fs.pathExists(dest) ? await fs.readFile(dest, 'utf-8') : ''

  const sections = []
  for (const r of selectedRules) sections.push(await ruleToSection(r))
  const blockBody = sections.join('\n\n---\n\n')

  const next = upsertManagedBlock(current, blockBody)
  if (next === current) return 0
  if (!dryRun) await fs.writeFile(dest, next)
  const filled = blockBody.trim()
  logAction(dryRun, `AGENTS.md — ${filled ? selectedRules.length + ' rules' : 'block removed'}`, filled ? 'green' : 'red', filled ? '✓' : '×')
  return 1
}

// ---------- skills → .agents/skills/ ----------

async function scanExistingCodexSkills(proj) {
  const dir = path.join(proj, '.agents', 'skills')
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir, { withFileTypes: true })
  return new Set(entries.filter(e => e.isDirectory()).map(e => e.name))
}

async function copySkillsFlat(skills, proj, dryRun) {
  const root = path.join(proj, '.agents', 'skills')
  for (const s of skills) {
    const dest = path.join(root, s.name)
    if (!dryRun) {
      await fs.ensureDir(path.dirname(dest))
      await fs.copy(s.sourcePath, dest, { overwrite: true, filter: copyFilter })
    }
    logAction(dryRun, `.agents/skills/${s.name}`)
  }
  return skills.length
}

async function removeUnselectedFlat(subdir, existingNames, selectedNames, templateNames, proj, dryRun) {
  let count = 0
  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    // 项目独有(模板未提供过)的条目永不删除,保留用户自定义
    if (!templateNames.has(name)) continue
    if (!dryRun) await fs.remove(path.join(proj, ...subdir, name))
    logAction(dryRun, `${subdir.join('/')}/${name}`, 'red', '×')
    count++
  }
  return count
}

// ---------- hooks → .codex/ ----------

async function scanExistingCodexHooks(proj) {
  const dir = path.join(proj, '.codex', 'hooks')
  if (!await fs.pathExists(dir)) return new Set()
  const entries = await fs.readdir(dir)
  return new Set(entries.filter(n => n !== '.gitkeep' && n !== '.DS_Store'))
}

async function copyCodexHooks(hooks, proj, dryRun) {
  if (hooks.length === 0) return 0
  const dir = path.join(proj, '.codex', 'hooks')
  if (!dryRun) await fs.ensureDir(dir)
  for (const h of hooks) {
    const dest = path.join(dir, h.name)
    if (!dryRun) {
      await fs.copy(h.sourcePath, dest, { overwrite: true, filter: copyFilter })
      await fs.chmod(dest, 0o755)
    }
    logAction(dryRun, `.codex/hooks/${h.name}`)
  }
  return hooks.length
}

function filterCodexHooksByNames(hooksJson, selectedNames) {
  if (!hooksJson.hooks) return hooksJson
  const cloned = JSON.parse(JSON.stringify(hooksJson))
  const re = /\.codex\/hooks\/([^\s"']+)/

  for (const event of Object.keys(cloned.hooks)) {
    const kept = []
    for (const cfg of cloned.hooks[event] || []) {
      const remaining = (cfg.hooks || []).filter(h => {
        const m = h.command?.match(re)
        if (!m) return true
        return selectedNames.has(m[1])
      })
      if (remaining.length > 0) kept.push({ ...cfg, hooks: remaining })
    }
    if (kept.length > 0) cloned.hooks[event] = kept
    else delete cloned.hooks[event]
  }
  if (Object.keys(cloned.hooks).length === 0) delete cloned.hooks
  return cloned
}

async function syncCodexHooksJson(hooksJsonSrc, proj, selectedHookNames, dryRun) {
  if (!await fs.pathExists(hooksJsonSrc)) return 0
  const dest = path.join(proj, '.codex', 'hooks.json')
  const filtered = filterCodexHooksByNames(await fs.readJson(hooksJsonSrc), selectedHookNames)

  if (!filtered.hooks) {
    if (!await fs.pathExists(dest)) return 0
    if (!dryRun) await fs.remove(dest)
    logAction(dryRun, '.codex/hooks.json — removed', 'red', '×')
    return 1
  }

  if (!dryRun) {
    await fs.ensureDir(path.dirname(dest))
    await fs.writeJson(dest, filtered, { spaces: 2 })
  }
  logAction(dryRun, '.codex/hooks.json')
  return 1
}

// ---------- 交互选择 ----------

async function promptSelection(items, label, defaultNames) {
  if (items.length === 0) return []
  return groupedCheckbox({ message: `选择 ${label}`, items, defaultSelected: defaultNames, pageSize: 15 })
}

async function interactiveSelect(scans, existing) {
  const sel = {}

  let i = 0
  while (i < CATEGORIES.length) {
    const { key, label } = CATEGORIES[i]
    const defaultNames = sel[key] ? new Set(sel[key].map(x => x.name)) : existing[key]
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

// ---------- 入口 ----------

/**
 * 入口：`dwy codex sync [target]`
 *   target=undefined  同步到项目：rules→AGENTS.md / skills→.agents/skills / hooks→.codex
 *   target='md'       仅同步 CLAUDE.md → 全局 ~/.codex/AGENTS.md
 */
export async function syncCodex({ target, reselect = false, dryRun = false } = {}) {
  const claudeGlobal = await resolveSourceDir()
  if (!await fs.pathExists(claudeGlobal)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  if (target === 'md') {
    const src = path.join(claudeGlobal, 'CLAUDE.md')
    if (!await fs.pathExists(src)) {
      console.log(chalk.yellow('CLAUDE.md not found in templates, nothing to sync.'))
      return
    }
    const dest = path.join(os.homedir(), '.codex', 'AGENTS.md')
    console.log(chalk.blue(`\nSyncing CLAUDE.md → ${dest}...\n`))
    if (!dryRun) {
      await fs.ensureDir(path.dirname(dest))
      await fs.copy(src, dest, { overwrite: true })
    }
    logAction(dryRun, dest)
    console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done.'}`))
    return
  }

  if (target !== undefined) {
    console.error(chalk.red(`Error: unknown sync target "${target}". Supported: (none) | md`))
    process.exit(2)
  }

  const codexGlobal = path.join(claudeGlobal, '..', 'codex-global')
  const hooksJsonSrc = path.join(codexGlobal, 'hooks.json')
  const proj = process.cwd()

  console.log(chalk.blue('\nScanning available config for Codex...\n'))

  const scans = {
    skills: await scanSkills(claudeGlobal),
    rules: await scanRules(claudeGlobal),
    hooks: await scanHooks(codexGlobal),
  }
  console.log(chalk.yellow(`Found ${scans.skills.length} skills, ${scans.rules.length} rules, ${scans.hooks.length} hooks\n`))

  const agentsMdPath = path.join(proj, 'AGENTS.md')
  const agentsMdContent = await fs.pathExists(agentsMdPath) ? await fs.readFile(agentsMdPath, 'utf-8') : ''
  const existing = {
    skills: await scanExistingCodexSkills(proj),
    rules: parseManagedRuleNames(agentsMdContent),
    hooks: await scanExistingCodexHooks(proj),
  }
  const hasAnyExisting = existing.skills.size + existing.rules.size + existing.hooks.size > 0

  if (!hasAnyExisting && !await fs.pathExists(path.join(proj, '.codex')) && !await fs.pathExists(path.join(proj, '.agents'))) {
    const { ok } = await inquirer.prompt([{
      type: 'confirm',
      name: 'ok',
      message: `当前目录 ${chalk.yellow(proj)} 尚无 Codex 配置，是否在此初始化？`,
      default: false,
    }])
    if (!ok) {
      console.log(chalk.yellow('\n已取消同步。'))
      return
    }
  }

  let selected
  if (!reselect && hasAnyExisting) {
    selected = {
      skills: scans.skills.filter(s => existing.skills.has(s.name)),
      rules: scans.rules.filter(r => existing.rules.has(r.name)),
      hooks: existing.hooks.size > 0 ? scans.hooks.filter(h => existing.hooks.has(h.name)) : scans.hooks,
    }
    console.log(chalk.gray('使用已选覆盖同步（如需调整请加 -i / --reselect）：'))
    console.log(chalk.gray(`  ${selected.skills.length} skills, ${selected.rules.length} rules, ${selected.hooks.length} hooks\n`))
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

  console.log(chalk.blue(`\n${dryRun ? '[dry-run] ' : ''}Syncing to ${proj}...\n`))

  let syncedCount = 0
  let removedCount = 0

  syncedCount += await copySkillsFlat(selected.skills, proj, dryRun)
  syncedCount += await syncRulesToAgentsMd(selected.rules, proj, dryRun)
  syncedCount += await copyCodexHooks(selected.hooks, proj, dryRun)
  syncedCount += await syncCodexHooksJson(hooksJsonSrc, proj, selectedHookNames, dryRun)

  // 删除已存在但本次未勾选的（仅 reselect 模式；rules 删除已由托管块重生成体现）
  if (reselect) {
    const skillTemplateNames = new Set(scans.skills.map(s => s.name))
    const hookTemplateNames = new Set(scans.hooks.map(h => h.name))
    removedCount += await removeUnselectedFlat(['.agents', 'skills'], existing.skills, new Set(selected.skills.map(s => s.name)), skillTemplateNames, proj, dryRun)
    removedCount += await removeUnselectedFlat(['.codex', 'hooks'], existing.hooks, selectedHookNames, hookTemplateNames, proj, dryRun)
  }

  console.log(chalk.blue(`\n${dryRun ? 'Dry-run complete.' : 'Done!'} ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Rules  → ${agentsMdPath}`))
  console.log(chalk.gray(`  Skills → ${path.join(proj, '.agents', 'skills')}`))
  console.log(chalk.gray(`  Hooks  → ${path.join(proj, '.codex')}`))
}
