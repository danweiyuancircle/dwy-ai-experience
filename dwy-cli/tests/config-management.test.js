import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import path from 'node:path'
import os from 'node:os'
import { syncAll } from '../src/sync-all.js'

const baseBlock = '<!-- DWY-BASELINE:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->\n# old baseline\n<!-- DWY-BASELINE:END -->'
const rulesBlock = '<!-- DWY-RULES:START 由 dwy 交互式同步生成，请勿手动编辑此区块 -->\n<!-- dwy-rule: personal.md -->\n# keep rules\n<!-- DWY-RULES:END -->'

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-config-management-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home'), projectDir = path.join(root, 'project')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# managed baseline')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# sample\nproject rules')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '#!/bin/sh\necho checked')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [
    { name: 'check.sh', event: 'PreToolUse', matcher: 'Bash', platforms: ['claude', 'codex'] },
  ])
  return { sourceDir, homeDir, projectDir, codexHome: path.join(homeDir, '.codex'),
    selectedPlatforms: ['claude', 'codex'], selected: { skills: [], rules: [{ name: 'sample.md' }] } }
}

test('项目通用规范、Rules 和手写内容独立更新及移除', async t => {
  const opts = await fixture(t)
  const dest = path.join(opts.projectDir, 'AGENTS.md')
  await fs.outputFile(dest, '# personal project')
  await syncAll({ ...opts, contentTypes: ['baseline', 'rules'] })
  let text = await fs.readFile(dest, 'utf8')
  assert.match(text, /personal project/)
  assert.match(text, /managed baseline/)
  assert.match(text, /project rules/)
  await syncAll({ ...opts, contentTypes: ['rules'], selected: { rules: [] } })
  text = await fs.readFile(dest, 'utf8')
  assert.match(text, /managed baseline/)
  assert.doesNotMatch(text, /project rules/)
  await syncAll({ ...opts, contentTypes: ['rules'] })
  await syncAll({ ...opts, contentTypes: ['baseline'], contentActions: { baseline: 'remove' } })
  text = await fs.readFile(dest, 'utf8')
  assert.match(text, /personal project/)
  assert.match(text, /project rules/)
  assert.doesNotMatch(text, /managed baseline|DWY-BASELINE/)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/CLAUDE.md')), false)
})

test('全局通用规范启停不删除其他块，移除状态可恢复读取', async t => {
  const opts = await fixture(t)
  const dest = path.join(opts.homeDir, '.claude/CLAUDE.md')
  await fs.outputFile(dest, '# personal global\n' + rulesBlock)
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['baseline'] })
  assert.match(await fs.readFile(dest, 'utf8'), /keep rules/)
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['baseline'], contentActions: { baseline: 'remove' } })
  const text = await fs.readFile(dest, 'utf8')
  assert.match(text, /personal global/)
  assert.match(text, /keep rules/)
  assert.doesNotMatch(text, /DWY-BASELINE/)
  const state = await fs.readJson(path.join(opts.homeDir, '.dwy/sync-state.json'))
  assert.equal(state.platforms.claude.baseline, false)
})

test('手写全局 AGENTS 文件不妨碍项目安装；任一选中平台有托管基线则项目只清理重复块', async t => {
  const opts = await fixture(t)
  await fs.outputFile(path.join(opts.codexHome, 'AGENTS.md'), '# personal only')
  await syncAll({ ...opts, contentTypes: ['baseline', 'rules'] })
  assert.match(await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8'), /managed baseline/)
  await fs.outputFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), '# global provider\n' + baseBlock)
  const before = await fs.readFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), 'utf8')
  const operations = await syncAll({ ...opts, contentTypes: ['baseline'] })
  const project = await fs.readFile(path.join(opts.projectDir, 'AGENTS.md'), 'utf8')
  assert.doesNotMatch(project, /DWY-BASELINE/)
  assert.match(project, /project rules/)
  assert.equal(await fs.readFile(path.join(opts.homeDir, '.claude/CLAUDE.md'), 'utf8'), before)
  assert.ok(operations.some(item => /全局/.test(item.label)))
})

