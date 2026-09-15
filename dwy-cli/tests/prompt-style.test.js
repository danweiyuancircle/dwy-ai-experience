import test from 'node:test'
import assert from 'node:assert/strict'
import {
  formatCheckboxRow,
  formatRadioRow,
} from '../src/prompt-style.js'

/** 去掉 ANSI，模拟 dim/颜色都失效的终端。 */
function stripAnsi(text) {
  return text.replace(/\x1b\[[0-9;]*m/g, '')
}

test('多选：已勾选时聚焦行去掉 ANSI 后仍和未聚焦行不同', () => {
  const active = formatCheckboxRow({ label: 'dwy-eui', selected: true, active: true })
  const inactive = formatCheckboxRow({ label: 'dwy-eui', selected: true, active: false })
  assert.notEqual(stripAnsi(active), stripAnsi(inactive))
})

test('多选：未勾选时聚焦行去掉 ANSI 后仍和未聚焦行不同', () => {
  const active = formatCheckboxRow({ label: 'dwy-eui', selected: false, active: true })
  const inactive = formatCheckboxRow({ label: 'dwy-eui', selected: false, active: false })
  assert.notEqual(stripAnsi(active), stripAnsi(inactive))
})

test('多选：聚焦行有指针，未聚焦行没有', () => {
  const active = stripAnsi(formatCheckboxRow({ label: 'dwy-eui', selected: true, active: true }))
  const inactive = stripAnsi(formatCheckboxRow({ label: 'dwy-eui', selected: true, active: false }))
  assert.match(active, /[›>]/)
  assert.doesNotMatch(inactive, /[›>]/)
})

test('多选：prefix 出现在文案前', () => {
  const line = stripAnsi(formatCheckboxRow({
    label: 'dwy-eui',
    selected: false,
    active: false,
    prefix: 'skill',
  }))
  assert.match(line, /skill.*dwy-eui/)
})

test('单选：聚焦行去掉 ANSI 后仍和未聚焦行不同', () => {
  const active = formatRadioRow({ label: '同步项目配置', active: true })
  const inactive = formatRadioRow({ label: '同步项目配置', active: false })
  assert.notEqual(stripAnsi(active), stripAnsi(inactive))
  assert.match(stripAnsi(active), /[›>]/)
  assert.doesNotMatch(stripAnsi(inactive), /[›>]/)
})
