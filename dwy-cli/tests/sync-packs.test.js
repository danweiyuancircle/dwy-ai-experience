import test from 'node:test'
import assert from 'node:assert/strict'
import {
  SCENE_PACKS,
  STACK_PACKS,
  expandPackSelection,
  normalizePacks,
} from '../src/sync-packs.js'
import {
  initialChildValues,
  itemsFromChildKeys,
  packChildKey,
  packGroupOptions,
  parsePackChildKey,
} from '../src/sync-scene.js'

/** 构造 expand 用的扫描结果，字段与 scanSkills/scanRules/scanHooks 对齐。 */
function buildScans() {
  return {
    skills: [
      { name: 'dwy-shared', category: '元工具' },
      { name: 'dwy-eui', category: '基础库' },
      { name: 'dwy-eapi', category: '基础库' },
      { name: 'dwy-fullstack-scaffold', category: '脚手架' },
      { name: 'dwy-docker', category: '运维发布' },
      { name: 'dwy-dolphindb', category: '数据库' },
      { name: 'dwy-semver', category: '发布发版' },
      { name: 'dwy-publish', category: '发布发版' },
      { name: 'dwy-product-launcher', category: '产品0到1' },
      { name: 'dwy-pentest', category: '安全' },
    ],
    rules: [
      { name: 'dwy-git-commit.md', category: '开发流程' },
      { name: 'dwy-vue-core.md', category: 'Vue' },
      { name: 'dwy-python-core.md', category: 'Python' },
      { name: 'dwy-postgres.md', category: '数据库' },
      { name: 'dwy-docker.md', category: 'Docker' },
    ],
    commands: [{ name: 'ghost.md', category: '文件命令' }],
    hooks: [
      { name: 'pre-git-commit-sensitive-check.sh', category: 'Git' },
    ],
  }
}

function names(items) {
  return items.map(item => item.name).sort()
}

test('normalizePacks 丢掉未知 id，去重，缺省为空数组', () => {
  assert.deepEqual(normalizePacks(undefined), { stacks: [], scenes: [] })
  assert.deepEqual(
    normalizePacks({ stacks: ['common', 'common', 'nope'], scenes: ['media', 'media'] }),
    { stacks: ['common'], scenes: ['media'] },
  )
})

test('通用 + Vue 并集去重，不含 DolphinDB skill', () => {
  const selected = expandPackSelection(buildScans(), {
    stacks: ['common', 'vue'],
    scenes: [],
  })

  assert.deepEqual(names(selected.skills), ['dwy-eui', 'dwy-fullstack-scaffold', 'dwy-semver', 'dwy-shared'])
  assert.deepEqual(names(selected.rules), ['dwy-git-commit.md', 'dwy-vue-core.md'])
  assert.deepEqual(names(selected.hooks), ['pre-git-commit-sensitive-check.sh'])
  assert.deepEqual(selected.commands, [])
  assert.ok(!names(selected.skills).includes('dwy-dolphindb'))
})

test('仅 Skills 时丢掉 rules/hooks，场景包可单独叠加', () => {
  const selected = expandPackSelection(buildScans(), {
    stacks: ['python'],
    scenes: ['release', 'dolphindb'],
    skillsOnly: true,
  })

  assert.deepEqual(names(selected.skills), ['dwy-dolphindb', 'dwy-eapi', 'dwy-fullstack-scaffold', 'dwy-publish', 'dwy-semver'])
  assert.deepEqual(selected.rules, [])
  assert.deepEqual(selected.hooks, [])
  assert.deepEqual(selected.commands, [])
})

test('数据库栈只有 postgres 类 rules，DolphinDB 必须走场景包', () => {
  const stackOnly = expandPackSelection(buildScans(), { stacks: ['database'], scenes: [] })
  assert.deepEqual(names(stackOnly.skills), [])
  assert.deepEqual(names(stackOnly.rules), ['dwy-postgres.md'])

  const withScene = expandPackSelection(buildScans(), { stacks: ['database'], scenes: ['dolphindb'] })
  assert.deepEqual(names(withScene.skills), ['dwy-dolphindb'])
})

test('groupMultiselect 分组挂可勾子项，value 带 packId', () => {
  const scans = buildScans()
  const vue = STACK_PACKS.find(pack => pack.id === 'vue')
  const groups = packGroupOptions([vue], scans)
  const title = Object.keys(groups)[0]
  assert.match(title, /Vue（/)
  const children = groups[title]
  assert.ok(children.every(option => !option.disabled))
  assert.ok(children.some(option => option.value === 'vue:rules:dwy-vue-core.md'))
  assert.ok(children.some(option => option.value === 'vue:skills:dwy-eui'))
})

