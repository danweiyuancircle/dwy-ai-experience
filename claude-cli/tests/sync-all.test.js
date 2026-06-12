import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { syncAll } from '../src/sync-all.js'

test('syncAll mirrors one cached selection to Claude Code and Codex', async t => {
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

  await syncAll({ sourceDir, projectDir })

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
