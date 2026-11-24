import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import {
  loadCatalog,
  addCatalogEntry,
  removeCatalogEntry,
  exportCatalog,
  importCatalog,
  catalogPath,
} from '../src/skills-catalog.js'

async function tempHome() {
  return fs.mkdtemp(path.join(os.tmpdir(), 'dwy-skills-catalog-'))
}

test('empty home loads versioned empty catalog', async () => {
  const home = await tempHome()
  const catalog = await loadCatalog(home)
  assert.equal(catalog.version, 1)
  assert.deepEqual(catalog.entries, [])
})

test('add upserts by id and export/import roundtrip', async () => {
  const home = await tempHome()
  await addCatalogEntry(home, {
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['react-best-practices'],
    agents: ['claude-code'],
  })
  await addCatalogEntry(home, {
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['react-best-practices', 'web-design'],
    agents: ['claude-code', 'codex'],
  })
  let catalog = await loadCatalog(home)
  assert.equal(catalog.entries.length, 1)
  assert.deepEqual(catalog.entries[0].skills, ['react-best-practices', 'web-design'])

  const out = path.join(home, 'exported.json')
  await exportCatalog(home, out)
  const home2 = await tempHome()
  await importCatalog(home2, out)
  catalog = await loadCatalog(home2)
  assert.equal(catalog.entries[0].source, 'vercel-labs/agent-skills')

  await removeCatalogEntry(home2, catalog.entries[0].id)
  assert.equal((await loadCatalog(home2)).entries.length, 0)
  assert.equal(catalogPath(home), path.join(home, '.dwy', 'skills-catalog', 'catalog.json'))
})

test('rejects absolute path fields and unknown kind', async () => {
  const home = await tempHome()
  await assert.rejects(
    () => addCatalogEntry(home, { kind: 'skills-cli', source: '/tmp/skill' }),
    /绝对路径/,
  )
  await assert.rejects(
    () => addCatalogEntry(home, { kind: 'other', source: 'a/b' }),
    /kind/,
  )
})
