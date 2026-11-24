import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { addCatalogEntry, loadCatalog } from '../src/skills-catalog.js'
import { runSkillsCommand } from '../src/skills-cmd.js'

async function tempHome() {
  return fs.mkdtemp(path.join(os.tmpdir(), 'dwy-skills-cmd-'))
}

test('catalog add export import install --yes runs official command', async () => {
  const home = await tempHome()
  await runSkillsCommand(['add', 'vercel-labs/agent-skills'], { homeDir: home })
  const catalog = await loadCatalog(home)
  assert.equal(catalog.entries.length, 1)

  const exported = path.join(home, 'out.json')
  await runSkillsCommand(['catalog', 'export', exported], { homeDir: home })

  const home2 = await tempHome()
  await runSkillsCommand(['catalog', 'import', exported], { homeDir: home2 })
  assert.equal((await loadCatalog(home2)).entries.length, 1)

  const calls = []
  const result = await runSkillsCommand(['install', '--all', '--yes'], {
    homeDir: home2,
    runCommand: async (cmd, args) => { calls.push([cmd, ...args]) },
  })
  assert.equal(result.ok.length, 1)
  assert.equal(calls[0][0], 'npx')
  assert.ok(calls[0].includes('vercel-labs/agent-skills'))
})

test('cancel confirm does not run commands', async () => {
  const home = await tempHome()
  await addCatalogEntry(home, { kind: 'skills-cli', source: 'owner/repo' })
  const calls = []
  const result = await runSkillsCommand(['install', '--all'], {
    homeDir: home,
    confirmFn: async () => false,
    runCommand: async (...args) => { calls.push(args) },
  })
  assert.equal(result.cancelled, true)
  assert.equal(calls.length, 0)
})

test('remove rejects dwy template skill names', async () => {
  const home = await tempHome()
  await assert.rejects(
    () => runSkillsCommand(['remove', 'dwy-publish', '--yes'], {
      homeDir: home,
      templateSkillNames: ['dwy-publish'],
      runCommand: async () => {
        throw new Error('should not run')
      },
    }),
    /dwy 模板 Skill/,
  )
})

test('interactive install cancel before confirm has no runner calls', async () => {
  const home = await tempHome()
  await addCatalogEntry(home, { kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' })
  const calls = []
  const result = await runSkillsCommand([], {
    homeDir: home,
    selectFn: async () => 'install',
    multiselectFn: async () => ['feature-dev@claude-plugins-official'],
    confirmFn: async () => false,
    runCommand: async (...args) => { calls.push(args) },
  })
  assert.equal(result.cancelled, true)
  assert.equal(calls.length, 0)
})
