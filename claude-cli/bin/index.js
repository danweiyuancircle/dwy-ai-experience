#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { program } from 'commander'
import { createProject } from '../src/create.js'
import { syncClaude, syncProjectClaudeMd } from '../src/sync.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))

program
  .name('dwy')
  .description('项目脚手架与 Claude Code 配置同步工具')
  .version(pkg.version)

program
  .command('create [name]')
  .description('从模板创建新项目')
  .action(createProject)

program
  .command('sync')
  .description('同步 Claude Code 配置到项目 .claude/（默认覆盖已选项；CLAUDE.md → 全局 ~/.claude/）')
  .option('--no-cache', '忽略已选缓存，重新交互式选择（已选项默认勾选）')
  .action((opts) => syncClaude(opts))

program
  .command('sync-claude-md')
  .description('单独同步 CLAUDE.md 到全局 ~/.claude/')
  .action(syncProjectClaudeMd)

program.parse()
