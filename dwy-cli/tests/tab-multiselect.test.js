import test from 'node:test'
import assert from 'node:assert/strict'
import {
  firstTabWithSelection,
  formatItemTypePrefix,
  itemTypeMeta,
  tabBarSegments,
  tabSelectionStats,
  tabWindow,
  toggleTabValues,
} from '../src/tab-multiselect.js'

/** 单 Tab 测试夹具。options 只要 value。 */
function tab(id, values) {
  return { id, label: id, options: values.map(value => ({ value, label: value })) }
}

test('tabSelectionStats 按当前 value 计本 Tab 已勾数', () => {
  const t = tab('vue', ['a', 'b', 'c'])
  assert.deepEqual(tabSelectionStats(t, ['a', 'c', 'other']), { selected: 2, total: 3 })
  assert.deepEqual(tabSelectionStats(t, []), { selected: 0, total: 3 })
})

test('toggleTabValues 未全勾则补全，已全勾则清空本 Tab，不动其它 Tab', () => {
  const tabValues = ['vue:a', 'vue:b']
  assert.deepEqual(
    toggleTabValues(['vue:a', 'keep'], tabValues).sort(),
    ['keep', 'vue:a', 'vue:b'],
  )
  assert.deepEqual(
    toggleTabValues(['vue:a', 'vue:b', 'keep'], tabValues),
    ['keep'],
  )
})

test('firstTabWithSelection 落在第一个有已选项的 Tab，否则 0', () => {
  const tabs = [tab('common', ['c1']), tab('vue', ['v1']), tab('ios', ['i1'])]
  assert.equal(firstTabWithSelection(tabs, ['v1']), 1)
  assert.equal(firstTabWithSelection(tabs, []), 0)
  assert.equal(firstTabWithSelection([], ['x']), 0)
})

test('tabBarSegments 文案含 已选/总数', () => {
  const tabs = [tab('通用', ['a', 'b']), tab('Vue', ['c'])]
  assert.deepEqual(tabBarSegments(tabs, ['a']), ['通用 1/2', 'Vue 0/1'])
})

test('tabWindow 以当前 Tab 为中心裁切，超出宽度两端出省略标记', () => {
  const segs = ['AAAAAA', 'BBBBBB', 'CCCCCC', 'DDDDDD', 'EEEEEE']
  const win = tabWindow(segs, 0, 16)
  assert.equal(win.start, 0)
  assert.ok(win.end < segs.length)
  assert.equal(win.showLeft, false)
  assert.equal(win.showRight, true)

  const mid = tabWindow(segs, 2, 16)
  assert.ok(mid.start <= 2 && mid.end > 2)
  assert.equal(mid.showLeft, mid.start > 0)
  assert.equal(mid.showRight, mid.end < segs.length)
})

test('itemTypeMeta 三种类型用不同词和图标，未知类型当 skill', () => {
  assert.equal(itemTypeMeta('skills').word, 'skill')
  assert.equal(itemTypeMeta('skills').title, '技能')
  assert.equal(itemTypeMeta('rules').word, 'rule')
  assert.equal(itemTypeMeta('rules').title, '规则')
  assert.equal(itemTypeMeta('hooks').word, 'hook')
  assert.equal(itemTypeMeta('hooks').title, '钩子')
  assert.equal(itemTypeMeta('nope').word, 'skill')
  assert.notEqual(itemTypeMeta('skills').icon, itemTypeMeta('rules').icon)
  assert.notEqual(itemTypeMeta('rules').icon, itemTypeMeta('hooks').icon)
})

test('formatItemTypePrefix 含类型词，三种互不相同', () => {
  const skill = formatItemTypePrefix('skills')
  const rule = formatItemTypePrefix('rules')
  const hook = formatItemTypePrefix('hooks')
  assert.match(skill, /skill/)
  assert.match(rule, /rule/)
  assert.match(hook, /hook/)
  assert.notEqual(skill, rule)
  assert.notEqual(rule, hook)
})

test('tabWindow 相邻 group 不同时预留分隔宽度', () => {
  const segs = ['AAAA', 'BBBB']
  const without = tabWindow(segs, 0, 11)
  const withSep = tabWindow(segs, 0, 11, ['stack', 'scene'])
  assert.equal(without.end, 2)
  assert.equal(withSep.end, 1)
})

test('tabWindow 当前段比宽度还长时仍露出这一段', () => {
  const win = tabWindow(['VERY-LONG-TAB-LABEL'], 0, 8)
  assert.deepEqual(win, { start: 0, end: 1, showLeft: false, showRight: false })
})
