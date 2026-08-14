#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { syncAll } from '../src/sync-all.js'
import { installSkills } from '../src/skills-install.js'
import { buildHelpText, buildSkillsHelpText } from '../src/cli-help.js'

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

function printSkillsHelp() {
  console.log(buildSkillsHelpText())
}

if (argv[0] === 'skills') {
  const rest = argv.slice(1)
  if (rest.length === 0 || wantsHelp(rest) || rest[0] === 'help') {
    printSkillsHelp()
  } else if (rest[0] === 'install') {
    await installSkills()
  } else {
    console.error(`未知命令: dwy skills ${rest.join(' ')}`)
    printSkillsHelp()
    process.exitCode = 1
  }
} else if (wantsHelp(argv)) {
  printHelp()
} else if (argv.includes('--version') || argv.includes('-V')) {
  console.log(pkg.version)
} else if (argv.length === 0 || argv[0] === 'sync') {
  await syncAll()
} else {
  console.error(`未知命令: ${argv.join(' ')}`)
  printHelp()
  process.exitCode = 1
}
