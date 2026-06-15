import fs from 'fs-extra'
import path from 'path'
import { chalk } from './utils.js'
import {
  extractDescription,
  logAction,
  readBaselineDoc,
  scanRules,
  resolveSourceDir,
} from './sync.js'

const BASELINE_RULE_NAME = '00-dwy-global.mdc'

function stripFrontmatter(content) {
  const match = content.match(/^---\s*\n[\s\S]*?\n---\s*\n?/)
  return match ? content.slice(match[0].length).trim() : content.trim()
}

function extractFrontmatter(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/)
  return match ? match[1] : ''
}

function parseRulePaths(frontmatter) {
  const match = frontmatter.match(/^paths:\s*\n((?:\s*-\s*.*\n?)+)/m)
  if (!match) return []
  return match[1]
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.startsWith('-'))
    .map(line => line.replace(/^-\s*/, '').replace(/^["']|["']$/g, '').trim())
    .filter(Boolean)
}

function toCursorRuleName(ruleName) {
  return `dwy-${ruleName.replace(/\.md$/i, '')}.mdc`
}

async function buildCursorRule(ruleItem) {
  const raw = await fs.readFile(ruleItem.sourcePath, 'utf-8')
  const description = extractDescription(raw) || ruleItem.name.replace(/\.md$/i, '')
  const frontmatter = extractFrontmatter(raw)
  const paths = parseRulePaths(frontmatter)
  const body = stripFrontmatter(raw)

  const lines = [
    '---',
    `description: ${JSON.stringify(`[dwy] ${description}`)}`,
  ]

  if (paths.length > 0) {
    lines.push('alwaysApply: false')
    lines.push('globs:')
    for (const rulePath of paths) {
      lines.push(`  - ${JSON.stringify(rulePath)}`)
    }
  } else {
    lines.push('alwaysApply: true')
  }

  lines.push('---', '', body, '')
  return lines.join('\n')
}

async function syncCursorRules(selectedRules, projectDir) {
  const rulesDir = path.join(projectDir, '.cursor', 'rules')
  await fs.ensureDir(rulesDir)

  let syncedCount = 0
  for (const rule of selectedRules) {
    const destName = toCursorRuleName(rule.name)
    const destPath = path.join(rulesDir, destName)
    const content = await buildCursorRule(rule)
    await fs.writeFile(destPath, content)
    logAction(`.cursor/rules/${destName}`)
    syncedCount++
  }

  return syncedCount
}

async function syncCursorBaselineRule(sourceDir, projectDir) {
  const baseline = await readBaselineDoc(sourceDir)
  if (!baseline) return 0

  const rulesDir = path.join(projectDir, '.cursor', 'rules')
  const destPath = path.join(rulesDir, BASELINE_RULE_NAME)
  const content = [
    '---',
    `description: ${JSON.stringify('[dwy] Global baseline')}`,
    'alwaysApply: true',
    '---',
    '',
    baseline.trim(),
    '',
  ].join('\n')

  await fs.ensureDir(rulesDir)
  await fs.writeFile(destPath, content)
  logAction(`.cursor/rules/${BASELINE_RULE_NAME}`)
  return 1
}

async function removeUnselectedCursorRules(existingNames, selectedNames, managedNames, projectDir) {
  const rulesDir = path.join(projectDir, '.cursor', 'rules')
  let removedCount = 0

  for (const name of existingNames) {
    if (selectedNames.has(name)) continue
    if (!managedNames.has(name)) continue
    await fs.remove(path.join(rulesDir, name))
    logAction(`.cursor/rules/${name}`, 'red', '×')
    removedCount++
  }

  return removedCount
}

export async function scanExistingCursorRules(projectDir) {
  const rulesDir = path.join(projectDir, '.cursor', 'rules')
  if (!await fs.pathExists(rulesDir)) return new Set()
  const entries = await fs.readdir(rulesDir, { withFileTypes: true })
  return new Set(
    entries
      .filter(entry => entry.isFile()
        && ((entry.name.startsWith('dwy-') && entry.name.endsWith('.mdc')) || entry.name === BASELINE_RULE_NAME))
      .map(entry => entry.name),
  )
}

export async function syncCursor({
  sourceDir: sourceDirOverride,
  projectDir,
  selected,
  staleRemovals = {},
} = {}) {
  const sourceDir = sourceDirOverride || await resolveSourceDir()
  if (!await fs.pathExists(sourceDir)) {
    throw new Error('ai-tools templates not found in repo')
  }

  const proj = projectDir || process.cwd()

  console.log(chalk.blue('\nSyncing Cursor configuration...\n'))

  const scans = {
    rules: await scanRules(sourceDir),
  }
  const selectedRuleNames = new Set((selected.rules || []).map(item => item.name))
  const syncedSelection = scans.rules.filter(rule => selectedRuleNames.has(rule.name))
  const existingRules = await scanExistingCursorRules(proj)
  const nextRuleNames = new Set(syncedSelection.map(rule => toCursorRuleName(rule.name)))
  const managedRuleNames = new Set([
    ...scans.rules.map(rule => toCursorRuleName(rule.name)),
    ...[...(staleRemovals.rules || new Set())].map(ruleName => toCursorRuleName(ruleName)),
    BASELINE_RULE_NAME,
  ])

  let syncedCount = 0
  let removedCount = 0

  syncedCount += await syncCursorBaselineRule(sourceDir, proj)
  syncedCount += await syncCursorRules(syncedSelection, proj)
  nextRuleNames.add(BASELINE_RULE_NAME)
  removedCount += await removeUnselectedCursorRules(existingRules, nextRuleNames, managedRuleNames, proj)

  console.log(chalk.blue(`\nDone! ${syncedCount} synced${removedCount > 0 ? `, ${removedCount} removed` : ''}.`))
  console.log(chalk.gray(`  Rules → ${path.join(proj, '.cursor', 'rules')}`))
  console.log(chalk.gray('  Skills / Commands / Hooks → 当前适配未支持'))
}
