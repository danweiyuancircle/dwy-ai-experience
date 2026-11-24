/**
 * `dwy skills`：第三方 skills / plugins 收藏与官方命令编排。
 * 不改写 dwy 模板 sync；确认前不执行安装/卸载。
 */

import { confirm, isCancel, select } from '@clack/prompts'
import os from 'node:os'
import path from 'node:path'
import { searchableMultiselect } from './searchable-select.js'
import {
  addCatalogEntry,
  exportCatalog,
  importCatalog,
  loadCatalog,
  removeCatalogEntry,
} from './skills-catalog.js'
import {
  buildInstallCommand,
  buildRemoveCommand,
  buildUpdateCommand,
  formatCommand,
  runCommands,
} from './skills-install.js'
import { scanInstalledSkills } from './skills-scan.js'
import { resolveSourceDir, scanSkills } from './sync.js'
import { chalk } from './utils.js'

function printSkillsHelp() {
  console.log([
    '用法：',
    '  dwy skills                 交互管理第三方 Skills / Plugins',
    '  dwy skills list            列出本机已装项与来源',
    '  dwy skills catalog         列出收藏',
    '  dwy skills catalog add <源> [--kind skills-cli|claude-plugin|claude-marketplace|codex-plugin|codex-marketplace]',
    '  dwy skills catalog remove <id>',
    '  dwy skills catalog export <文件>',
    '  dwy skills catalog import <文件> [--replace]',
    '  dwy skills add <源> [--install] [--kind ...]',
    '  dwy skills install [id…] [--all] [--yes]',
    '  dwy skills update [id…]',
    '  dwy skills remove <id|name> [--yes]',
    '',
    '安装/更新/卸载走官方命令（npx skills / claude plugin / codex plugin）；dwy 模板 Skills 请用 dwy sync。',
  ].join('\n'))
}

function parseFlags(args) {
  const flags = new Set()
  const positionals = []
  let kind
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    if (arg === '--kind') {
      kind = args[++i]
      continue
    }
    if (arg.startsWith('--')) flags.add(arg.slice(2))
    else positionals.push(arg)
  }
  return { flags, positionals, kind }
}

function inferKind(source, kindFlag) {
  if (kindFlag) return kindFlag
  if (/^[^/@]+@[^/@]+$/.test(source)) return 'claude-plugin'
  return 'skills-cli'
}

async function templateSkillNames(homeDir, override) {
  if (override instanceof Set) return override
  if (Array.isArray(override)) return new Set(override)
  try {
    const sourceDir = await resolveSourceDir({ homeDir, onFallback: () => {} })
    const skills = await scanSkills(sourceDir)
    return new Set(skills.map(skill => skill.name))
  } catch {
    return new Set()
  }
}

function findEntries(catalog, ids) {
  if (!ids.length) return []
  const wanted = new Set(ids)
  return catalog.entries.filter(entry => wanted.has(entry.id) || wanted.has(entry.source))
}

async function previewAndRun(commands, { yes, runCommand, confirmFn = confirm } = {}) {
  if (!commands.length) {
    console.log(chalk.yellow('没有可执行的命令。'))
    return { ok: [], failed: [] }
  }
  console.log(chalk.blue('\n将执行：'))
  for (const command of commands) console.log(chalk.gray(`  ${formatCommand(command)}`))
  if (!yes) {
    const ok = await confirmFn({ message: '确认执行以上官方命令？', initialValue: false })
    if (isCancel(ok) || !ok) {
      console.log(chalk.yellow('已取消。'))
      return { ok: [], failed: [], cancelled: true }
    }
  }
  const result = await runCommands(commands, { runCommand })
  console.log(chalk.green(`\n完成：成功 ${result.ok.length}，失败 ${result.failed.length}`))
  for (const item of result.failed) console.log(chalk.red(`  ✗ ${item.label}: ${item.error}`))
  return result
}

async function cmdList({ homeDir, listPlugins, listCodexPlugins, templateSkillNames: templatesOverride }) {
  const templates = await templateSkillNames(homeDir, templatesOverride)
  const installed = await scanInstalledSkills({
    homeDir,
    templateSkillNames: templates,
    listPlugins,
    listCodexPlugins,
  })
  console.log(chalk.blue('已装 Skills：'))
  if (!installed.skills.length) console.log(chalk.gray('  （无）'))
  for (const item of installed.skills) {
    console.log(`  ${item.name}  [${item.provenance}]  agents=${item.agents.join(',') || '-'}`)
  }
  const claudePlugins = installed.plugins.filter(item => item.runtime === 'claude' || item.kind === 'claude-plugin')
  const codexPlugins = installed.plugins.filter(item => item.runtime === 'codex' || item.kind === 'codex-plugin')
  console.log(chalk.blue('\n已装 Claude Plugins：'))
  if (!claudePlugins.length) console.log(chalk.gray('  （无）'))
  for (const item of claudePlugins) {
    console.log(`  ${item.source}  [${item.provenance}]`)
  }
  console.log(chalk.blue('\n已装 Codex Plugins：'))
  if (!codexPlugins.length) console.log(chalk.gray('  （无）'))
  for (const item of codexPlugins) {
    console.log(`  ${item.source}  [${item.provenance}]`)
  }
  return installed
}

