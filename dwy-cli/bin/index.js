#!/usr/bin/env node

import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'
import { syncAll } from '../src/sync-all.js'
import { installSkills } from '../src/skills-install.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pkg = JSON.parse(readFileSync(resolve(__dirname, '..', 'package.json'), 'utf-8'))
const argv = process.argv.slice(2)

function printHelp() {
  const lines = [
    `dwy ${pkg.version}`,
    '',
    'Usage:',
    '  dwy               运行交互式同步',
    '  dwy sync          运行交互式同步',
    '  dwy skills install  安装/更新全局外部 skill 到 ~/.dwy/skills/',
    '  dwy --help        显示本说明',
    '  dwy -h            显示本说明',
    '  dwy --version     显示当前版本',
    '  dwy -V            显示当前版本',
    '',
  ]
  console.log(lines.join('\n'))
}

if (argv.includes('--help') || argv.includes('-h') || argv[0] === 'help') {
  printHelp()
} else if (argv.includes('--version') || argv.includes('-V')) {
  console.log(pkg.version)
} else if (argv[0] === 'skills' && argv[1] === 'install') {
  await installSkills()
} else if (argv.length === 0 || argv[0] === 'sync') {
  await syncAll()
} else {
  console.error(`未知命令: ${argv.join(' ')}`)
  printHelp()
  process.exitCode = 1
}
