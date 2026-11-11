import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { syncAll, migrateSkills } from '../src/sync-all.js'
import { refreshSharedSkills } from '../src/skill-store.js'
import { buildSyncPlan, contentOptions, projectSkillChoices } from '../src/sync-plan.js'
import { buildCodexHooksJson } from '../src/sync-codex.js'

for (const scope of ['project', 'global']) {
  test(`${scope} 产品0到1 Skills 计划不包含外部安装，执行不调用 Git 或补装依赖`, async t => {
    const opts = await fixture(t)
    const dwyHome = path.join(opts.homeDir, '.dwy'), targetDir = path.join(dwyHome, 'skills')
    const binDir = path.join(opts.homeDir, 'bin'), calls = path.join(opts.homeDir, 'git-calls')
    await fs.move(path.join(opts.sourceDir, 'skills/通用/sample'), path.join(opts.sourceDir, 'skills/产品0到1/sample'))
    await fs.outputFile(path.join(binDir, 'git'), `#!${process.execPath}\nrequire('node:fs').appendFileSync(${JSON.stringify(calls)}, 'git called\\n'); process.exit(1)\n`, { mode: 0o755 })
    const previous = { PATH: process.env.PATH, DWY_HOME: process.env.DWY_HOME }
    process.env.PATH = `${binDir}${path.delimiter}${previous.PATH}`
    process.env.DWY_HOME = dwyHome
    t.after(() => {
      for (const [key, value] of Object.entries(previous)) {
        if (value === undefined) delete process.env[key]
        else process.env[key] = value
      }
    })
    const skill = { name: 'sample', category: '产品0到1', sourcePath: path.join(opts.sourceDir, 'skills/产品0到1/sample') }
    const plan = await buildSyncPlan({ ...opts, scope, platforms: ['codex'], contentTypes: ['skills'],
      selected: { skills: [skill], rules: [] }, scans: { skills: [skill], rules: [], hooks: [] },
      projectState: { platforms: {} }, globalState: { platforms: {} } })
    await t.test('只读计划没有外部安装操作', () => {
      assert.equal(plan.operations.some(operation => operation.kind === 'external-skills'), false)
    })
    await t.test('实际同步只安装所选共享 Skill', async () => {
      const operations = await syncAll({ ...opts, scope, selectedPlatforms: ['codex'], contentTypes: ['skills'] })
      assert.equal(await fs.pathExists(calls), false, '同步不得调用 Git 或下载外部依赖')
      assert.equal(operations.some(operation => operation.kind === 'external-skills'), false)
      assert.deepEqual(await fs.readdir(targetDir), ['sample'])
      const entry = path.join(scope === 'global' ? opts.homeDir : opts.projectDir, '.agents/skills/sample/SKILL.md')
      assert.equal(await fs.readFile(entry, 'utf8'), '# v1')
    })
  })
}

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-explicit-sync-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# global baseline')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# v1')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# project rule')
  await fs.outputFile(path.join(sourceDir, 'hooks/通用/check.sh'), '#!/bin/sh\necho hook')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', event: 'PreToolUse', platforms: ['claude', 'codex'] }])
  return { sourceDir, projectDir, homeDir, codexHome: path.join(homeDir, '.codex'), selectedPlatforms: ['claude', 'codex'],
    selected: { skills: [{ name: 'sample' }], rules: [{ name: 'sample.md' }], hooks: [] } }
}

test('项目仅选 Skills：全局规范、项目 Rules、Hooks 及其状态全部保留', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# keep project')
  await fs.outputFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), '# keep global')
  await fs.outputFile(path.join(opts.projectDir, '.claude/hooks/local.sh'), '# keep hook')
  await fs.outputJson(path.join(opts.projectDir, '.dwy/sync-state.json'), { version: 1, platforms: {
    claude: { skills: [], rules: ['old.md'], hooks: ['local.sh'], commands: [] },
  } })
  await syncAll({ ...opts, contentTypes: ['skills'] })
  assert.equal(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), '# keep project')
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), 'utf8'), '# keep global')
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.claude/hooks/local.sh'), 'utf8'), '# keep hook')
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/settings.json')), false)
  const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
  assert.deepEqual(state.platforms.claude.rules, ['old.md'])
  assert.deepEqual(state.platforms.claude.hooks, ['local.sh'])
})

test('全局仅选 Skills：不创建或修改项目 Rules 和全局规范', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# project unchanged')
  await fs.outputFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), '# global unchanged')
  await syncAll({ ...opts, scope: 'global', contentTypes: ['skills'] })
  assert.equal(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), '# project unchanged')
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), 'utf8'), '# global unchanged')
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/settings.json')), false)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.dwy/sync-state.json')), false)
})

