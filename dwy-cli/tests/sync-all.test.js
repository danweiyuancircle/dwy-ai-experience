import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { buildSelectionDefaultsFromSyncState, syncAll } from '../src/sync-all.js'

function buildSelected() {
  return {
    skills: [
      { name: 'dwy-shared' },
    ],
    rules: [
      { name: 'dwy-vue.md' },
    ],
    commands: [
      { name: 'release.md' },
    ],
    hooks: [
      { name: 'pre-check.sh' },
    ],
  }
}

test('buildSelectionDefaultsFromSyncState prefers stored sync state selections', () => {
  const existing = {
    skills: new Set(['existing-skill']),
    rules: new Set(['existing-rule.md']),
    commands: new Set(['existing-command.md']),
    hooks: new Set(['existing-hook.sh']),
  }

  const syncState = {
    version: 1,
    platforms: {
      claude: {
        skills: ['state-skill'],
        rules: ['state-rule.md'],
        commands: ['state-command.md'],
        hooks: ['state-hook.sh'],
      },
      codex: {
        skills: ['state-skill', 'codex-skill'],
        rules: ['codex-rule.md'],
        hooks: ['codex-hook.sh'],
      },
      cursor: {
        rules: ['cursor-rule.md'],
      },
      opencode: {
        skills: ['opencode-skill'],
        commands: ['opencode-command.md'],
      },
    },
  }

  const defaults = buildSelectionDefaultsFromSyncState(existing, syncState)

  assert.deepEqual([...defaults.skills].sort(), ['codex-skill', 'opencode-skill', 'state-skill'])
  assert.deepEqual([...defaults.rules].sort(), ['codex-rule.md', 'cursor-rule.md', 'state-rule.md'])
  assert.deepEqual([...defaults.commands].sort(), ['opencode-command.md', 'state-command.md'])
  assert.deepEqual([...defaults.hooks].sort(), ['codex-hook.sh', 'state-hook.sh'])
})

test('buildSelectionDefaultsFromSyncState falls back to existing scan when sync state is empty', () => {
  const existing = {
    skills: new Set(['existing-skill']),
    rules: new Set(['existing-rule.md']),
    commands: new Set(['existing-command.md']),
    hooks: new Set(['existing-hook.sh']),
  }

  const defaults = buildSelectionDefaultsFromSyncState(existing, {
    version: 1,
    platforms: {},
  })

  assert.deepEqual([...defaults.skills], ['existing-skill'])
  assert.deepEqual([...defaults.rules], ['existing-rule.md'])
  assert.deepEqual([...defaults.commands], ['existing-command.md'])
  assert.deepEqual([...defaults.hooks], ['existing-hook.sh'])
})

