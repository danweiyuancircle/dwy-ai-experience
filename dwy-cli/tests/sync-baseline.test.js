import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { buildSelectionDefaultsFromSyncState, syncAll } from '../src/sync-all.js'

const globalFiles = {
  claude: '.claude/CLAUDE.md',
  codex: '.codex/AGENTS.md',
  opencode: '.config/opencode/AGENTS.md',
}

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-baseline-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates')
  const homeDir = path.join(root, 'home')
  const projectDir = path.join(root, 'project')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# Universal baseline\n')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/first.md'), '# First rule\nFirst project only.\n')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/second.md'), '# Second rule\nSecond project only.\n')
  return { sourceDir, homeDir, codexHome: path.join(homeDir, '.codex'), projectDir,
    selected: { skills: [], rules: [{ name: 'first.md' }], hooks: [] } }
}

for (const platform of Object.keys(globalFiles)) {
  test(`${platform} 单独同步也默认更新全局基线，并把 Rules 写入项目根`, async t => {
    const opts = await fixture(t)
    await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# Personal project\n')
    await syncAll({ ...opts, selectedPlatforms: [platform] })
    const global = await fs.readFile(path.join(opts.homeDir, globalFiles[platform]), 'utf8')
    assert.match(global, /Universal baseline/)
    assert.doesNotMatch(global, /First project only/)
    const project = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
    assert.match(project, /Personal project/)
    assert.match(project, /First project only/)
    assert.doesNotMatch(project, /Universal baseline/)
    for (const [other, relative] of Object.entries(globalFiles)) {
      if (other !== platform) assert.equal(await fs.pathExists(path.join(opts.homeDir, relative)), false)
    }
  })
}

test('没有选择 Rules 时只更新全局基线，不创建项目 AGENTS.md', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['claude', 'codex', 'opencode'],
    selected: { skills: [], rules: [], hooks: [] } })
  assert.equal(await fs.pathExists(path.join(opts.projectDir, 'AGENTS.md')), false)
  for (const relative of Object.values(globalFiles)) {
    assert.match(await fs.readFile(path.join(opts.homeDir, relative), 'utf8'), /Universal baseline/)
  }
})

test('不同项目共享全局基线，Rules 及同步记录保持各自独立', async t => {
  const opts = await fixture(t)
  const secondProject = path.join(opts.homeDir, '..', 'second-project')
  await syncAll({ ...opts, selectedPlatforms: ['codex'] })
  await syncAll({ ...opts, projectDir: secondProject, selectedPlatforms: ['codex'],
    selected: { skills: [], rules: [{ name: 'second.md' }], hooks: [] } })
  const first = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  const second = await fs.readFile(path.join(secondProject, 'AGENTS.md'), 'utf8')
  assert.match(first, /First project only/)
  assert.doesNotMatch(first, /Second project only/)
  assert.match(second, /Second project only/)
  assert.doesNotMatch(second, /First project only/)
  const global = await fs.readFile(path.join(opts.codexHome, 'AGENTS.md'), 'utf8')
  assert.equal(global.split('Universal baseline').length - 1, 1)
  assert.doesNotMatch(global, /project only/)
  for (const [projectDir, rule] of [[opts.projectDir, 'first.md'], [secondProject, 'second.md']]) {
    const state = await fs.readJson(path.join(projectDir, '.dwy/sync-state.json'))
    assert.deepEqual(state.platforms.codex.rules, [rule])
  }
})

test('取消勾选只移除项目托管 Rules，保留全局基线及手写内容', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# Personal project\n')
  await syncAll({ ...opts, selectedPlatforms: ['claude'] })
  const globalFile = path.join(opts.homeDir, globalFiles.claude)
  const globalBefore = await fs.readFile(globalFile, 'utf8')
  await syncAll({ ...opts, selectedPlatforms: ['claude'], selected: { skills: [], rules: [], hooks: [] } })
  const project = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  assert.match(project, /Personal project/)
  assert.doesNotMatch(project, /First project only|DWY-RULES/)
  assert.equal(await fs.readFile(globalFile, 'utf8'), globalBefore)
})

test('切换 CLI 后取消共享 Rules，不会被未选平台的旧记录重新勾选', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['claude', 'codex'] })
  const statePath = path.join(opts.projectDir, '.dwy/sync-state.json')
  const previous = await fs.readJson(statePath)
  previous.platforms.codex.skills = ['keep']
  previous.platforms.codex.hooks = ['keep.sh']
  await fs.writeJson(statePath, previous)
  await fs.outputFile(path.join(opts.projectDir, '.agents/skills/keep/SKILL.md'), '# Personal skill')
  await fs.outputFile(path.join(opts.projectDir, '.codex/hooks/keep.sh'), '# Personal hook')
  await syncAll({ ...opts, selectedPlatforms: ['claude'], selected: { skills: [], rules: [], hooks: [] } })
  const state = await fs.readJson(statePath)
  const defaults = buildSelectionDefaultsFromSyncState({ skills: new Set(), rules: new Set(), hooks: new Set() }, state)
  assert.deepEqual([...defaults.rules], [])
  assert.deepEqual(state.platforms.codex.rules, [])
  assert.deepEqual(state.platforms.codex.skills, ['keep'])
  assert.deepEqual(state.platforms.codex.hooks, ['keep.sh'])
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/keep/SKILL.md'), 'utf8'), '# Personal skill')
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.codex/hooks/keep.sh'), 'utf8'), '# Personal hook')
})