test('全局启用规范显式清理当前项目基线，移除全局后不回填项目', async t => {
  const opts = await fixture(t)
  const dest = path.join(opts.projectDir, 'AGENTS.md')
  await fs.outputFile(dest, '# personal project\n' + baseBlock + '\n' + rulesBlock)
  const operations = await syncAll({ ...opts, scope: 'global', contentTypes: ['baseline'] })
  assert.ok(operations.some(item => item.paths.includes(dest)))
  let text = await fs.readFile(dest, 'utf8')
  assert.match(text, /personal project|keep rules/)
  assert.doesNotMatch(text, /DWY-BASELINE/)
  await syncAll({ ...opts, scope: 'global', contentTypes: ['baseline'], contentActions: { baseline: 'remove' } })
  assert.equal(await fs.readFile(dest, 'utf8'), text)
})

test('项目 Hooks 按有效全局注册继承，只补缺少的平台并保留全局提供者', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
  const globalConfig = path.join(opts.homeDir, '.claude/settings.json')
  const before = await fs.readFile(globalConfig, 'utf8')
  await syncAll({ ...opts, contentTypes: ['hooks'] })
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/hooks/check.sh')), false)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.codex/hooks/check.sh')), true)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/settings.json')), false)
  assert.equal(await fs.readFile(globalConfig, 'utf8'), before)
})

test('仅有全局 Hook 文件、错误事件注册或禁用配置时，项目仍安装 Hook', async t => {
  for (const mode of ['file-only', 'wrong-event', 'disabled', 'script-missing']) {
    const opts = await fixture(t)
    await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
    const config = path.join(opts.homeDir, '.claude/settings.json')
    const json = await fs.readJson(config)
    if (mode === 'file-only') delete json.hooks
    if (mode === 'wrong-event') { json.hooks.PostToolUse = json.hooks.PreToolUse; delete json.hooks.PreToolUse }
    if (mode === 'disabled') json.disableAllHooks = true
    if (mode === 'script-missing') await fs.remove(path.join(opts.homeDir, '.claude/hooks/check.sh'))
    await fs.writeJson(config, json)
    await syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
    assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/hooks/check.sh')), true, mode)
  }
})

test('全局启用 Hooks 清理当前项目重复注册和脚本，移除只删托管项并保留个人配置', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
  const localConfig = path.join(opts.projectDir, '.claude/settings.json')
  const personal = { type: 'command', command: 'bash /personal/hooks/check.sh' }
  const config = await fs.readJson(localConfig)
  config.permissions = { allow: ['Read'] }
  config.hooks.PreToolUse[0].hooks.push(personal)
  await fs.writeJson(localConfig, config)
  await fs.outputFile(path.join(opts.projectDir, '.claude/hooks/personal.sh'), '# personal')
  const operations = await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
  assert.ok(operations.some(item => item.paths.includes(localConfig)))
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.claude/hooks/check.sh')), false)
  const after = await fs.readJson(localConfig)
  assert.deepEqual(after.hooks.PreToolUse[0].hooks, [personal])
  assert.deepEqual(after.permissions, { allow: ['Read'] })
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['hooks'], contentActions: { hooks: 'remove' } })
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/hooks/check.sh')), false)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/settings.json')), false)
  assert.equal(await fs.readFile(path.join(opts.projectDir, '.claude/hooks/personal.sh'), 'utf8'), '# personal')
})

test('显式移除已从模板下架的 Hook，同时清理历史注册，保留同名个人路径', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['codex'], contentTypes: ['hooks'] })
  const file = path.join(opts.projectDir, '.codex/hooks.json')
  const config = await fs.readJson(file)
  config.hooks.PreToolUse[0].hooks.push({ type: 'command', command: 'bash /personal/hooks/check.sh' })
  await fs.writeJson(file, config)
  await fs.remove(path.join(opts.sourceDir, 'hooks/Git/check.sh'))
  await fs.outputJson(path.join(opts.sourceDir, 'hook-manifests/hooks.json'), [])
  await syncAll({ ...opts, selectedPlatforms: ['codex'], contentTypes: ['hooks'], contentActions: { hooks: 'remove' } })
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.codex/hooks/check.sh')), false)
  assert.deepEqual((await fs.readJson(file)).hooks.PreToolUse[0].hooks, [{ type: 'command', command: 'bash /personal/hooks/check.sh' }])
})

