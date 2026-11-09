import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { syncAll, refreshAll } from '../src/sync-all.js'
import { refreshExternalSkills } from '../src/skills-install.js'

for (const { stalled, allFailed } of [{ stalled: false, allFailed: false }, { stalled: true, allFailed: false }, { stalled: false, allFailed: true }]) {
  test(`外部 Skills ${allFailed ? '全部拉取失败时不改版本清单' : `拉取${stalled ? '超时' : '失败'}时保留旧副本并继续刷新其他来源`}`, { timeout: 25000 }, async t => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-network-'))
    t.after(() => fs.remove(root))
    const target = path.join(root, 'skills'), bin = path.join(root, 'bin')
    await fs.outputFile(path.join(target, 'create-prd/SKILL.md'), '# Old PRD')
    await fs.outputFile(path.join(target, 'brainstorming/SKILL.md'), '# Old brainstorming')
    const oldVersion = { repo: 'https://github.com/phuryn/pm-skills.git', tag: 'v1.0.0' }
    await fs.outputJson(path.join(target, 'VERSIONS.json'), { manifest_hash: 'old', versions: { 'create-prd': oldVersion } })
    await fs.outputFile(path.join(bin, 'git'), `#!${process.execPath}
const fs = require('node:fs'), path = require('node:path')
if (${allFailed} || process.argv.includes('https://github.com/phuryn/pm-skills.git')) {
  setTimeout(() => process.exit(1), ${stalled ? 18000 : 0})
} else {
  const dest = process.argv.at(-1)
  fs.mkdirSync(path.join(dest, 'skills/brainstorming'), { recursive: true })
  fs.writeFileSync(path.join(dest, 'skills/brainstorming/SKILL.md'), '# New brainstorming')
  fs.writeFileSync(path.join(dest, 'LICENSE'), 'MIT')
}
`)
    await fs.chmod(path.join(bin, 'git'), 0o755)
    const previousPath = process.env.PATH
    process.env.PATH = `${bin}${path.delimiter}${previousPath}`
    t.after(() => { process.env.PATH = previousPath })
    const messages = []
    t.mock.method(console, 'log', message => messages.push(message))
    const started = Date.now()
    await refreshExternalSkills(target)
    assert.ok(Date.now() - started < 17000, '拉取必须在 15 秒超时后及时结束')
    assert.equal(await fs.readFile(path.join(target, 'create-prd/SKILL.md'), 'utf8'), '# Old PRD')
    assert.equal(await fs.readFile(path.join(target, 'brainstorming/SKILL.md'), 'utf8'), allFailed ? '# Old brainstorming' : '# New brainstorming')
    const versions = await fs.readJson(path.join(target, 'VERSIONS.json'))
    assert.deepEqual(versions.versions['create-prd'], oldVersion)
    assert.equal(versions.manifest_hash, 'old')
    if (allFailed) {
      assert.deepEqual(versions.versions, { 'create-prd': oldVersion })
      assert.ok(!messages.some(message => message.includes('已安装到')))
    }
    assert.ok(messages.some(message => message.includes('pm-skills') && message.includes('跳过')))
    assert.equal(await fs.pathExists(path.join(target, 'market-sizing')), false)
  })
}

