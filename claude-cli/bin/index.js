#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { program } from 'commander'
import { createProject } from '../src/create.js'
import { syncClaude } from '../src/sync.js'
import { syncCodex } from '../src/sync-codex.js'
import { syncAll } from '../src/sync-all.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))

program
  .name('dwy')
  .description('项目脚手架与 Claude Code 配置管理工具')
  .version(pkg.version)
  .addHelpText('after', `
Examples:
  $ dwy create my-app              创建新项目
  $ dwy sync                       同步 Claude Code 与 Codex 配置（只选择一次）
  $ dwy sync -i                    重新交互式选择后同步到 Claude Code 与 Codex
  $ dwy sync md                    同步 CLAUDE.md 到 ~/.claude/ 与 ~/.codex/AGENTS.md
  $ dwy claude sync                同步 Claude 配置（基于已选覆盖）
  $ dwy claude sync -i             重新交互式选择
  $ dwy claude sync --dry-run      预演同步，不写入文件
  $ dwy claude sync md             仅同步 CLAUDE.md 到 ~/.claude/
  $ dwy codex sync                 同步配置到项目（AGENTS.md / .agents/skills / .codex）
  $ dwy codex sync -i              重新交互式选择
  $ dwy codex sync md              仅同步 CLAUDE.md 到 ~/.codex/AGENTS.md
`)

program
  .command('create [name]')
  .description('从模板创建新项目')
  .action(createProject)
  .addHelpText('after', `
Examples:
  $ dwy create
  $ dwy create my-app
`)

program
  .command('sync [target]')
  .description('同步 Claude Code 与 Codex 配置（target=md 时同步 CLAUDE.md 到两个全局目录）')
  .option('-i, --reselect', '忽略已选缓存，重新交互式选择（已选项默认勾选）')
  .option('--dry-run', '预演模式，不实际写入文件')
  .action((target, opts) => syncAll({ target, ...opts }))
  .addHelpText('after', `
Examples:
  $ dwy sync                       基于已选覆盖同步到 Claude Code 与 Codex
  $ dwy sync -i                    重新交互式选择一次，同步到两端
  $ dwy sync --dry-run             预演，不写入文件
  $ dwy sync md                    同步 CLAUDE.md 到 ~/.claude/ 与 ~/.codex/AGENTS.md
`)

const claudeCmd = program
  .command('claude')
  .description('Claude Code 配置管理')

claudeCmd
  .command('sync [target]')
  .description('同步配置到项目 .claude/（target=md 时仅同步 CLAUDE.md 到 ~/.claude/）')
  .option('-i, --reselect', '忽略已选缓存，重新交互式选择（已选项默认勾选）')
  .option('--dry-run', '预演模式，不实际写入文件')
  .action((target, opts) => syncClaude({ target, ...opts }))
  .addHelpText('after', `
Examples:
  $ dwy claude sync                基于已选缓存覆盖同步
  $ dwy claude sync -i             重新交互式选择
  $ dwy claude sync --dry-run      预演，不写入文件
  $ dwy claude sync md             仅同步 CLAUDE.md 到 ~/.claude/
`)

const codexCmd = program
  .command('codex')
  .description('OpenAI Codex 配置管理')

codexCmd
  .command('sync [target]')
  .description('同步配置到项目（rules→AGENTS.md / skills→.agents/skills / hooks→.codex；target=md 时仅同步 CLAUDE.md 到 ~/.codex/AGENTS.md）')
  .option('-i, --reselect', '忽略已选缓存，重新交互式选择（已选项默认勾选）')
  .option('--dry-run', '预演模式，不实际写入文件')
  .action((target, opts) => syncCodex({ target, ...opts }))
  .addHelpText('after', `
Examples:
  $ dwy codex sync                基于已选覆盖同步
  $ dwy codex sync -i             重新交互式选择
  $ dwy codex sync --dry-run      预演，不写入文件
  $ dwy codex sync md             仅同步 CLAUDE.md 到 ~/.codex/AGENTS.md
`)

program.parse()