test('场景包同样按组列出可勾子项', () => {
  const scans = buildScans()
  const product = SCENE_PACKS.find(pack => pack.id === 'product-0to1')
  const groups = packGroupOptions([product], scans)
  const title = Object.keys(groups)[0]
  assert.match(title, /产品0到1（/)
  assert.ok(groups[title].some(option => option.value === 'product-0to1:skills:dwy-product-launcher'))
})

test('扫描无匹配项的包不进分组，避免空组被当成已全选', () => {
  const groups = packGroupOptions(
    [{ id: 'ios', label: 'iOS', ruleCategories: ['iOS'] }],
    { skills: [], rules: [], hooks: [] },
  )
  assert.deepEqual(groups, {})
})

test('取消某个子项后结果不含该项，仍记所属包', () => {
  const scans = buildScans()
  const vue = STACK_PACKS.find(pack => pack.id === 'vue')
  const children = Object.values(packGroupOptions([vue], scans))[0]
  const keys = children.map(option => option.value).filter(value => value !== 'vue:skills:dwy-eui')
  const picked = itemsFromChildKeys(keys, scans)
  assert.deepEqual(picked.packIds, ['vue'])
  assert.ok(!picked.skills.some(item => item.name === 'dwy-eui'))
  assert.ok(picked.rules.some(item => item.name === 'dwy-vue-core.md'))
})

test('某包子项全取消则不再记该包', () => {
  const scans = buildScans()
  const picked = itemsFromChildKeys(['common:skills:dwy-shared'], scans)
  assert.deepEqual(picked.packIds, ['common'])
  assert.deepEqual(names(picked.skills), ['dwy-shared'])
  assert.deepEqual(picked.rules, [])
})

test('默认包展开成全部子 value，供 initialValues 预勾', () => {
  const scans = buildScans()
  const values = initialChildValues(STACK_PACKS, scans, ['common'])
  assert.ok(values.length > 0)
  assert.ok(values.every(value => value.startsWith('common:')))
  assert.ok(values.includes('common:skills:dwy-shared'))
})

test('跨包同名 skill 的 child key 互不覆盖', () => {
  const scans = buildScans()
  const groups = packGroupOptions(
    STACK_PACKS.filter(pack => pack.id === 'vue' || pack.id === 'python'),
    scans,
  )
  const vueTitle = Object.keys(groups).find(title => title.startsWith('Vue'))
  const pythonTitle = Object.keys(groups).find(title => title.startsWith('Python'))
  const vueKeys = groups[vueTitle].map(option => option.value)
  const pythonKeys = groups[pythonTitle].map(option => option.value)
  assert.ok(vueKeys.includes('vue:skills:dwy-fullstack-scaffold'))
  assert.ok(pythonKeys.includes('python:skills:dwy-fullstack-scaffold'))
  const onlyVue = itemsFromChildKeys(vueKeys, scans)
  assert.ok(onlyVue.skills.some(item => item.name === 'dwy-fullstack-scaffold'))
  assert.equal(parsePackChildKey('vue:skills:dwy-eui').packId, 'vue')
  assert.equal(packChildKey('vue', 'skills', 'dwy-eui'), 'vue:skills:dwy-eui')
})

test('skillsOnly 分组只含子 skill，解析结果不含 rules/hooks', () => {
  const scans = buildScans()
  const vue = STACK_PACKS.find(pack => pack.id === 'vue')
  const groups = packGroupOptions([vue], scans, { skillsOnly: true })
  const children = Object.values(groups)[0]
  assert.ok(children.every(option => option.value.startsWith('vue:skills:')))
  const picked = itemsFromChildKeys(['vue:skills:dwy-eui', 'vue:rules:dwy-vue-core.md'], scans, { skillsOnly: true })
  assert.deepEqual(names(picked.skills), ['dwy-eui'])
  assert.deepEqual(picked.rules, [])
  assert.deepEqual(picked.hooks, [])
  assert.equal(parsePackChildKey('not-a-key'), null)
})

test('包目录 id 稳定，供按包勾选与 sync-state 使用', () => {
  assert.deepEqual(STACK_PACKS.map(pack => pack.id), [
    'common', 'vue', 'python', 'ios', 'android', 'flutter', 'harmony', 'docker', 'database',
  ])
  assert.deepEqual(SCENE_PACKS.map(pack => pack.id), [
    'product-0to1', 'media', 'release', 'security', 'article', 'dolphindb',
  ])
})
