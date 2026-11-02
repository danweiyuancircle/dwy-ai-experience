import test from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
import { buildHelpText } from '../src/cli-help.js'

test('dwy --help lists sync and upgrade, no hidden commands', () => {
  const help = buildHelpText('0.0.0')
  assert.match(help, /dwy sync/)
  assert.match(help, /dwy upgrade/)
  assert.match(help, /dwy refresh/)
  assert.match(help, /dwy migrate/)
  assert.match(help, /同步步骤/)
  assert.match(help, /交互按键/)
  assert.match(help, /常见用法/)
  assert.match(help, /cd your-project/)
  assert.match(help, /npm install -g create-dwy@latest/)
  assert.match(help, /共享.*Skills/)
  assert.match(help, /备份/)
  assert.match(help, /全局.*项目/)
  assert.doesNotMatch(help, /dwy skills/)
  assert.doesNotMatch(help, /dwy scene/)
  assert.doesNotMatch(help, /隐藏命令/)
})

test('帮助说明显式范围、内容选择与共享副本更新边界', () => {
  const help = buildHelpText('0.0.0')
  assert.match(help, /1\. 选择同步范围/)
  assert.match(help, /2\. 选择.*平台/)
  assert.match(help, /3\. 选择本次处理内容.*默认只选 Skills/)
  assert.match(help, /未选择的类型保持原样/)
  assert.match(help, /全局已启用.*不能重复勾选/)
  assert.match(help, /部分平台.*缺少全局入口/)
  assert.match(help, /sync.*migrate.*不刷新已有共享内容/)
  assert.doesNotMatch(help, /位置选择只影响|Hooks 按平台自动同步，无需选择/)
})

test('dwy 启动展示品牌，取消后退出', async t => {
  const { spawn } = await import('node:child_process')
  const child = spawn(process.execPath, ['dwy-cli/bin/index.js'], {
    cwd: new URL('../../', import.meta.url),
    // 取消交互不依赖远端认证，也不能更新开发者的共享模板缓存。
    env: { ...process.env, FORCE_COLOR: '0', DWY_TEMPLATE_SOURCE_DIR: fileURLToPath(new URL('../templates/ai-tools', import.meta.url)) },
  })
  t.after(() => child.kill())
  let output = ''
  let cancelled = false
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => { child.kill(); reject(new Error('dwy 启动超时')) }, 5000)
    child.stdout.on('data', chunk => {
      output += chunk.toString()
      if (!cancelled && output.includes('选择同步范围')) {
        cancelled = true
        setTimeout(() => child.stdin.write('\u001b'), 30)
      }
    })
    child.stderr.on('data', chunk => { output += chunk.toString() })
    child.on('error', reject)
    child.on('close', code => {
      clearTimeout(timer)
      assert.equal(code, 0, output)
      resolve()
    })
  })
  assert.match(output, /\bdwy\b/)
  assert.ok(output.indexOf('dwy') < output.indexOf('选择同步范围'))
  assert.match(output, /已取消/)
  assert.doesNotMatch(output, /选择要做的事|初始化/)
})
