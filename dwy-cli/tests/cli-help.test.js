import test from 'node:test'
import assert from 'node:assert/strict'
import { buildHelpText } from '../src/cli-help.js'

test('dwy --help lists sync and upgrade, no hidden commands', () => {
  const help = buildHelpText('0.0.0')
  assert.match(help, /dwy sync/)
  assert.match(help, /dwy upgrade/)
  assert.match(help, /同步步骤/)
  assert.match(help, /交互按键/)
  assert.match(help, /常见用法/)
  assert.match(help, /cd your-project/)
  assert.match(help, /npm install -g create-dwy@latest/)
  assert.match(help, /本地配置需再执行 dwy sync 更新/)
  assert.match(help, /全局.*项目/)
  assert.doesNotMatch(help, /dwy skills/)
  assert.doesNotMatch(help, /dwy scene/)
  assert.doesNotMatch(help, /隐藏命令/)
})

test('dwy 启动展示品牌，取消后退出', async t => {
  const { spawn } = await import('node:child_process')
  const child = spawn(process.execPath, ['dwy-cli/bin/index.js'], {
    cwd: new URL('../../', import.meta.url),
    env: { ...process.env, FORCE_COLOR: '0' },
  })
  t.after(() => child.kill())
  let output = ''
  let cancelled = false
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => { child.kill(); reject(new Error('dwy 启动超时')) }, 5000)
    child.stdout.on('data', chunk => {
      output += chunk.toString()
      if (!cancelled && output.includes('选择 Skills')) {
        cancelled = true
        setTimeout(() => child.stdin.write('\u001b'), 30)
      }
    })
    child.stderr.on('data', chunk => { output += chunk.toString() })
    child.on('error', reject)
    child.on('close', code => {
      clearTimeout(timer)
      assert.equal(code, 0)
      resolve()
    })
  })
  assert.match(output, /\bdwy\b/)
  assert.ok(output.indexOf('dwy') < output.indexOf('选择 Skills'))
  assert.match(output, /已取消/)
  assert.doesNotMatch(output, /选择要做的事|初始化|选择同步范围/)
})
