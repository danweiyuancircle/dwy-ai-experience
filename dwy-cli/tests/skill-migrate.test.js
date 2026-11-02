import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { migrateSkills } from '../src/sync-all.js'

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-migrate-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates')
  const homeDir = path.join(root, 'home')
  const projectDir = path.join(root, 'project')
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'sample', 'SKILL.md'), '# current')
  await fs.ensureDir(projectDir)
  return { root, sourceDir, homeDir, projectDir, codexHome: path.join(homeDir, '.codex') }
}

test('老项目一键迁移已有入口，保留个人内容和其他配置，重复执行不增加备份', async t => {
  const opts = await fixture(t)
  for (const dir of ['.claude/skills', '.agents/skills', '.opencode/skills']) {
    await fs.outputFile(path.join(opts.projectDir, dir, 'sample/SKILL.md'), '# edited old')
    await fs.outputFile(path.join(opts.projectDir, dir, 'sample/custom.txt'), 'local')
    await fs.outputFile(path.join(opts.projectDir, dir, 'personal/SKILL.md'), '# personal')
  }
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# keep instructions')
  await fs.outputFile(path.join(opts.projectDir, '.claude/hooks/check.sh'), 'keep hook')
  await fs.outputJson(path.join(opts.projectDir, '.dwy/sync-state.json'), {
    version: 1, platforms: { claude: { skills: ['sample'], rules: ['keep.md'], hooks: ['check.sh'], commands: [] } },
  })
  await migrateSkills(opts)
  for (const dir of ['.claude/skills', '.agents/skills', '.opencode/skills']) {
    assert.equal((await fs.lstat(path.join(opts.projectDir, dir, 'sample'))).isSymbolicLink(), true)
    assert.equal(await fs.readFile(path.join(opts.projectDir, dir, 'sample/SKILL.md'), 'utf8'), '# current')
    assert.equal(await fs.readFile(path.join(opts.projectDir, dir, 'personal/SKILL.md'), 'utf8'), '# personal')
  }
  const backupRoot = path.join(opts.projectDir, '.dwy/skill-backups')
  const backups = await fs.readdir(backupRoot)
  assert.equal(backups.length, 3)
  for (const backup of backups) assert.equal(await fs.readFile(path.join(backupRoot, backup, 'custom.txt'), 'utf8'), 'local')
  await migrateSkills(opts)
  assert.deepEqual(await fs.readdir(backupRoot), backups)
  assert.equal(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), '# keep instructions')
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.claude/hooks/check.sh'), 'utf8'), 'keep hook')
  const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
  assert.deepEqual(state.platforms.claude.rules, ['keep.md'])
  assert.deepEqual(state.platforms.claude.hooks, ['check.sh'])
})

test('迁移遵循全局优先，旧包已移除的条目保留并报告，不给其他平台补装', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.homeDir, '.agents/skills/sample/SKILL.md'), '# global')
  await fs.outputFile(path.join(opts.projectDir, '.agents/skills/sample/local.txt'), 'keep')
  await fs.outputFile(path.join(opts.projectDir, '.agents/skills/removed/SKILL.md'), '# historical')
  await fs.outputJson(path.join(opts.projectDir, '.dwy/sync-state.json'), {
    version: 1, platforms: { codex: { skills: ['sample', 'removed'], rules: [], hooks: [], commands: [] } },
  })
  const result = await migrateSkills(opts)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.agents/skills/sample')), false)
  assert.equal((await fs.lstat(path.join(opts.homeDir, '.agents/skills/sample'))).isDirectory(), true)
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# global')
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/removed/SKILL.md'), 'utf8'), '# historical')
  assert.deepEqual(result.retained, [{ platform: 'codex', name: 'removed' }])
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude')), false)
  const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
  assert.deepEqual(state.platforms.codex.skills, ['removed'])
})

test('迁移保留已有的整个 skills 根链接，不通过链接改写外部目录', async t => {
  const opts = await fixture(t)
  const external = path.join(opts.root, 'external')
  await fs.outputFile(path.join(external, 'sample/SKILL.md'), '# external original')
  await fs.ensureDir(path.join(opts.projectDir, '.agents'))
  await fs.symlink(external, path.join(opts.projectDir, '.agents/skills'), process.platform === 'win32' ? 'junction' : 'dir')
  await migrateSkills(opts)
  assert.equal(await fs.readFile(path.join(external, 'sample/SKILL.md'), 'utf8'), '# external original')
})

test('公开 migrate / refresh 命令在无交互下完成；未知参数退出且不写共享副本', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, '.agents/skills/sample/SKILL.md'), '# old')
  const bin = fileURLToPath(new URL('../bin/index.js', import.meta.url))
  const env = { ...process.env, HOME: opts.homeDir, USERPROFILE: opts.homeDir, CODEX_HOME: opts.codexHome,
    DWY_TEMPLATE_SOURCE_DIR: opts.sourceDir, FORCE_COLOR: '0' }
  const run = args => spawnSync(process.execPath, [bin, ...args], { cwd: opts.projectDir, env, encoding: 'utf8', timeout: 5000 })
  const invalid = run(['migrate', 'extra'])
  assert.equal(invalid.status, 1)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy')), false)
  const migrated = run(['migrate'])
  assert.equal(migrated.status, 0, migrated.stderr)
  assert.equal((await fs.lstat(path.join(opts.projectDir, '.agents/skills/sample'))).isSymbolicLink(), true)
  await fs.outputFile(path.join(opts.sourceDir, 'skills/通用/sample/SKILL.md'), '# refreshed')
  const refreshed = run(['refresh'])
  assert.equal(refreshed.status, 0, refreshed.stderr)
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# refreshed')
})
