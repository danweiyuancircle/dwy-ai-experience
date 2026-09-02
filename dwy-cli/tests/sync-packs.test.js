import test from 'node:test'
import assert from 'node:assert/strict'
import {
  SCENE_PACKS,
  STACK_PACKS,
  expandPackSelection,
  normalizePacks,
} from '../src/sync-packs.js'
import { buildPackItemOptions, packOptionsWithChildren, splitPackItemKeys } from '../src/sync-scene.js'

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

test('技术栈选项下列出子条目，整包可勾、子条目只展示', () => {
  const scans = buildScans()
  const vue = STACK_PACKS.find(pack => pack.id === 'vue')
  const options = packOptionsWithChildren([vue], scans)
  assert.equal(options[0].value, 'vue')
  assert.match(options[0].label, /Vue（/)
  assert.match(options[0].description, /dwy-vue-core\.md/)
  assert.ok(options.some(option => option.disabled && option.packId === 'vue' && option.label.includes('dwy-vue-core.md')))
  assert.ok(options.some(option => option.disabled && option.packId === 'vue' && option.label.includes('dwy-eui')))
})

test('场景包选项下列出子条目，整包可勾、子条目只展示', () => {
  const scans = buildScans()
  const product = SCENE_PACKS.find(pack => pack.id === 'product-0to1')
  const options = packOptionsWithChildren([product], scans)
  assert.equal(options[0].value, 'product-0to1')
  assert.match(options[0].label, /产品0到1（/)
  assert.match(options[0].description, /dwy-product-launcher/)
  assert.ok(options.some(option => option.disabled && option.label.includes('dwy-product-launcher')))
})

test('包展开子条目默认全勾，取消某条后从结果里拿掉', () => {
  const expanded = expandPackSelection(buildScans(), { stacks: ['common', 'vue'], scenes: [] })
  const options = buildPackItemOptions(expanded, ['common', 'vue'])
  assert.ok(options.every(option => option.value.includes(':')))
  assert.ok(options.some(option => option.label.includes(' / ')))

  const withoutEui = options
    .map(option => option.value)
    .filter(value => value !== 'skills:dwy-eui')
  const tuned = splitPackItemKeys(expanded, withoutEui)
  assert.ok(!tuned.skills.some(item => item.name === 'dwy-eui'))
  assert.ok(tuned.skills.some(item => item.name === 'dwy-shared'))
})

test('包目录 id 稳定，供按包勾选与 sync-state 使用', () => {
  assert.deepEqual(STACK_PACKS.map(pack => pack.id), [
    'common', 'vue', 'python', 'ios', 'android', 'flutter', 'harmony', 'docker', 'database',
  ])
  assert.deepEqual(SCENE_PACKS.map(pack => pack.id), [
    'product-0to1', 'media', 'release', 'security', 'article', 'dolphindb',
  ])
})
