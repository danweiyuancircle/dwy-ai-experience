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
  await fs.outputFile(path.join(sourceDir, 'CLAUDE.md'), '# Baseline')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [
    { name: 'check.sh', event: 'PreToolUse', platforms: ['claude', 'codex'] },
  ])
  return { sourceDir, homeDir, projectDir, selectedPlatforms: ['claude', 'codex', 'opencode'],
    selected: { skills: [{ name: 'sample' }], rules: [{ name: 'sample.md' }], hooks: [{ name: 'check.sh' }] } }
}

test('全局整套同步隔离项目，保留个人规则和设置，Hooks 可从其他目录执行', async t => {
  const opts = await fixture(t)
  for (const relative of ['.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md']) {
    await fs.outputFile(path.join(opts.homeDir, relative), '# Personal instructions')
  }
  await fs.outputJson(path.join(opts.homeDir, '.claude/settings.json'), { model: 'personal' })
  await syncAll({ ...opts, scope: 'global' })
  assert.deepEqual(await fs.readdir(opts.projectDir), [])
  for (const relative of ['.claude/skills', '.agents/skills', '.config/opencode/skills']) {
    assert.equal(await fs.pathExists(path.join(opts.homeDir, relative, 'sample/SKILL.md')), true)
  }
  for (const relative of ['.claude/CLAUDE.md', '.codex/AGENTS.md', '.config/opencode/AGENTS.md']) {
    assert.match(await fs.readFile(path.join(opts.homeDir, relative), 'utf8'), /Personal instructions/)
  }
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
  const repeated = await fs.readJson(path.join(opts.homeDir, '.claude/settings.json'))
  assert.equal(repeated.hooks.PreToolUse[0].hooks.length, 1)
  await fs.remove(path.join(opts.sourceDir, 'skills/通用/sample'))
  await fs.remove(path.join(opts.sourceDir, 'rules/通用/sample.md'))
  await syncAll({ ...opts, scope: 'global', selected: { skills: [], rules: [], hooks: [] } })
  for (const relative of ['.claude/skills', '.agents/skills', '.config/opencode/skills']) {
    assert.equal(await fs.pathExists(path.join(opts.homeDir, relative, 'sample')), false)
  }
  assert.doesNotMatch(await fs.readFile(path.join(opts.homeDir, '.codex/AGENTS.md'), 'utf8'), /# Rule/)
  assert.match(await fs.readFile(path.join(opts.homeDir, '.codex/AGENTS.md'), 'utf8'), /Personal instructions/)

})

test('最后取消不写配置或同步记录', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, scope: 'project', confirmed: false })
  assert.deepEqual(await fs.readdir(opts.projectDir), [])
  assert.equal(await fs.pathExists(opts.homeDir), false)
})

test('全局 Cursor 不支持文件规则时拒绝写入', async t => {
  const opts = await fixture(t)
  await assert.rejects(syncAll({ ...opts, scope: 'global', selectedPlatforms: ['cursor'] }), /不支持/)
  assert.equal(await fs.pathExists(opts.homeDir), false)
})
