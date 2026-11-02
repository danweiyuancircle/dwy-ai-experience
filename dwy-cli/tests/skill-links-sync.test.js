import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { syncAll } from '../src/sync-all.js'
import { scanExistingCodexSkills } from '../src/sync-codex.js'
import * as globalSkillTools from '../src/sync-global-skills.js'

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-link-sync-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'source')
  const homeDir = path.join(root, 'home')
  const projectDir = path.join(root, 'project')
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'sample', 'SKILL.md'), '# new')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [])
  return { sourceDir, homeDir, projectDir, codexHome: path.join(homeDir, '.codex'),
    selectedPlatforms: ['claude', 'codex', 'opencode'],
    selected: { skills: [{ name: 'sample' }], rules: [], hooks: [] } }
}

for (const syncMode of ['all', 'skills']) {
  test(`${syncMode}：项目入口使用共享链接，Codex 扫描不漏掉链接或坏链`, async t => {
    const opts = await fixture(t)
    await syncAll({ ...opts, syncMode })
    for (const dir of ['.claude/skills', '.agents/skills', '.opencode/skills']) {
      const entry = path.join(opts.projectDir, dir, 'sample')
      assert.equal((await fs.lstat(entry)).isSymbolicLink(), true)
      assert.equal(await fs.realpath(entry), await fs.realpath(path.join(opts.homeDir, '.dwy/skills/sample')))
    }
    const broken = path.join(opts.projectDir, '.agents/skills/broken')
    await fs.symlink(path.join(opts.projectDir, 'missing'), broken, process.platform === 'win32' ? 'junction' : 'dir')
    assert.deepEqual(await scanExistingCodexSkills(opts.projectDir), new Set(['sample', 'broken']))
  })

  test(`${syncMode}：全局有效入口优先，项目旧目录备份，状态按实际入口记录`, async t => {
    const opts = await fixture(t)
    await fs.outputFile(path.join(opts.homeDir, '.claude/skills/sample/SKILL.md'), '# global old')
    await fs.outputFile(path.join(opts.projectDir, '.claude/skills/sample/private.txt'), 'keep')
    await fs.outputFile(path.join(opts.projectDir, '.agents/skills/personal/SKILL.md'), '# personal')
    await syncAll({ ...opts, syncMode })
    assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/skills/sample')), false)
    assert.equal(await fs.pathExists(path.join(opts.projectDir, '.opencode/skills/sample')), false)
    assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# new')
    assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/personal/SKILL.md'), 'utf8'), '# personal')
    const backups = await fs.readdir(path.join(opts.projectDir, '.dwy/skill-backups'))
    assert.equal(backups.length, 1)
    assert.equal(await fs.readFile(path.join(opts.projectDir, '.dwy/skill-backups', backups[0], 'private.txt'), 'utf8'), 'keep')
    const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
    assert.deepEqual(state.platforms.claude.skills, [])
    assert.deepEqual(state.platforms.codex.skills, ['sample'])
    assert.deepEqual(state.platforms.opencode.skills, [])
    assert.equal((await fs.lstat(path.join(opts.homeDir, '.claude/skills/sample'))).isDirectory(), true)
    assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/skills/sample/SKILL.md'), 'utf8'), '# global old')
  })

  test(`${syncMode}：切换为全局同步后清理项目重复入口，仍保留共享内容`, async t => {
    const opts = await fixture(t)
    await syncAll({ ...opts, syncMode })
    await syncAll({ ...opts, syncMode, scope: 'global' })
    for (const dir of ['.claude/skills', '.agents/skills', '.opencode/skills']) {
      assert.equal(await fs.pathExists(path.join(opts.projectDir, dir, 'sample')), false)
    }
    for (const dir of ['.claude/skills', '.agents/skills', '.config/opencode/skills']) {
      assert.equal((await fs.lstat(path.join(opts.homeDir, dir, 'sample'))).isSymbolicLink(), true)
    }
    const projectState = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
    const globalState = await fs.readJson(path.join(opts.homeDir, '.dwy/sync-state.json'))
    for (const platform of opts.selectedPlatforms) {
      assert.deepEqual(projectState.platforms[platform].skills, [])
      assert.deepEqual(globalState.platforms[platform].skills, ['sample'])
    }
    assert.equal(await fs.readFile(path.join(opts.homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# new')
  })
}

test('同轮项目+额外全局先写全局，再清理项目重复入口；取消不准备共享目录', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, confirmed: false })
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy')), false)
  await fs.outputFile(path.join(opts.projectDir, '.claude/skills/sample/custom.md'), 'keep')
  await syncAll({ ...opts, selectedPlatforms: ['claude'], skillScope: {
    destinations: ['project', 'claude'], globalSkills: ['sample'],
  } })
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/skills/sample')), false)
  assert.equal((await fs.lstat(path.join(opts.homeDir, '.claude/skills/sample'))).isSymbolicLink(), true)
})