test('迁移可识别的旧托管内容，保留全局与项目的个人内容', async t => {
  const opts = await fixture(t)
  const oldBaseline = '<!-- DWY-BASELINE:START -->\nOld baseline\n<!-- DWY-BASELINE:END -->\n'
  const oldRules = '<!-- DWY-RULES:START -->\n<!-- dwy-rule: first.md -->\nOld global rule\n<!-- DWY-RULES:END -->\n'
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# Project personal\n' + oldBaseline)
  await fs.outputFile(path.join(opts.homeDir, '.claude/AGENTS.md'), '# Claude personal\n' + oldBaseline)
  await fs.outputFile(path.join(opts.codexHome, 'AGENTS.md'), '# Codex personal\n' + oldBaseline + oldRules)
  await fs.outputFile(path.join(opts.homeDir, '.config/opencode/AGENTS.md'), '# OpenCode personal\n' + oldBaseline + oldRules)
  await fs.outputFile(path.join(opts.projectDir, '.claude/AGENTS.md'), '# Universal baseline\n')
  await fs.outputFile(path.join(opts.projectDir, '.claude/rules/first.md'), '# Old rule')
  await fs.outputFile(path.join(opts.projectDir, '.claude/rules/personal.md'), '# Keep personal rule')
  await syncAll({ ...opts, selectedPlatforms: ['claude', 'codex', 'opencode'] })
  const project = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  assert.match(project, /Project personal/)
  assert.match(project, /First project only/)
  assert.doesNotMatch(project, /Old baseline|Universal baseline/)
  for (const [platform, relative] of Object.entries(globalFiles)) {
    const content = await fs.readFile(path.join(opts.homeDir, relative), 'utf8')
    assert.match(content, /Universal baseline/)
    assert.doesNotMatch(content, /Old baseline|Old global rule|DWY-RULES/)
    if (platform !== 'claude') assert.match(content, /personal/)
  }
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/AGENTS.md'), 'utf8'), '# Claude personal\n')
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/AGENTS.md')), false)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/rules/first.md')), false)
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.claude/rules/personal.md'), 'utf8'), '# Keep personal rule')
})

test('Codex 基线可写入指定配置目录', async t => {
  const opts = await fixture(t)
  const codexHome = path.join(opts.homeDir, 'custom codex')
  await syncAll({ ...opts, codexHome, selectedPlatforms: ['codex'] })
  assert.match(await fs.readFile(path.join(codexHome, 'AGENTS.md'), 'utf8'), /Universal baseline/)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.codex/AGENTS.md')), false)
})

test('Codex 默认基线位置遵循 CODEX_HOME', async t => {
  const opts = await fixture(t)
  const codexHome = path.join(opts.homeDir, 'profile')
  execFileSync(process.execPath, ['--input-type=module', '-e', `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify({ ...opts, codexHome: undefined, selectedPlatforms: ['codex'] })});
  `], { cwd: new URL('../../', import.meta.url), env: { ...process.env, CODEX_HOME: codexHome }, stdio: 'pipe' })
  assert.match(await fs.readFile(path.join(codexHome, 'AGENTS.md'), 'utf8'), /Universal baseline/)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.codex/AGENTS.md')), false)
})

test('旧全局文件等于基线模板时迁移为单个托管块', async t => {
  const opts = await fixture(t)
  const target = path.join(opts.homeDir, globalFiles.claude)
  await fs.outputFile(target, '# Universal baseline\n')
  await syncAll({ ...opts, selectedPlatforms: ['claude'] })
  const content = await fs.readFile(target, 'utf8')
  assert.equal(content.split('Universal baseline').length - 1, 1)
  assert.match(content, /DWY-BASELINE:START/)
})

test('旧同步记录中的规则名不能越出规则目录删除文件', async t => {
  const opts = await fixture(t)
  const personalFile = path.join(opts.homeDir, 'personal.md')
  await fs.outputFile(personalFile, '# Keep personal')
  await fs.outputJson(path.join(opts.homeDir, '.dwy/sync-state.json'), {
    version: 1, platforms: { claude: { rules: ['../../personal.md'] } },
  })
  await syncAll({ ...opts, selectedPlatforms: ['claude'] })
  assert.equal(await fs.readFile(personalFile, 'utf8'), '# Keep personal')
})
