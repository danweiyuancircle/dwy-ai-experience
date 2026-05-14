#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { program } from 'commander'
import { createProject } from '../src/create.js'
import { syncClaude } from '../src/sync.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))

program
  .name('dwy')
  .description('项目脚手架与 Claude Code 配置管理工具')
  .version(pkg.version)

program
  .command('create [name]')
  .description('从模板创建新项目')
  .action(createProject)
  .addHelpText('after', `
Examples:
  $ dwy create
  $ dwy create my-app
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

program.parse()
