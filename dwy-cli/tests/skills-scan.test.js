import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { addCatalogEntry } from '../src/skills-catalog.js'
import { scanInstalledSkills, parseClaudePluginList, parseCodexPluginList } from '../src/skills-scan.js'

async function tempHome() {
  return fs.mkdtemp(path.join(os.tmpdir(), 'dwy-skills-scan-'))
}

async function writeSkill(root, name) {
  const dir = path.join(root, name)
  await fs.ensureDir(dir)
  await fs.writeFile(path.join(dir, 'SKILL.md'), `---\nname: ${name}\ndescription: test\n---\n`)
}

test('parseClaudePluginList extracts name@marketplace', () => {
  const text = `
Installed plugins:

  ❯ feature-dev@claude-plugins-official
    Version: 1.0.0
    Scope: user

  ❯ code-review@claude-plugins-official
    Status: enabled
`
  assert.deepEqual(parseClaudePluginList(text), [
    'feature-dev@claude-plugins-official',
    'code-review@claude-plugins-official',
  ])
})

test('scan marks catalog, dwy-template and unknown', async () => {
  const home = await tempHome()
  await writeSkill(path.join(home, '.claude', 'skills'), 'find-skills')
  await writeSkill(path.join(home, '.claude', 'skills'), 'dwy-publish')
  await writeSkill(path.join(home, '.agents', 'skills'), 'mystery-skill')

  await addCatalogEntry(home, {
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['find-skills'],
    agents: ['claude-code'],
  })
  await addCatalogEntry(home, {
    kind: 'claude-plugin',
    source: 'feature-dev@claude-plugins-official',
  })
  await addCatalogEntry(home, {
    kind: 'codex-plugin',
    source: 'browser@openai-bundled',
  })

  const result = await scanInstalledSkills({
    homeDir: home,
    templateSkillNames: new Set(['dwy-publish']),
    listPlugins: async () => ['feature-dev@claude-plugins-official', 'other@x'],
    listCodexPlugins: async () => ['browser@openai-bundled', 'warp@codex-warp'],
  })

  const byName = Object.fromEntries(result.skills.map(item => [item.name, item]))
  assert.equal(byName['find-skills'].provenance, 'catalog')
  assert.equal(byName['dwy-publish'].provenance, 'dwy-template')
  assert.equal(byName['mystery-skill'].provenance, 'unknown')
  assert.ok(byName['mystery-skill'].agents.includes('agents'))

  const plugins = Object.fromEntries(result.plugins.map(item => [`${item.runtime}:${item.source}`, item]))
  assert.equal(plugins['claude:feature-dev@claude-plugins-official'].provenance, 'catalog')
  assert.equal(plugins['claude:other@x'].provenance, 'unknown')
  assert.equal(plugins['codex:browser@openai-bundled'].provenance, 'catalog')
  assert.equal(plugins['codex:warp@codex-warp'].provenance, 'unknown')
})

test('parseCodexPluginList reads installed pluginId from JSON', () => {
  const json = JSON.stringify({
    installed: [
      { pluginId: 'browser@openai-bundled', installed: true },
      { name: 'warp', marketplaceName: 'codex-warp', installed: true },
    ],
    available: [],
  })
  assert.deepEqual(parseCodexPluginList(json), [
    'browser@openai-bundled',
    'warp@codex-warp',
  ])
})

test('parseCodexPluginList ignores trailing stderr noise after JSON', () => {
  const json = JSON.stringify({
    installed: [{ pluginId: 'slack@openai-curated', installed: true }],
    available: [],
  })
  const noisy = `${json}\nWarning: failed to list remote marketplace plugins\n`
  // JSON.parse 整段会失败，回退到 name@marketplace 文本抽取仍应命中已装项
  assert.deepEqual(parseCodexPluginList(noisy), ['slack@openai-curated'])
})