test('项目同步按平台跳过全局入口，不改写全局原副本，只清理本地重复入口', async t => {
  const opts = await fixture(t)
  const global = path.join(opts.homeDir, '.claude/skills/sample')
  await fs.outputFile(path.join(global, 'SKILL.md'), '# keep global original')
  await fs.outputFile(path.join(opts.projectDir, '.claude/skills/sample/local.txt'), 'keep local')
  await syncAll({ ...opts, contentTypes: ['skills'] })
  assert.equal(await fs.readFile(path.join(global, 'SKILL.md'), 'utf8'), '# keep global original')
  assert.equal((await fs.lstat(global)).isDirectory(), true)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/skills/sample')), false)
  assert.equal((await fs.lstat(path.join(opts.projectDir, '.agents/skills/sample'))).isSymbolicLink(), true)
  const backupRoot = path.join(opts.projectDir, '.dwy/skill-backups')
  const backups = await fs.readdir(backupRoot)
  assert.equal(await fs.readFile(path.join(backupRoot, backups[0], 'local.txt'), 'utf8'), 'keep local')
})

test('sync 和 migrate 不刷新已有共享内容，refresh 才更新', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, contentTypes: ['skills'] })
  await fs.outputFile(path.join(opts.sourceDir, 'skills/通用/sample/SKILL.md'), '# v2')
  await syncAll({ ...opts, contentTypes: ['skills'] })
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# v1')
  await migrateSkills(opts)
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# v1')
  await refreshSharedSkills(opts)
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# v2')
})

test('只有显式选择全局规范才更新用户入口，不能借全局流程写项目 Rules', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, 'AGENTS.md'), '# keep project')
  await syncAll({ ...opts, scope: 'global', contentTypes: ['baseline'] })
  assert.match(await fs.readFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), 'utf8'), /global baseline/)
  assert.match(await fs.readFile(path.join(opts.codexHome, 'AGENTS.md'), 'utf8'), /global baseline/)
  assert.equal(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), '# keep project')
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy/skills')), false)
  await assert.rejects(syncAll({ ...opts, scope: 'global', contentTypes: ['rules'] }), /不支持/)
  await syncAll({ ...opts, scope: 'project', contentTypes: ['baseline'] })
  assert.equal(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), '# keep project')
})

test('不支持的全局平台在确认前拒绝，取消不写任何文件', async t => {
  const opts = await fixture(t)
  await assert.rejects(syncAll({ ...opts, scope: 'global', selectedPlatforms: ['cursor'], contentTypes: ['rules'] }), /不支持/)
  await syncAll({ ...opts, contentTypes: ['skills'], confirmed: false })
  assert.deepEqual(await fs.readdir(opts.projectDir), [])
  assert.equal(await fs.pathExists(opts.homeDir), false)
})

test('内容选项按范围和平台过滤，项目 Skills 覆盖状态由真实全局入口决定', async t => {
  const opts = await fixture(t)
  assert.deepEqual(contentOptions('project', ['cursor']).map(item => item.value), ['rules'])
  assert.deepEqual(contentOptions('global', ['opencode']).map(item => item.value), ['skills', 'baseline'])
  const skills = [{ name: 'sample', category: '通用' }]
  await fs.outputFile(path.join(opts.homeDir, '.claude/skills/sample/SKILL.md'), '# global')
  const [partial] = await projectSkillChoices(skills, opts.selectedPlatforms, opts)
  assert.equal(partial.disabled, false)
  assert.equal(partial.inherited, true)
  assert.match(partial.label, /Codex 可安装到项目/)
  await fs.outputFile(path.join(opts.homeDir, '.agents/skills/sample/SKILL.md'), '# global')
  const [covered] = await projectSkillChoices(skills, opts.selectedPlatforms, opts)
  assert.equal(covered.disabled, true)
  assert.equal(covered.inherited, true)
  assert.match(covered.label, /全局已启用/)
})

test('只选择项目 Rules 不清空 Skills 或 Hooks，返回清单不包含未选择类型', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.projectDir, '.agents/skills/sample/SKILL.md'), '# keep old')
  await fs.outputJson(path.join(opts.projectDir, '.dwy/sync-state.json'), { version: 1, platforms: {
    codex: { skills: ['sample'], hooks: ['old.sh'], rules: [], commands: [] },
  } })
  const operations = await syncAll({ ...opts, contentTypes: ['rules'] })
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# keep old')
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy/skills')), false)
  assert.deepEqual(operations.map(item => item.kind), ['rules', 'state'])
  const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
  assert.deepEqual(state.platforms.codex.skills, ['sample'])
  assert.deepEqual(state.platforms.codex.hooks, ['old.sh'])
})

test('只选择 Hooks 按支持平台自动同步，预览路径与实际脚本和配置对应', async t => {
  const opts = await fixture(t)
  const operations = await syncAll({ ...opts, selectedPlatforms: ['claude', 'codex', 'opencode'], contentTypes: ['hooks'] })
  assert.deepEqual(operations.map(item => item.kind), ['hooks', 'hooks', 'state'])
  for (const operation of operations) for (const dest of operation.paths) assert.equal(await fs.pathExists(dest), true, dest)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, 'AGENTS.md')), false)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.dwy/skills')), false)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.opencode/hooks')), false)
})

