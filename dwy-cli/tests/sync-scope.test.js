import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { syncAll } from '../src/sync-all.js'

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-scope-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates')
  const homeDir = path.join(root, 'user home')
  const projectDir = path.join(root, 'project')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'sample', 'SKILL.md'), '# Skill')
  await fs.outputFile(path.join(sourceDir, 'rules', '通用', 'sample.md'), '# Rule')
  await fs.outputFile(path.join(sourceDir, 'hooks', '通用', 'check.sh'), '#!/bin/sh\nprintf hook-ok')
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# Baseline')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [
    { name: 'check.sh', event: 'PreToolUse', platforms: ['claude', 'codex'] },
  ])
  return { sourceDir, homeDir, codexHome: path.join(homeDir, '.codex'), projectDir, selectedPlatforms: ['claude', 'codex', 'opencode'],
    selected: { skills: [{ name: 'sample' }], rules: [{ name: 'sample.md' }], hooks: [{ name: 'check.sh' }] } }
}

test('Skills 与 Hooks 可选全局，基线固定全局且 Rules 固定项目，保留个人内容', async t => {
  const opts = await fixture(t)
  for (const relative of ['.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md']) {
    await fs.outputFile(path.join(opts.homeDir, relative), '# Personal instructions')
  }
  await fs.outputJson(path.join(opts.homeDir, '.claude/settings.json'), { model: 'personal' })
  await syncAll({ ...opts, scope: 'global' })
  const projectRules = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  assert.match(projectRules, /# Rule/)
  assert.doesNotMatch(projectRules, /# Baseline/)
  for (const relative of ['.claude/skills', '.agents/skills', '.config/opencode/skills']) {
    assert.equal(await fs.pathExists(path.join(opts.homeDir, relative, 'sample/SKILL.md')), true)
  }
  for (const relative of ['.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md']) {
    const content = await fs.readFile(path.join(opts.homeDir, relative), 'utf8')
    assert.match(content, /Personal instructions/)
    assert.match(content, /# Baseline/)
    assert.doesNotMatch(content, /# Rule/)
  }
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/AGENTS.md')), false)
  const settings = await fs.readJson(path.join(opts.homeDir, '.claude/settings.json'))
  assert.equal(settings.model, 'personal')
  const codex = await fs.readJson(path.join(opts.homeDir, '.codex/hooks.json'))
  for (const config of [settings, codex]) {
    const command = config.hooks.PreToolUse[0].hooks[0].command
    assert.equal(execFileSync('bash', ['-c', command], { cwd: opts.projectDir, env: { ...process.env, HOME: opts.homeDir }, encoding: 'utf8' }), 'hook-ok')
  }
  assert.equal(await fs.pathExists(path.join(opts.homeDir, 'AGENTS.md')), false)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy/sync-state.json')), true)
  await syncAll({ ...opts, scope: 'global' })
  for (const relative of ['.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md']) {
    const content = await fs.readFile(path.join(opts.homeDir, relative), 'utf8')
    assert.equal(content.split('# Baseline').length - 1, 1)
  }
  const repeated = await fs.readJson(path.join(opts.homeDir, '.claude/settings.json'))
  assert.equal(repeated.hooks.PreToolUse[0].hooks.length, 1)
  const projectState = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
  const globalState = await fs.readJson(path.join(opts.homeDir, '.dwy/sync-state.json'))
  for (const platform of opts.selectedPlatforms) {
    assert.deepEqual(projectState.platforms[platform].rules, ['sample.md'])
    assert.deepEqual(globalState.platforms[platform].rules, [])
  }
  await fs.remove(path.join(opts.sourceDir, 'skills/通用/sample'))
  await fs.remove(path.join(opts.sourceDir, 'rules/通用/sample.md'))
  await syncAll({ ...opts, scope: 'global', selected: { skills: [], rules: [], hooks: [] } })
  for (const relative of ['.claude/skills', '.agents/skills', '.config/opencode/skills']) {
    assert.equal(await fs.pathExists(path.join(opts.homeDir, relative, 'sample')), false)
  }
  assert.doesNotMatch(await fs.readFile(path.join(opts.homeDir, '.codex/AGENTS.md'), 'utf8'), /# Rule/)
  assert.match(await fs.readFile(path.join(opts.homeDir, '.codex/AGENTS.md'), 'utf8'), /Personal instructions/)

})

test('项目侧三种 CLI 共用根 AGENTS.md，只注入所选 Rules', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# Project instructions')
  await syncAll({ ...opts, scope: 'project', selectedPlatforms: [...opts.selectedPlatforms, 'cursor'] })
  const content = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  assert.match(content, /Project instructions/)
  assert.match(content, /# Rule/)
  assert.doesNotMatch(content, /# Baseline/)
  assert.equal(content.split('dwy-rule: sample.md').length - 1, 1)
  for (const relative of ['CLAUDE.md', '.claude/CLAUDE.md', '.claude/AGENTS.md', '.claude/rules/sample.md', '.cursor/rules/00-dwy-global.mdc']) {
    assert.equal(await fs.pathExists(path.join(opts.projectDir, relative)), false)
  }
  assert.match(await fs.readFile(path.join(opts.projectDir, '.cursor/rules/dwy-sample.mdc'), 'utf8'), /# Rule/)
})

test('最后取消不写配置或同步记录', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, scope: 'project', confirmed: false })
  assert.deepEqual(await fs.readdir(opts.projectDir), [])
  assert.equal(await fs.pathExists(opts.homeDir), false)
})

test('Skills 位置选全局时 Cursor Rules 仍只写项目', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['cursor'] })
  assert.match(await fs.readFile(path.join(opts.projectDir, '.cursor/rules/dwy-sample.mdc'), 'utf8'), /# Rule/)
  assert.equal(await fs.pathExists(opts.homeDir), false)
})
