import test from 'node:test'
import assert from 'node:assert/strict'
import { buildHelpText, buildSkillsHelpText } from '../src/cli-help.js'

test('dwy --help lists skills install as a first-class command', () => {
  const help = buildHelpText('0.0.0')
  assert.match(help, /dwy skills install/)
  assert.doesNotMatch(help, /隐藏命令/)
})

test('dwy skills --help lists install and does not hide it', () => {
  const help = buildSkillsHelpText()
  assert.match(help, /dwy skills install/)
  assert.match(help, /~\/\.dwy\/skills/)
  assert.doesNotMatch(help, /隐藏命令/)
})