test('全局 Codex Hooks 遵循配置目录，命令可执行且重复同步保留个人项', async t => {
  const opts = await fixture(t)
  await fs.outputJson(path.join(opts.sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', event: 'PreToolUse', platforms: ['codex'], statusMessage: 'dwy：检查提交' }])
  const codexHome = path.join(opts.homeDir, "custom profile's codex")
  const personalCommand = "bash '/somewhere/hooks/check.sh'"
  await fs.outputJson(path.join(codexHome, 'hooks.json'), { hooks: { PreToolUse: [
    { matcher: 'Bash', hooks: [{ type: 'command', command: personalCommand }] },
  ] } })
  const options = { ...opts, scope: 'global', codexHome, selectedPlatforms: ['codex'], contentTypes: ['hooks'] }
  const operations = await syncAll(options)
  await syncAll(options)
  const config = await fs.readJson(path.join(codexHome, 'hooks.json'))
  const commands = config.hooks.PreToolUse.flatMap(item => item.hooks.map(hook => hook.command))
  assert.equal(commands.length, 2)
  assert.ok(commands.includes(personalCommand))
  const generated = commands.find(command => command !== personalCommand)
  assert.equal(config.hooks.PreToolUse.flatMap(item => item.hooks).find(hook => hook.command === generated).statusMessage, 'dwy：检查提交')
  assert.equal(execFileSync('bash', ['-c', generated], { encoding: 'utf8' }).trim(), 'hook')
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.codex')), false)
  assert.ok(operations.some(operation => operation.paths.includes(path.join(codexHome, 'hooks.json'))))
})

test('内置 Codex Hooks 在全局和项目注册中显示 dwy 功能描述', async () => {
  const manifests = await fs.readJson(new URL('../templates/ai-tools/hook-manifests/hooks.json', import.meta.url))
  const names = new Set(manifests.map(item => item.name))
  for (const global of [true, false]) {
    const config = buildCodexHooksJson(manifests, names, global, '/test/.codex')
    assert.deepEqual(config.hooks.PreToolUse.flatMap(group => group.hooks.map(hook => hook.statusMessage)), [
      'dwy：检查提交中的敏感信息',
      'dwy：检查提交命令中的反引号',
      'dwy：检查提交信息中的 AI 签名',
    ])
  }
})

test('Hooks 清单包含平台不再支持的旧脚本，缺省 platforms 的脚本仍通用', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.sourceDir, 'hooks/通用/claude-only.sh'), '#!/bin/sh\necho claude')
  await fs.outputJson(path.join(opts.sourceDir, 'hook-manifests/hooks.json'), [
    { name: 'check.sh', event: 'PreToolUse' },
    { name: 'claude-only.sh', event: 'PreToolUse', platforms: ['claude'] },
  ])
  const oldCodexHook = path.join(opts.projectDir, '.codex/hooks/claude-only.sh')
  await fs.outputFile(oldCodexHook, '# old platform support')
  const operations = await syncAll({ ...opts, contentTypes: ['hooks'] })
  assert.ok(operations.some(operation => operation.paths.includes(oldCodexHook)))
  assert.equal(await fs.pathExists(oldCodexHook), false)
  for (const platform of ['claude', 'codex']) {
    assert.equal(await fs.pathExists(path.join(opts.projectDir, `.${platform}/hooks/check.sh`)), true)
  }
})

test('用户主目录及其别名不能作为项目范围改写全局入口', async t => {
  const opts = await fixture(t)
  const global = path.join(opts.homeDir, '.claude/skills/sample/SKILL.md')
  await fs.outputFile(global, '# keep global')
  for (const projectDir of [opts.homeDir, path.join(opts.projectDir, 'home-alias')]) {
    if (projectDir !== opts.homeDir) await fs.symlink(opts.homeDir, projectDir, 'dir')
    await assert.rejects(syncAll({ ...opts, projectDir, selectedPlatforms: ['claude'], contentTypes: ['skills'] }), /主目录.*全局/)
    assert.equal(await fs.readFile(global, 'utf8'), '# keep global')
  }
})

test('从用户主目录别名执行全局同步，不把全局入口当作项目重复项删除', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.homeDir, '.claude/skills/sample/SKILL.md'), '# existing global')
  const alias = path.join(opts.projectDir, 'home-alias')
  await fs.symlink(opts.homeDir, alias, 'dir')
  const operations = await syncAll({ ...opts, scope: 'global', projectDir: alias,
    selectedPlatforms: ['claude'], contentTypes: ['skills'] })
  assert.equal(operations.some(operation => operation.kind === 'remove-skill'), false)
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/skills/sample/SKILL.md'), 'utf8'), '# v1')
  await assert.rejects(migrateSkills({ ...opts, projectDir: alias }), /主目录.*全局/)
})