test('syncAll mirrors one selected configuration to Claude Code and Codex', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-all-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'ai-tools')
  const projectDir = path.join(tempDir, 'project')

  await fs.outputFile(
    path.join(sourceDir, 'skills', '基础', 'dwy-shared', 'SKILL.md'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  await fs.outputFile(
    path.join(sourceDir, 'rules', 'Vue', 'dwy-vue.md'),
    '---\ndescription: Vue rule\npaths:\n  - "frontend/**/*.vue"\n---\n# Vue rule\nUse Vue carefully.\n',
  )
  await fs.outputFile(path.join(sourceDir, 'commands', 'release.md'), '# Release\n')
  await fs.outputFile(path.join(sourceDir, 'hooks', 'Git', 'pre-check.sh'), '#!/bin/sh\necho claude\n')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [
    {
      name: 'pre-check.sh',
      event: 'PreToolUse',
      matcher: 'Bash',
      platforms: ['claude', 'codex'],
      timeout: 30,
    },
  ])

  await fs.ensureDir(path.join(projectDir, '.claude', 'skills', 'dwy-shared'))
  await fs.outputFile(path.join(projectDir, '.claude', 'rules', 'dwy-vue.md'), 'old')
  await fs.outputFile(path.join(projectDir, '.claude', 'commands', 'release.md'), 'old')
  await fs.outputFile(path.join(projectDir, '.claude', 'hooks', 'pre-check.sh'), 'old')

  await syncAll({
    sourceDir,
    projectDir,
    selected: buildSelected(),
    selectedPlatforms: ['claude', 'codex'],
  })

  assert.equal(
    await fs.readFile(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md'), 'utf-8'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  assert.equal(
    await fs.readFile(path.join(projectDir, '.claude', 'commands', 'release.md'), 'utf-8'),
    '# Release\n',
  )
  assert.equal(
    await fs.readFile(path.join(projectDir, '.agents', 'skills', 'dwy-shared', 'SKILL.md'), 'utf-8'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  assert.equal(
    await fs.readFile(path.join(projectDir, '.codex', 'hooks', 'pre-check.sh'), 'utf-8'),
    '#!/bin/sh\necho claude\n',
  )

  const agentsMd = await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf-8')
  assert.match(agentsMd, /<!-- DWY-RULES:START/)
  assert.match(agentsMd, /Use Vue carefully\./)
})

test('syncAll keeps stale managed items until deletion is confirmed', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-all-stale-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'ai-tools')
  const projectDir = path.join(tempDir, 'project')

  await fs.outputFile(
    path.join(sourceDir, 'skills', '基础', 'dwy-shared', 'SKILL.md'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  await fs.outputFile(
    path.join(sourceDir, 'rules', 'Vue', 'dwy-vue.md'),
    '---\ndescription: Vue rule\n---\n# Vue rule\nUse Vue carefully.\n',
  )
  await fs.outputFile(path.join(sourceDir, 'commands', 'release.md'), '# Release\n')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [])

  const selected = {
    skills: [{ name: 'dwy-shared' }],
    rules: [{ name: 'dwy-vue.md' }],
    commands: [{ name: 'release.md' }],
    hooks: [],
  }

  await syncAll({
    sourceDir,
    projectDir,
    selected,
    selectedPlatforms: ['claude', 'codex', 'opencode'],
  })

  await fs.remove(path.join(sourceDir, 'skills', '基础', 'dwy-shared'))
  await fs.remove(path.join(sourceDir, 'rules', 'Vue', 'dwy-vue.md'))

  await syncAll({
    sourceDir,
    projectDir,
    selected: {
      skills: [],
      rules: [],
      commands: [{ name: 'release.md' }],
      hooks: [],
    },
    selectedPlatforms: ['claude', 'codex', 'opencode'],
    staleRemovals: {
      claude: { skills: [], rules: [] },
      codex: { skills: [], rules: [] },
      opencode: { rules: [] },
    },
  })

  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md')), true)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'rules', 'dwy-vue.md')), true)
  assert.equal(await fs.pathExists(path.join(projectDir, '.agents', 'skills', 'dwy-shared', 'SKILL.md')), true)

  const preservedAgentsMd = await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf-8')
  assert.match(preservedAgentsMd, /dwy-vue\.md/)

  await syncAll({
    sourceDir,
    projectDir,
    selected: {
      skills: [],
      rules: [],
      commands: [{ name: 'release.md' }],
      hooks: [],
    },
    selectedPlatforms: ['claude', 'codex', 'opencode'],
    staleRemovals: {
      claude: { skills: ['dwy-shared'], rules: ['dwy-vue.md'] },
      codex: { skills: ['dwy-shared'], rules: ['dwy-vue.md'] },
      opencode: { rules: ['dwy-vue.md'] },
    },
  })

  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md')), false)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'rules', 'dwy-vue.md')), false)
  assert.equal(await fs.pathExists(path.join(projectDir, '.agents', 'skills', 'dwy-shared', 'SKILL.md')), false)

  const finalAgentsMd = await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf-8')
  assert.doesNotMatch(finalAgentsMd, /dwy-vue\.md/)
})
