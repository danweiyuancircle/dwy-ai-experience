#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { program } from 'commander'
import { createProject } from '../src/create.js'
import { syncClaude, syncProjectClaude } from '../src/sync.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))

program
  .name('dwy')
  .description('Project scaffolding and Claude Code config sync')
  .version(pkg.version)

program
  .command('create [name]')
  .description('Create a new project from template')
  .action(createProject)

program
  .command('sync <target>')
  .description('Sync configuration (claude | project-claude)')
  .action(async (target) => {
    if (target === 'claude') {
      await syncClaude()
    } else if (target === 'project-claude') {
      await syncProjectClaude()
    } else {
      console.error(`Unknown sync target: ${target}. Use "claude" or "project-claude".`)
      process.exit(1)
    }
  })

program.parse()
