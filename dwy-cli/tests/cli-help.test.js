import test from 'node:test'
import assert from 'node:assert/strict'
import { buildHelpText } from '../src/cli-help.js'

test('dwy --help lists sync and upgrade, no hidden commands', () => {
  const help = buildHelpText('0.0.0')
  assert.match(help, /dwy sync/)
  assert.match(help, /dwy upgrade/)
  assert.match(help, /刷新全局外部 skill/)
  assert.doesNotMatch(help, /dwy skills/)
  assert.doesNotMatch(help, /dwy scene/)
  assert.doesNotMatch(help, /隐藏命令/)
})
