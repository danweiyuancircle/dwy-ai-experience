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
  .description('交互式选择并同步 Claude Code 配置（skills/rules/commands/settings.json → 项目 .claude/；CLAUDE.md → 全局 ~/.claude/）')
  .action(syncClaude)

program
  .command('sync-claude-md')
  .description('单独同步 CLAUDE.md 到全局 ~/.claude/')
  .action(syncProjectClaudeMd)

program.parse()