async function cmdCatalog(args, { homeDir }) {
  const sub = args[0]
  if (!sub || sub === 'list') {
    const catalog = await loadCatalog(homeDir)
    if (!catalog.entries.length) {
      console.log(chalk.gray('收藏为空。用 dwy skills add <源> 添加。'))
      return catalog
    }
    for (const entry of catalog.entries) {
      const extra = [
        entry.kind,
        entry.skills?.length ? `skills=${entry.skills.join(',')}` : null,
        entry.agents?.length ? `agents=${entry.agents.join(',')}` : null,
      ].filter(Boolean).join(' · ')
      console.log(`  ${entry.id}  (${extra})`)
    }
    return catalog
  }
  if (sub === 'add') {
    const { positionals, kind } = parseFlags(args.slice(1))
    const source = positionals[0]
    if (!source) throw new Error('用法：dwy skills catalog add <源>')
    const entry = await addCatalogEntry(homeDir, { kind: inferKind(source, kind), source })
    console.log(chalk.green(`已收藏 ${entry.id}`))
    return entry
  }
  if (sub === 'remove') {
    const id = args[1]
    if (!id) throw new Error('用法：dwy skills catalog remove <id>')
    await removeCatalogEntry(homeDir, id)
    console.log(chalk.green(`已从收藏移除 ${id}`))
    return
  }
  if (sub === 'export') {
    const file = args[1]
    if (!file) throw new Error('用法：dwy skills catalog export <文件>')
    await exportCatalog(homeDir, path.resolve(file))
    console.log(chalk.green(`已导出到 ${path.resolve(file)}`))
    return
  }
  if (sub === 'import') {
    const { positionals, flags } = parseFlags(args.slice(1))
    const file = positionals[0]
    if (!file) throw new Error('用法：dwy skills catalog import <文件> [--replace]')
    await importCatalog(homeDir, path.resolve(file), { merge: !flags.has('replace') })
    console.log(chalk.green(`已导入 ${path.resolve(file)}`))
    return
  }
  throw new Error(`未知 catalog 子命令: ${sub}`)
}

async function cmdAdd(args, deps) {
  const { positionals, flags, kind } = parseFlags(args)
  const source = positionals[0]
  if (!source) throw new Error('用法：dwy skills add <源> [--install] [--kind ...]')
  const entry = await addCatalogEntry(deps.homeDir, { kind: inferKind(source, kind), source })
  console.log(chalk.green(`已收藏 ${entry.id}`))
  if (flags.has('install')) {
    return previewAndRun([buildInstallCommand(entry)], {
      yes: flags.has('yes'),
      runCommand: deps.runCommand,
      confirmFn: deps.confirmFn,
    })
  }
  return entry
}

async function cmdInstall(args, deps) {
  const { positionals, flags } = parseFlags(args)
  const catalog = await loadCatalog(deps.homeDir)
  const entries = flags.has('all') ? catalog.entries : findEntries(catalog, positionals)
  if (!flags.has('all') && !positionals.length) throw new Error('用法：dwy skills install <id…> 或 --all')
  if (!entries.length) throw new Error('收藏中没有匹配项')
  return previewAndRun(entries.map(buildInstallCommand), {
    yes: flags.has('yes'),
    runCommand: deps.runCommand,
    confirmFn: deps.confirmFn,
  })
}

async function cmdUpdate(args, deps) {
  const { positionals, flags } = parseFlags(args)
  const catalog = await loadCatalog(deps.homeDir)
  const entries = positionals.length ? findEntries(catalog, positionals) : catalog.entries
  if (!entries.length) throw new Error('没有可更新的收藏项')
  return previewAndRun(entries.map(buildUpdateCommand), {
    yes: flags.has('yes'),
    runCommand: deps.runCommand,
    confirmFn: deps.confirmFn,
  })
}

async function cmdRemove(args, deps) {
  const { positionals, flags, kind: kindFlag } = parseFlags(args)
  const id = positionals[0]
  if (!id) throw new Error('用法：dwy skills remove <id|name> [--yes] [--kind claude-plugin|codex-plugin]')

  const templates = await templateSkillNames(deps.homeDir, deps.templateSkillNames)
  if (templates.has(id)) {
    throw new Error(`${id} 是 dwy 模板 Skill，请用 dwy sync 管理，不能通过 dwy skills remove 卸载`)
  }

  const catalog = await loadCatalog(deps.homeDir)
  const entry = catalog.entries.find(item => item.id === id || item.source === id)
  if (entry) {
    return previewAndRun([buildRemoveCommand(entry)], {
      yes: flags.has('yes'),
      runCommand: deps.runCommand,
      confirmFn: deps.confirmFn,
    })
  }

  const guessed = /^[^/@]+@[^/@]+$/.test(id)
    ? { kind: kindFlag === 'codex-plugin' ? 'codex-plugin' : 'claude-plugin', source: id }
    : { kind: 'skills-cli', source: id, skills: [id], id }
  return previewAndRun([buildRemoveCommand(guessed)], {
    yes: flags.has('yes'),
    runCommand: deps.runCommand,
    confirmFn: deps.confirmFn,
  })
}

