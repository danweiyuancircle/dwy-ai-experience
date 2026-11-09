import test from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const help = execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), '--help'], {
  encoding: 'utf8',
  env: { ...process.env, FORCE_COLOR: '0' },
})

test('dwy --help lists sync and upgrade, no hidden commands', () => {
  assert.match(help, /dwy sync/)
  assert.match(help, /dwy upgrade/)
  assert.match(help, /dwy refresh/)
  assert.match(help, /dwy migrate/)
  assert.match(help, /dwy source/)
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

test('实际帮助按内容选择后选 CLI，并说明全局继承与确认边界', () => {
  const steps = [...help.matchAll(/^  \d+\. (.+)$/gm)].map(match => match[1])
  const expected = [/同步范围/, /Skills/, /AGENTS\.md.*默认启用/, /Hooks.*默认启用/, /CLI.*Codex/, /预览/, /确认/]
  assert.equal(steps.length, expected.length)
  expected.forEach((pattern, index) => assert.match(steps[index], pattern))
  assert.match(help, /恢复.*当前范围.*CLI/)
  assert.match(help, /全局.*跳过.*操作页/)
  assert.match(help, /关闭.*当前范围.*不.*全局/)
  assert.match(help, /确认前不改.*项目.*全局.*共享/)
  assert.match(help, /确认后.*共享 Skills/)
  assert.match(help, /全局已启用.*不能重复勾选/)
  assert.match(help, /部分平台.*缺少全局入口/)
  assert.doesNotMatch(help, /选择本次处理内容|范围 \/ 平台 \/ 内容|不勾选整个类型/)
  assert.doesNotMatch(help, /选择 Rules|Cursor：/)
})

test('实际帮助说明远端模板、离线缓存和 CLI 升级', () => {
  assert.match(help, /dwy refresh.*最新模板.*已安装.*共享 Skills/)
  assert.match(help, /dwy refresh.*当前项目.*全局.*规范.*Hooks.*Rules.*外部 Skills/)
  assert.match(help, /dwy upgrade.*npm.*正式版/)
  assert.match(help, /GitHub.*develop/)
  assert.match(help, /离线.*缓存.*随包/)
  assert.match(help, /DWY_TEMPLATE_SOURCE_DIR.*优先/)
  assert.match(help, /Skills.*变更.*不.*CLI.*发版/)
})

test('dwy 启动展示品牌，取消后退出', async t => {
  const { spawn } = await import('node:child_process')
  const child = spawn(process.execPath, ['dwy-cli/bin/index.js'], {
    cwd: new URL('../../', import.meta.url),
    // 使用仓库模板验证启动和取消，不依赖当前安装包的模板位置。
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