test('配置目录软链接指向全局时，在确认前拒绝清理，不修改全局提供者', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, scope: 'global', selectedPlatforms: ['claude'], contentTypes: ['hooks'] })
  await fs.symlink(path.join(opts.homeDir, '.claude'), path.join(opts.projectDir, '.claude'), 'dir')
  const dest = path.join(opts.homeDir, '.claude/settings.json')
  const before = await fs.readFile(dest, 'utf8')
  await assert.rejects(syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: ['hooks'] }), /链接|外部/)
  assert.equal(await fs.readFile(dest, 'utf8'), before)
  assert.equal(await fs.pathExists(path.join(opts.homeDir, '.claude/hooks/check.sh')), true)
})

test('AGENTS 和 Hook 配置单文件链接不能穿透修改外部内容', async t => {
  for (const type of ['baseline', 'hooks']) {
    const opts = await fixture(t)
    const target = path.join(opts.homeDir, 'external.txt')
    const body = type === 'hooks' ? '{}' : '# external baseline'
    await fs.outputFile(target, body)
    const dest = path.join(opts.projectDir, type === 'hooks' ? '.claude/settings.json' : 'AGENTS.md')
    await fs.ensureDir(path.dirname(dest))
    await fs.symlink(target, dest)
    await assert.rejects(syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: [type] }), /链接|外部/)
    assert.equal(await fs.readFile(target, 'utf8'), body)
    assert.equal(await fs.pathExists(path.join(opts.projectDir, '.dwy/sync-state.json')), false)
  }
})

test('清理 Hook 只识别完整生成命令，个人组合命令及同名其他路径保留', async t => {
  const opts = await fixture(t)
  const file = path.join(opts.projectDir, '.claude/settings.json')
  const commands = [
    'echo "$HOME/.claude/hooks/check.sh"',
    'bash "$HOME/.claude/hooks/check.sh" && echo personal',
    'bash /personal/.claude/hooks/check.sh',
  ]
  await fs.outputJson(file, { hooks: { PreToolUse: [{ matcher: 'Bash', hooks: commands.map(command => ({ type: 'command', command })) }] }, permissions: { allow: ['Read'] } })
  const before = await fs.readFile(file, 'utf8')
  await syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: ['hooks'], contentActions: { hooks: 'remove' } })
  assert.equal(await fs.readFile(file, 'utf8'), before)
})

test('普通同步保留未确认删除的历史 Hook，显式移除才清理', async t => {
  const opts = await fixture(t)
  await syncAll({ ...opts, selectedPlatforms: ['codex'], contentTypes: ['hooks'] })
  await fs.remove(path.join(opts.sourceDir, 'hooks/Git/check.sh'))
  await fs.outputJson(path.join(opts.sourceDir, 'hook-manifests/hooks.json'), [])
  const file = path.join(opts.projectDir, '.codex/hooks.json')
  const before = await fs.readFile(file, 'utf8')
  await syncAll({ ...opts, selectedPlatforms: ['codex'], contentTypes: ['hooks'], staleRemovals: {} })
  assert.equal(await fs.readFile(file, 'utf8'), before)
  assert.equal(await fs.pathExists(path.join(opts.projectDir, '.codex/hooks/check.sh')), true)
})

test('无效动作和损坏的全局配置在确认前拒绝，不写项目', async t => {
  const opts = await fixture(t)
  await assert.rejects(syncAll({ ...opts, contentTypes: ['hooks'], contentActions: { hooks: 'invalid' } }), /无效/)
  await fs.outputJson(path.join(opts.homeDir, '.claude/settings.json'), { hooks: { PreToolUse: {} } })
  await assert.rejects(syncAll({ ...opts, selectedPlatforms: ['claude'], contentTypes: ['hooks'] }), /格式无效/)
  assert.deepEqual(await fs.readdir(opts.projectDir), [])
})

test('旧无标记基线与 Rules 同轮处理时，先迁移或移除基线再追加规则', async t => {
  for (const action of ['sync', 'remove']) {
    const opts = await fixture(t)
    const dest = path.join(opts.projectDir, 'AGENTS.md')
    await fs.outputFile(dest, '# managed baseline')
    await syncAll({ ...opts, contentTypes: ['baseline', 'rules'], contentActions: { baseline: action } })
    const text = await fs.readFile(dest, 'utf8')
    assert.equal(text.split('# managed baseline').length - 1, action === 'sync' ? 1 : 0, action)
    assert.match(text, /project rules/)
    const state = await fs.readJson(path.join(opts.projectDir, '.dwy/sync-state.json'))
    assert.equal(state.platforms.claude.baseline, action === 'sync')
  }
})
