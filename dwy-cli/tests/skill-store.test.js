import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { prepareSharedSkills, linkSkill, removeSkillEntry, refreshSharedSkills } from '../src/skill-store.js'

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-skill-store-'))
  t.after(() => fs.remove(root))
  const homeDir = path.join(root, 'user home')
  const sourceDir = path.join(root, 'templates')
  const sourcePath = path.join(sourceDir, 'skills', '通用', 'sample')
  await fs.outputFile(path.join(sourcePath, 'SKILL.md'), '# v1')
  await fs.outputFile(path.join(sourcePath, 'references', 'guide.md'), 'guide v1')
  return { root, homeDir, sourceDir, skill: { name: 'sample', sourcePath } }
}

test('两个项目链接到稳定共享目录，刷新后正文、引用和删除文件同时生效', async t => {
  const { root, homeDir, sourceDir, skill } = await fixture(t)
  await fs.outputFile(path.join(skill.sourcePath, 'old.md'), 'remove me')
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  assert.equal(shared.sourcePath, path.join(homeDir, '.dwy', 'skills', 'sample'))
  const entries = ['one', 'two'].map(name => path.join(root, name, '.agents', 'skills', skill.name))
  for (const dest of entries) {
    await linkSkill({ skill: shared, dest, backupRoot: path.join(root, 'backups') })
    assert.equal((await fs.lstat(dest)).isSymbolicLink(), true)
    assert.equal(await fs.realpath(dest), await fs.realpath(shared.sourcePath))
  }
  await fs.outputFile(path.join(skill.sourcePath, 'SKILL.md'), '# v2')
  await fs.outputFile(path.join(skill.sourcePath, 'references', 'guide.md'), 'guide v2')
  await fs.remove(path.join(skill.sourcePath, 'old.md'))
  const result = await refreshSharedSkills({ sourceDir, homeDir })
  assert.deepEqual(result.updated, ['sample'])
  for (const dest of entries) {
    assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), '# v2')
    assert.equal(await fs.readFile(path.join(dest, 'references', 'guide.md'), 'utf8'), 'guide v2')
    assert.equal(await fs.pathExists(path.join(dest, 'old.md')), false)
  }
})

test('旧真实目录完整备份，重复链接不重复备份，删除入口不删除共享内容', async t => {
  const { root, homeDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  const dest = path.join(root, 'project', '.claude', 'skills', 'sample')
  const backupRoot = path.join(root, 'project', '.dwy', 'skill-backups')
  await fs.outputFile(path.join(dest, 'SKILL.md'), '# edited')
  await fs.outputFile(path.join(dest, 'personal.txt'), 'keep')
  const backup = await linkSkill({ skill: shared, dest, backupRoot })
  assert.equal(await fs.readFile(path.join(backup, 'personal.txt'), 'utf8'), 'keep')
  assert.equal(await fs.readFile(path.join(backup, 'SKILL.md'), 'utf8'), '# edited')
  assert.equal(await linkSkill({ skill: shared, dest, backupRoot }), null)
  assert.equal((await fs.readdir(backupRoot)).length, 1)
  await removeSkillEntry({ dest, backupRoot })
  assert.equal(await fs.pathExists(dest), false)
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v1')
})

test('坏链接可以修复，项目去重时真实目录先备份', async t => {
  const { root, homeDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  const dest = path.join(root, 'sample')
  const backupRoot = path.join(root, 'backup')
  await fs.symlink(path.join(root, 'missing'), dest, process.platform === 'win32' ? 'junction' : 'dir')
  await linkSkill({ skill: shared, dest, backupRoot })
  assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), '# v1')
  await fs.remove(dest)
  await fs.outputFile(path.join(dest, 'custom.md'), 'keep on dedup')
  const backup = await removeSkillEntry({ dest, backupRoot })
  assert.equal(await fs.readFile(path.join(backup, 'custom.md'), 'utf8'), 'keep on dedup')
})

test('新包移除的共享 Skill 保留，外部缓存不纳入刷新', async t => {
  const { homeDir, sourceDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  await fs.outputFile(path.join(homeDir, '.dwy', 'skills', 'external', 'SKILL.md'), '# external')
  await fs.remove(skill.sourcePath)
  const result = await refreshSharedSkills({ sourceDir, homeDir })
  assert.deepEqual(result.retained, ['sample'])
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v1')
  assert.equal(await fs.readFile(path.join(homeDir, '.dwy', 'skills', 'external', 'SKILL.md'), 'utf8'), '# external')
})

test('无效来源不能覆盖已安装共享副本', async t => {
  const { homeDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  await fs.remove(path.join(skill.sourcePath, 'SKILL.md'))
  await assert.rejects(prepareSharedSkills({ skills: [skill], homeDir }), /SKILL.md/)
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v1')
})

test('链接创建失败保留原目录，拒绝通过不安全名称写出共享目录', async t => {
  const { root, homeDir, skill } = await fixture(t)
  const dest = path.join(root, 'original')
  await fs.outputFile(path.join(dest, 'SKILL.md'), '# original')
  await assert.rejects(linkSkill({
    skill: { ...skill, sourcePath: path.join(root, 'missing') },
    dest,
    backupRoot: path.join(root, 'backup'),
  }))
  assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), '# original')
  await assert.rejects(prepareSharedSkills({ skills: [{ ...skill, name: '../outside' }], homeDir }), /名称/)
})

