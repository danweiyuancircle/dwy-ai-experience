import test from 'node:test'
import assert from 'node:assert/strict'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { fileURLToPath } from 'node:url'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { syncAll } from '../src/sync-all.js'

const execFileAsync = promisify(execFile)
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const packageDir = path.resolve(__dirname, '..')

test('syncAll mirrors one cached selection to Claude Code and Codex', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-all-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'claude-global')
  const codexGlobalDir = path.join(tempDir, 'templates', 'codex-global')
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
  await fs.outputJson(path.join(sourceDir, 'settings.json'), {
    hooks: {
      PreToolUse: [{
        hooks: [{ type: 'command', command: '$CLAUDE_PROJECT_DIR/.claude/hooks/pre-check.sh' }],
      }],
    },
  })

  await fs.outputFile(path.join(codexGlobalDir, 'hooks', 'Git', 'pre-check.sh'), '#!/bin/sh\necho codex\n')
  await fs.outputJson(path.join(codexGlobalDir, 'hooks.json'), {
    hooks: {
      PreToolUse: [{
        hooks: [{ type: 'command', command: '$CODEX_PROJECT_DIR/.codex/hooks/pre-check.sh' }],
      }],
    },
  })

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
    '#!/bin/sh\necho codex\n',
  )

  const agentsMd = await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf-8')
  assert.match(agentsMd, /<!-- DWY-RULES:START/)
  assert.match(agentsMd, /Use Vue carefully\./)
})

test('CLI help lists the combined sync command', async () => {
  const { stdout } = await execFileAsync(process.execPath, [path.join(packageDir, 'bin', 'index.js'), '--help'])

  assert.match(stdout, /sync \[options\] \[target\]/)
  assert.match(stdout, /同步 Claude Code 与 Codex 配置/)
})
