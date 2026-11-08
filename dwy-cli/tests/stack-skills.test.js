import test from 'node:test'
import assert from 'node:assert/strict'
import path from 'node:path'
import os from 'node:os'
import fs from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { interactiveSelect, scanRules, scanSkills } from '../src/sync.js'
import { syncAll } from '../src/sync-all.js'

const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../templates/ai-tools')
const expected = ['dwy-python-development', 'dwy-python-architecture', 'dwy-python-api', 'dwy-vue-development', 'dwy-vue-architecture', 'dwy-apple-appkit', 'dwy-auth', 'dwy-payment', 'dwy-notify', 'dwy-webhooks', 'dwy-apple-notify', 'dwy-email-notify', 'dwy-wechatpay-notify', 'dwy-device-fingerprint', 'dwy-admin-kit', 'dwy-auth-web', 'dwy-android-development', 'dwy-android-architecture', 'dwy-flutter-development', 'dwy-harmony-development', 'dwy-postgres', 'dwy-redis', 'dwy-alembic']

test('语言与基础库技能可发现，引用资料存在，Python 和 Vue 规则已迁移', async () => {
  const skills = await scanSkills(source)
  for (const name of expected) {
    const skill = skills.find(item => item.name === name)
    assert.ok(skill, `缺少 ${name}`)
    const content = await fs.readFile(path.join(skill.sourcePath, 'SKILL.md'), 'utf8')
    for (const match of content.matchAll(/\]\((references\/[^)#]+\.md)\)/g)) {
      await fs.access(path.join(skill.sourcePath, match[1]))
    }
  }
  const rules = await scanRules(source)
  assert.equal(rules.filter(rule => /^dwy-(python|vue)-/.test(rule.name)).length, 0)
  assert.deepEqual(rules, [])
})

test('剩余技术栈和流程规则均有技能替代，模板不再分发 Rules', async () => {
  assert.deepEqual(await scanRules(source), [])
})

test('没有可选规则时跳过 Rules 交互', async () => {
  const selected = await interactiveSelect({ rules: [] }, { rules: new Set() }, { types: ['rules'] })
  assert.deepEqual(selected.rules, [])
})

test('无状态旧规则在确认后清理，不依赖选择技能，保留手写内容', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-rule-migration-'))
  t.after(() => fs.rm(root, { recursive: true, force: true }))
  const projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.mkdir(projectDir, { recursive: true })
  await fs.mkdir(path.join(projectDir, '.claude/rules'), { recursive: true })
  const personalRule = path.join(projectDir, '.claude/rules/dwy-python-core.md')
  await fs.writeFile(personalRule, '# 个人内容')
  const agents = path.join(projectDir, 'AGENTS.md')
  await fs.writeFile(agents, '# 手写内容\n\n<!-- DWY-RULES:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->\n\n<!-- dwy-rule: dwy-python-core.md -->\n\n# 旧规则\n\n<!-- dwy-rule: custom.md -->\n\n# 未知规则\n\n<!-- DWY-RULES:END -->\n')
  const opts = { sourceDir: source, projectDir, homeDir, codexHome: path.join(homeDir, '.codex'),
    scope: 'project', selectedPlatforms: ['codex', 'claude'], contentTypes: ['skills', 'rules'], confirmed: true }
  await syncAll({ ...opts, confirmed: false, selected: { skills: [{ name: 'dwy-python-development' }], rules: [] } })
  assert.match(await fs.readFile(agents, 'utf8'), /旧规则/)
  assert.equal(await fs.readFile(personalRule, 'utf8'), '# 个人内容')
  await syncAll({ ...opts, selected: { skills: [], rules: [] } })
  const result = await fs.readFile(agents, 'utf8')
  assert.match(result, /手写内容/)
  assert.doesNotMatch(result, /旧规则/)
  assert.match(result, /未知规则/)
  assert.equal(await fs.readFile(personalRule, 'utf8'), '# 个人内容')
  await assert.rejects(fs.access(path.join(projectDir, '.agents/skills/dwy-python-development/SKILL.md')))
})

test('多条旧托管规则清理后保留项目手写内容和未知规则', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-multi-rule-migration-'))
  t.after(() => fs.rm(root, { recursive: true, force: true }))
  const projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.mkdir(projectDir, { recursive: true })
  const names = ['dwy-android-core.md', 'dwy-android-support-only.md', 'dwy-code-craft.md', 'dwy-git-commit.md']
  const sections = [...names, 'custom.md'].map(name => `<!-- dwy-rule: ${name} -->\n\n# ${name}`)
  const agents = path.join(projectDir, 'AGENTS.md')
  await fs.writeFile(agents, `# 项目手写内容\n\n<!-- DWY-RULES:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->\n\n${sections.join('\n\n')}\n\n<!-- DWY-RULES:END -->\n`)
  await syncAll({ sourceDir: source, projectDir, homeDir, codexHome: path.join(homeDir, '.codex'),
    scope: 'project', selectedPlatforms: ['codex'], contentTypes: ['skills', 'rules'], confirmed: true,
    selected: { skills: [], rules: [] } })
  const content = await fs.readFile(agents, 'utf8')
  assert.match(content, /项目手写内容/)
  assert.match(content, /custom\.md/)
  for (const name of names) assert.ok(!content.includes(`dwy-rule: ${name}`), name)
  await assert.rejects(fs.access(path.join(projectDir, '.agents/skills/dwy-android-development/SKILL.md')))
})

test('Cursor 不支持 Skills，迁移时保留历史 Cursor 规则', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-cursor-migration-'))
  t.after(() => fs.rm(root, { recursive: true, force: true }))
  const projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  const rule = path.join(projectDir, '.cursor/rules/dwy-python-core.mdc')
  await fs.mkdir(path.dirname(rule), { recursive: true })
  await fs.writeFile(rule, '# 旧规则')
  await fs.mkdir(path.join(projectDir, '.dwy'), { recursive: true })
  await fs.writeFile(path.join(projectDir, '.dwy/sync-state.json'), JSON.stringify({ version: 1, platforms: {
    cursor: { skills: [], rules: ['dwy-python-core.md'], hooks: [], commands: [] },
  } }))
  await syncAll({ sourceDir: source, projectDir, homeDir, codexHome: path.join(homeDir, '.codex'),
    scope: 'project', selectedPlatforms: ['cursor'], contentTypes: ['rules'], confirmed: true, selected: { rules: [] } })
  assert.equal(await fs.readFile(rule, 'utf8'), '# 旧规则')
})