test('复制或替换失败保留旧副本，释放刷新锁后可重试', async t => {
  const { homeDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  await fs.outputFile(path.join(skill.sourcePath, 'SKILL.md'), '# v2')
  const copy = t.mock.method(fs, 'copy', async () => { throw new Error('copy failed') })
  await assert.rejects(prepareSharedSkills({ skills: [skill], homeDir }), /copy failed/)
  copy.mock.restore()
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v1')
  const originalRename = fs.rename
  const rename = t.mock.method(fs, 'rename', async (from, to) => {
    if (to === shared.sourcePath && !from.endsWith('.old')) throw new Error('replace failed')
    return originalRename(from, to)
  })
  await assert.rejects(prepareSharedSkills({ skills: [skill], homeDir }), /replace failed/)
  rename.mock.restore()
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v1')
  await prepareSharedSkills({ skills: [skill], homeDir })
  assert.equal(await fs.readFile(path.join(shared.sourcePath, 'SKILL.md'), 'utf8'), '# v2')
})

test('链接切换失败恢复原目录，临时目录创建失败也会释放刷新锁', async t => {
  const { root, homeDir, skill } = await fixture(t)
  const [shared] = await prepareSharedSkills({ skills: [skill], homeDir })
  const dest = path.join(root, 'project', 'sample')
  await fs.outputFile(path.join(dest, 'SKILL.md'), '# original')
  const originalRename = fs.rename
  const rename = t.mock.method(fs, 'rename', async (from, to) => {
    if (from.includes('.link-') && to === dest) throw new Error('link switch failed')
    return originalRename(from, to)
  })
  await assert.rejects(linkSkill({ skill: shared, dest, backupRoot: path.join(root, 'backup') }), /link switch failed/)
  rename.mock.restore()
  assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), '# original')
  const mkdtemp = t.mock.method(fs, 'mkdtemp', async () => { throw new Error('staging failed') })
  await assert.rejects(prepareSharedSkills({ skills: [skill], homeDir }), /staging failed/)
  mkdtemp.mock.restore()
  assert.equal(await fs.pathExists(path.join(homeDir, '.dwy/skill-store.lock')), false)
})

test('并发刷新互斥，第二个进程不能覆盖正在准备的副本', async t => {
  const { homeDir, skill } = await fixture(t)
  const originalCopy = fs.copy
  let entered
  const copying = new Promise(resolve => { entered = resolve })
  let release
  const blocked = new Promise(resolve => { release = resolve })
  const copy = t.mock.method(fs, 'copy', async (...args) => { entered(); await blocked; return originalCopy(...args) })
  const first = prepareSharedSkills({ skills: [skill], homeDir })
  await copying
  try {
    await assert.rejects(prepareSharedSkills({ skills: [skill], homeDir }), /另一个进程/)
  } finally {
    release()
    await first
    copy.mock.restore()
  }
})

test('批量复制、替换或清单提交失败时，所有共享副本恢复为旧内容', async t => {
  const { root, homeDir, skill } = await fixture(t)
  const other = { name: 'other', sourcePath: path.join(root, 'other') }
  await fs.outputFile(path.join(other.sourcePath, 'SKILL.md'), '# v1')
  await prepareSharedSkills({ skills: [skill, other], homeDir })
  for (const entry of [skill, other]) await fs.outputFile(path.join(entry.sourcePath, 'SKILL.md'), '# v2')
  const originalCopy = fs.copy
  const copy = t.mock.method(fs, 'copy', async (from, ...args) => {
    if (from === other.sourcePath) throw new Error('second copy failed')
    return originalCopy(from, ...args)
  })
  await assert.rejects(prepareSharedSkills({ skills: [skill, other], homeDir }), /second copy failed/)
  copy.mock.restore()
  for (const entry of [skill, other]) {
    assert.equal(await fs.readFile(path.join(homeDir, '.dwy/skills', entry.name, 'SKILL.md'), 'utf8'), '# v1')
  }
  const originalRename = fs.rename
  for (const failedTarget of [path.join(homeDir, '.dwy/skills/other'), path.join(homeDir, '.dwy/skill-store.json')]) {
    const rename = t.mock.method(fs, 'rename', async (from, to) => {
      if (to === failedTarget && !from.endsWith('.old')) throw new Error('commit failed')
      return originalRename(from, to)
    })
    await assert.rejects(prepareSharedSkills({ skills: [skill, other], homeDir }), /commit failed/)
    rename.mock.restore()
    for (const entry of [skill, other]) {
      assert.equal(await fs.readFile(path.join(homeDir, '.dwy/skills', entry.name, 'SKILL.md'), 'utf8'), '# v1')
    }
  }
})