async function interactiveSkills(deps) {
  const action = await (deps.selectFn || select)({
    message: '选择操作',
    options: [
      { value: 'install', label: '从收藏安装' },
      { value: 'manage', label: '管理已装（更新 / 卸载）' },
      { value: 'catalog', label: '编辑收藏（列出）' },
    ],
  })
  if (isCancel(action)) {
    console.log(chalk.yellow('已取消。'))
    return { cancelled: true }
  }
  if (action === 'catalog') return cmdCatalog(['list'], deps)

  const catalog = await loadCatalog(deps.homeDir)
  if (action === 'install') {
    if (!catalog.entries.length) {
      console.log(chalk.yellow('收藏为空，先用 dwy skills add <源> 添加。'))
      return catalog
    }
    const selected = await (deps.multiselectFn || searchableMultiselect)({
      message: '选择要安装的收藏项',
      options: catalog.entries.map(entry => ({
        value: entry.id,
        label: entry.id,
        description: `${entry.kind} · ${entry.source}`,
      })),
      required: true,
    })
    if (isCancel(selected)) {
      console.log(chalk.yellow('已取消。'))
      return { cancelled: true }
    }
    const entries = findEntries(catalog, selected)
    return previewAndRun(entries.map(buildInstallCommand), {
      runCommand: deps.runCommand,
      confirmFn: deps.confirmFn,
    })
  }

  const templates = await templateSkillNames(deps.homeDir, deps.templateSkillNames)
  const installed = await scanInstalledSkills({
    homeDir: deps.homeDir,
    templateSkillNames: templates,
    listPlugins: deps.listPlugins,
    listCodexPlugins: deps.listCodexPlugins,
  })
  const options = [
    ...installed.skills.map(item => ({
      value: `skill:${item.name}`,
      label: item.name,
      description: `skill · ${item.provenance}`,
      disabled: item.provenance === 'dwy-template',
    })),
    ...installed.plugins.map(item => ({
      value: `${item.kind}:${item.source}`,
      label: item.source,
      description: `${item.runtime || item.kind} · ${item.provenance}`,
    })),
  ]
  if (!options.length) {
    console.log(chalk.yellow('未扫描到已装项。'))
    return installed
  }
  const selected = await (deps.multiselectFn || searchableMultiselect)({
    message: '选择要处理的已装项',
    options,
    required: true,
  })
  if (isCancel(selected)) {
    console.log(chalk.yellow('已取消。'))
    return { cancelled: true }
  }
  const op = await (deps.selectFn || select)({
    message: '对这些项做什么',
    options: [
      { value: 'update', label: '更新' },
      { value: 'remove', label: '卸载' },
    ],
  })
  if (isCancel(op)) {
    console.log(chalk.yellow('已取消。'))
    return { cancelled: true }
  }
  const commands = []
  for (const value of selected) {
    if (value.startsWith('skill:')) {
      const name = value.slice('skill:'.length)
      if (templates.has(name)) continue
      const entry = catalog.entries.find(item =>
        item.kind === 'skills-cli' && (item.skills?.includes(name) || item.id === name || item.source === name),
      ) || { kind: 'skills-cli', source: name, skills: [name], id: name }
      commands.push(op === 'update' ? buildUpdateCommand(entry) : buildRemoveCommand(entry))
    } else if (value.startsWith('claude-plugin:') || value.startsWith('codex-plugin:') || value.startsWith('plugin:')) {
      const kind = value.startsWith('codex-plugin:')
        ? 'codex-plugin'
        : value.startsWith('claude-plugin:')
          ? 'claude-plugin'
          : 'claude-plugin'
      const source = value.slice(value.indexOf(':') + 1)
      const entry = catalog.entries.find(item => item.source === source && (item.kind === kind || !item.kind))
        || { kind, source }
      commands.push(op === 'update' ? buildUpdateCommand(entry) : buildRemoveCommand(entry))
    }
  }
  return previewAndRun(commands, {
    runCommand: deps.runCommand,
    confirmFn: deps.confirmFn,
  })
}

/**
 * @param {string[]} argv skills 后的参数
 * @param {object} [deps]
 */
export async function runSkillsCommand(argv = [], deps = {}) {
  const homeDir = deps.homeDir || os.homedir()
  const bound = { ...deps, homeDir }

  if (argv.includes('--help') || argv.includes('-h') || argv[0] === 'help') {
    printSkillsHelp()
    return
  }

  const command = argv[0]
  if (!command) return interactiveSkills(bound)
  if (command === 'list') return cmdList(bound)
  if (command === 'catalog') return cmdCatalog(argv.slice(1), bound)
  if (command === 'add') return cmdAdd(argv.slice(1), bound)
  if (command === 'install') return cmdInstall(argv.slice(1), bound)
  if (command === 'update') return cmdUpdate(argv.slice(1), bound)
  if (command === 'remove') return cmdRemove(argv.slice(1), bound)

  throw new Error(`未知命令: dwy skills ${argv.join(' ')}`)
}
