#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { runDwy } from '../src/sync-all.js'
import { selfUpgrade } from '../src/self-upgrade.js'
import { buildHelpText } from '../src/cli-help.js'

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
} else if (argv[0] === 'upgrade') {
  if (argv.length > 1) {
    console.error(`未知命令: dwy ${argv.join(' ')}`)
    printHelp()
    process.exitCode = 1
  } else {
    try {
      await selfUpgrade()
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