test('全局坏链不触发项目删除，未选择的托管重复目录也先备份再清理', async t => {
  const opts = await fixture(t)
  const globalEntry = path.join(opts.homeDir, '.claude/skills/sample')
  await fs.ensureDir(path.dirname(globalEntry))
  await fs.symlink(path.join(opts.homeDir, 'missing'), globalEntry, process.platform === 'win32' ? 'junction' : 'dir')
  await syncAll({ ...opts, selectedPlatforms: ['claude'] })
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.claude/skills/sample/SKILL.md'), 'utf8'), '# new')
  await fs.remove(globalEntry)
  await fs.outputFile(path.join(globalEntry, 'SKILL.md'), '# global')
  await fs.remove(path.join(opts.projectDir, '.claude/skills/sample'))
  await fs.outputFile(path.join(opts.projectDir, '.claude/skills/sample/custom.md'), 'keep')
  await syncAll({ ...opts, selectedPlatforms: ['claude'], selected: { skills: [], rules: [], hooks: [] } })
  const backups = await fs.readdir(path.join(opts.projectDir, '.dwy/skill-backups'))
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.dwy/skill-backups', backups[0], 'custom.md'), 'utf8'), 'keep')
})

test('全局 skills 根目录链接到共享目录时，不创建自链或移动源目录', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['codex'] })
  const root = path.join(opts.homeDir, '.agents/skills')
  await fs.ensureDir(path.dirname(root))
  await fs.symlink(path.join(opts.homeDir, '.dwy/skills'), root, process.platform === 'win32' ? 'junction' : 'dir')
  await syncAll({ ...opts, selectedPlatforms: ['codex'] })
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# new')
  assert.equal((await fs.lstat(path.join(opts.homeDir, '.dwy/skills/sample'))).isDirectory(), true)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.agents/skills/sample')), false)
})

test('常规同步拒绝穿透项目 skills 根链接改写外部目录', async t => {
  const opts = await fixture(t)
  const external = path.join(opts.homeDir, 'external')
  await fs.outputFile(path.join(external, 'sample/SKILL.md'), '# keep')
  await fs.ensureDir(path.join(opts.projectDir, '.agents'))
  await fs.symlink(external, path.join(opts.projectDir, '.agents/skills'), process.platform === 'win32' ? 'junction' : 'dir')
  await assert.rejects(syncAll({ ...opts, selectedPlatforms: ['codex'] }), /根目录链接/)
  assert.equal(await fs.readFile(path.join(external, 'sample/SKILL.md'), 'utf8'), '# keep')
})

test('全局默认勾选覆盖 CODEX_HOME/skills，并排除坏链和无效 Skill', async t => {
  const opts = await fixture(t)
  opts.codexHome = path.join(opts.homeDir, 'custom codex')
  await fs.outputFile(path.join(opts.codexHome, 'skills/sample/SKILL.md'), '# native')
  await fs.outputFile(path.join(opts.codexHome, 'skills/invalid/no-skill.md'), '# invalid')
  await fs.symlink(path.join(opts.homeDir, 'missing'), path.join(opts.codexHome, 'skills/broken'), process.platform === 'win32' ? 'junction' : 'dir')
  assert.deepEqual(await globalSkillTools.scanGlobalSkills(opts), new Set(['sample']))
})

for (const syncMode of ['all', 'skills']) {
  for (const [platform, directory] of [['claude', '.claude'], ['codex', '.agents'], ['opencode', '.opencode']]) {
    test(`${syncMode}/${platform}：取消选择不能穿透根链接删除外部 Skill`, async t => {
      const opts = await fixture(t)
      const external = path.join(opts.homeDir, 'external')
      await fs.outputFile(path.join(external, 'sample/SKILL.md'), '# original')
      await fs.ensureDir(path.join(opts.projectDir, directory))
      await fs.symlink(external, path.join(opts.projectDir, directory, 'skills'), process.platform === 'win32' ? 'junction' : 'dir')
      await assert.rejects(syncAll({ ...opts, syncMode, selectedPlatforms: [platform], selected: { skills: [], rules: [], hooks: [] } }), /根目录链接/)
      assert.equal(await fs.readFile(path.join(external, 'sample/SKILL.md'), 'utf8'), '# original')
    })
  }
}