test('refresh 更新全局及当前项目已有内容，保留个人内容和未启用项', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  const codexHome = path.join(homeDir, '.codex')
  const options = { sourceDir, projectDir, homeDir, codexHome }
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# Old baseline')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# Old skill')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# Old rule')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '# old hook')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', platforms: ['codex'] }])
  await syncAll({ ...options, scope: 'global', selectedPlatforms: ['codex'], selected: { skills: [{ name: 'sample' }] }, contentTypes: ['skills', 'baseline', 'hooks'] })
  await syncAll({ ...options, selectedPlatforms: ['codex'], selected: { rules: [{ name: 'sample.md' }] }, contentTypes: ['rules'] })
  await fs.appendFile(path.join(projectDir, 'AGENTS.md'), '\nPersonal project instructions\n')
  await fs.appendFile(path.join(codexHome, 'AGENTS.md'), '\nPersonal global instructions\n')
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# New baseline')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# New skill')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/unselected/SKILL.md'), '# Unselected')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# New rule')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '# new hook')
  execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), 'refresh'], {
    cwd: projectDir, encoding: 'utf8',
    env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: codexHome,
      DWY_HOME: path.join(homeDir, '.dwy'), DWY_TEMPLATE_SOURCE_DIR: sourceDir },
  })
  assert.equal(await fs.readFile(path.join(homeDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# New skill')
  assert.match(await fs.readFile(path.join(codexHome, 'AGENTS.md'), 'utf8'), /New baseline[\s\S]*Personal global instructions/)
  assert.match(await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf8'), /New rule[\s\S]*Personal project instructions/)
  assert.equal(await fs.readFile(path.join(codexHome, 'hooks/check.sh'), 'utf8'), '# new hook')
  assert.equal(await fs.pathExists(path.join(projectDir, '.codex/hooks/check.sh')), false)
  assert.equal(await fs.pathExists(path.join(homeDir, '.dwy/skills/unselected')), false)
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude')), false)
})

test('未初始化目录执行 refresh 不创建项目或全局配置；主目录只刷新一次', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-empty-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home')
  await fs.ensureDir(homeDir)
  await fs.ensureDir(sourceDir)
  await refreshAll({ sourceDir, homeDir, projectDir: homeDir, codexHome: path.join(homeDir, '.codex') })
  assert.deepEqual(await fs.readdir(homeDir), [])
})

test('外部 Skills 只刷新已有项；复制失败保留旧内容并报告错误', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-external-'))
  t.after(() => fs.remove(root))
  const repo = path.join(root, 'repo'), target = path.join(root, 'skills')
  await fs.outputFile(path.join(repo, 'skills/brainstorming/SKILL.md'), '# New external')
  await fs.outputFile(path.join(repo, 'LICENSE'), 'MIT')
  const git = args => execFileSync('git', args, { cwd: repo, stdio: 'pipe' })
  git(['init', '-q'])
  git(['add', '.'])
  git(['-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'fixture'])
  git(['tag', 'v6.0.3'])
  const env = { GIT_CONFIG_COUNT: '1', GIT_CONFIG_KEY_0: `url.file://${repo}.insteadOf`, GIT_CONFIG_VALUE_0: 'https://github.com/obra/superpowers.git' }
  const previous = Object.fromEntries(Object.keys(env).map(key => [key, process.env[key]]))
  Object.assign(process.env, env)
  t.after(() => { for (const [key, value] of Object.entries(previous)) { if (value === undefined) delete process.env[key]; else process.env[key] = value } })
  await fs.outputFile(path.join(target, 'brainstorming/SKILL.md'), '# Old external')
  await fs.outputFile(path.join(target, 'personal/SKILL.md'), '# Personal')
  const copy = fs.copy
  const failing = t.mock.method(fs, 'copy', async (from, ...args) => {
    if (from.endsWith('skills/brainstorming')) throw new Error('copy failed')
    return copy(from, ...args)
  })
  await assert.rejects(refreshExternalSkills(target), /copy failed/)
  assert.equal(await fs.readFile(path.join(target, 'brainstorming/SKILL.md'), 'utf8'), '# Old external')
  failing.mock.restore()
  const rename = fs.rename
  const replacing = t.mock.method(fs, 'rename', async (from, to) => {
    if (from.includes('.refresh-') && to === path.join(target, 'brainstorming')) throw new Error('replace failed')
    return rename(from, to)
  })
  await assert.rejects(refreshExternalSkills(target), /replace failed/)
  assert.equal(await fs.readFile(path.join(target, 'brainstorming/SKILL.md'), 'utf8'), '# Old external')
  replacing.mock.restore()
  await refreshExternalSkills(target)
  assert.equal(await fs.readFile(path.join(target, 'brainstorming/SKILL.md'), 'utf8'), '# New external')
  assert.equal(await fs.readFile(path.join(target, 'personal/SKILL.md'), 'utf8'), '# Personal')
  assert.equal(await fs.pathExists(path.join(target, 'writing-plans')), false)
})

test('旧项目 Skill 刷新时先备份，不补装产品流程外部依赖，移除的模板保留', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-legacy-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(homeDir)
  await fs.outputFile(path.join(sourceDir, 'skills/产品0到1/sample/SKILL.md'), '# Latest')
  await fs.outputFile(path.join(projectDir, '.agents/skills/sample/SKILL.md'), '# Old')
  await fs.outputFile(path.join(projectDir, '.agents/skills/removed/SKILL.md'), '# Removed template')
  await fs.outputJson(path.join(projectDir, '.dwy/sync-state.json'), { platforms: { codex: { skills: ['sample', 'removed'] } } })
  await refreshAll({ sourceDir, projectDir, homeDir, codexHome: path.join(homeDir, '.codex') })
  assert.equal(await fs.readFile(path.join(projectDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# Latest')
  const backups = await fs.readdir(path.join(projectDir, '.dwy/skill-backups'))
  assert.equal(backups.length, 1)
  assert.equal(await fs.readFile(path.join(projectDir, '.dwy/skill-backups', backups[0], 'SKILL.md'), 'utf8'), '# Old')
  assert.equal(await fs.readFile(path.join(projectDir, '.agents/skills/removed/SKILL.md'), 'utf8'), '# Removed template')
  assert.equal(await fs.pathExists(path.join(homeDir, '.dwy/skills/brainstorming')), false)
})
