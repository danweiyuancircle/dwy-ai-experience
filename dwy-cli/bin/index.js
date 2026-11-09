#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { runDwy, migrateSkills, refreshAll } from '../src/sync-all.js'
import { selfUpgrade } from '../src/self-upgrade.js'
import { buildHelpText } from '../src/cli-help.js'
import { manageTemplateSource } from '../src/template-source.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))
const argv = process.argv.slice(2)

/** 是否请求帮助（含 -h / --help / help） */
function wantsHelp(args) {
  return args.includes('--help') || args.includes('-h') || args[0] === 'help'
}

function printHelp() {
  console.log(buildHelpText(pkg.version))
}

if (wantsHelp(argv)) {
  printHelp()
} else if (argv.includes('--version') || argv.includes('-V')) {
  console.log(pkg.version)
} else if (['upgrade', 'refresh', 'migrate', 'source'].includes(argv[0])) {
  if (argv.length > (argv[0] === 'source' ? 2 : 1)) {
    console.error(`未知命令: dwy ${argv.join(' ')}`)
    printHelp()
    process.exitCode = 1
  } else {
    try {
      if (argv[0] === 'upgrade') await selfUpgrade()
      if (argv[0] === 'refresh') await refreshAll()
      if (argv[0] === 'migrate') await migrateSkills()
      if (argv[0] === 'source') await manageTemplateSource(argv[1])
    } catch (error) {
      console.error(error.message)
      process.exitCode = 1
    }
  }
} else if (argv.length === 0 || argv[0] === 'sync') {
  await runDwy()
} else {
  console.error(`未知命令: ${argv.join(' ')}`)
  printHelp()
  process.exitCode = 1
}
