import test from 'node:test'
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { syncAll } from '../src/sync-all.js'
import * as sync from '../src/sync.js'

const items = [
  { name: 'vue-b', category: 'Vue', description: 'Vue B' },
  { name: 'common', category: '通用', description: 'Common' },
  { name: 'vue-a', category: 'Vue', description: 'Vue A' },
  { name: 'uncategorized' },
]

test('分类 Tab 覆盖所有条目，同分类归组并按名称排序，不展开场景包', () => {
  assert.equal(typeof sync.buildCategoryTabs, 'function')
  const tabs = sync.buildCategoryTabs(items, 'skills')
  assert.deepEqual(tabs.map(tab => tab.label).sort(), ['Vue', '其他', '通用'].sort())
  const vue = tabs.find(tab => tab.label === 'Vue')
  assert.deepEqual(vue.options.map(option => option.value), ['vue-a', 'vue-b'])
  assert.equal(vue.options[0].description, 'Vue A')
  assert.equal(vue.options[0].type, 'skills')
  assert.equal(tabs.flatMap(tab => tab.options).length, 4)
  assert.deepEqual(sync.buildCategoryTabs([], 'rules'), [])
})

/** 用真实终端输入驱动选择器，验证分类切换、逐项勾选和阶段顺序。 */
function runSelection(t, scans, defaults, scripts, options = {}) {
  const code = `
    import { interactiveSelect } from './dwy-cli/src/sync.js';
    const defaults = Object.fromEntries(Object.entries(${JSON.stringify(defaults)}).map(([key, names]) => [key, new Set(names)]));
    const result = await interactiveSelect(${JSON.stringify(scans)}, defaults, ${JSON.stringify(options)});
    console.log('RESULT:' + JSON.stringify(result));
  `
  return runProgram(t, code, scripts)
}

function runProgram(t, code, scripts) {
  const child = spawn(process.execPath, ['--input-type=module', '-e', code], {
    cwd: new URL('../../', import.meta.url),
    env: { ...process.env, FORCE_COLOR: '0' },
  })
  t.after(() => child.kill())
  let transcript = ''
  let index = 0
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill()
      reject(new Error(`选择流程超时：${transcript}`))
    }, 5000)
    child.stdout.on('data', chunk => {
      transcript += chunk.toString()
      if (/RESULT:.*\n/.test(transcript)) child.stdin.end()
      if (/下一步：|确认提交还是重选/.test(transcript)) {
        clearTimeout(timer)
        child.kill()
        reject(new Error('选择后仍出现回退或重选菜单'))
        return
      }
      const script = scripts[index]
      if (script && transcript.includes(script.message || `选择 ${script.label}`)) {
        index++
        setTimeout(() => child.stdin.write(script.keys), 30)
      }
    })
    child.stderr.on('data', chunk => { transcript += chunk.toString() })
    child.on('error', reject)
    child.on('close', exitCode => {
      clearTimeout(timer)
      if (exitCode !== 0) {
        reject(new Error(`选择进程退出 ${exitCode}：${transcript}`))
        return
      }
      const result = transcript.match(/RESULT:(.*)/)
      if (!result) {
        reject(new Error(`选择流程未返回结果：${transcript}`))
        return
      }
      resolve({ result: JSON.parse(result[1]), transcript })
    })
  })
}

const scans = {
  skills: [{ name: 'first', category: 'A' }, { name: 'second', category: 'B' }],
  rules: [{ name: 'rule.md', category: '开发流程' }],
  commands: [{ name: 'command.md', category: '文件命令' }],
  hooks: [{ name: 'hook.sh', category: 'Git' }],
}
const defaults = { skills: ['first', 'removed'], rules: [], commands: [], hooks: [] }

test('Skills 后直接选 Rules；按分类勾选，Hooks 自动全选且没有 Commands 交互', async t => {
  const { result, transcript } = await runSelection(t, scans, defaults, [
    { label: 'Skills', keys: ' \u001b[C \r' },
    { label: 'Rules', keys: ' \r' },
  ])
  assert.deepEqual(result, {
    skills: [scans.skills[1]], rules: scans.rules, commands: [], hooks: scans.hooks,
  })
  assert.match(transcript, /切 Tab/)
  assert.ok(transcript.indexOf('选择 Skills') < transcript.indexOf('选择 Rules'))
  assert.doesNotMatch(transcript, /选择 Commands|选择 Hooks|◈|☰|\bskill\s|\brule\s|技能 ·|规则 ·/)
})

test('逐项取消全部勾选可继续，空类别不弹交互', async t => {
  const { result } = await runSelection(t, { ...scans, rules: [], commands: [], hooks: [] }, defaults, [
    { label: 'Skills', keys: ' \r' },
  ])
  assert.deepEqual(result, { skills: [], rules: [], commands: [], hooks: [] })
})

test('仅 Skills 模式不进入其他类别', async t => {
  const { result, transcript } = await runSelection(t, scans, defaults, [
    { label: 'Skills', keys: '\r' },
  ], { skillsOnly: true })
  assert.deepEqual(result, { skills: [scans.skills[0]], rules: [], commands: [], hooks: [] })
  assert.doesNotMatch(transcript, /选择 Rules|选择 Commands|选择 Hooks/)
})

test('全局已提供条目禁用，Space 和全选均不能把它加入项目选择', async t => {
  const covered = { ...scans.skills[0], disabled: true, label: 'first（全局已启用）' }
  const { result, transcript } = await runSelection(t, { ...scans, skills: [covered, scans.skills[1]] }, defaults, [
    { label: 'Skills', keys: ' a\u001b[Ca\r' },
  ], { types: ['skills'] })
  assert.deepEqual(result.skills, [scans.skills[1]])
  assert.deepEqual(result.rules, [])
  assert.deepEqual(result.hooks, [])
  assert.match(transcript, /全局已启用/)
  assert.doesNotMatch(transcript, /选择 Rules/)
})

test('中途取消终止整次选择，不进入下一类', async t => {
  const { result, transcript } = await runSelection(t, scans, defaults, [
    { label: 'Skills', keys: '\u001b' },
  ])
  assert.equal(result, null)
  assert.doesNotMatch(transcript, /选择 Rules/)
})


test('显式选择 Hooks 后自动安装支持项，旧包记录不展开，Commands 保留', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-selection-sync-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates')
  const projectDir = path.join(tempDir, 'project')
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'keep', 'SKILL.md'), '# Keep')
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'unselected', 'SKILL.md'), '# Unselected')
  await fs.outputFile(path.join(sourceDir, 'rules', 'Vue', 'vue.md'), '# Vue')
  await fs.outputFile(path.join(sourceDir, 'commands', 'old.md'), '# New command')
  await fs.outputFile(path.join(sourceDir, 'hooks', 'Git', 'check.sh'), '#!/bin/sh\nexit 0')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [
    { name: 'check.sh', event: 'PreToolUse', matcher: 'Bash', platforms: ['claude', 'codex'] },
  ])
  for (const platform of ['.claude', '.opencode']) {
    await fs.outputFile(path.join(projectDir, platform, 'commands', 'old.md'), '# Local command')
  }
  await fs.outputJson(path.join(projectDir, '.dwy', 'sync-state.json'), {
    version: 1,
    selectionStyle: 'packs',
    packs: { stacks: ['common', 'vue'], scenes: [] },
    platforms: { claude: { skills: ['keep'], rules: ['vue.md'], commands: ['old.md'], hooks: [] } },
  })
  const options = {
    sourceDir, projectDir, homeDir: path.join(tempDir, 'home'), selectedPlatforms: ['claude', 'codex', 'opencode'], syncMode: 'all',
    contentTypes: ['skills', 'rules', 'hooks'],
    skillScope: { destinations: ['project'], globalSkills: [] }, staleRemovals: {}, confirmed: true,
  }
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)});
    console.log('RESULT:{}');
  `, [{ label: 'Skills', keys: '\r' }, { label: 'Rules', keys: '\r' }, { message: '选择 Hooks 操作', keys: '\r' }])
  assert.doesNotMatch(transcript, /项目配置怎么勾|选择技术栈和场景包|选择 Commands/)
  assert.match(transcript, /选择 Hooks 操作/)
  for (const platform of ['.claude', '.agents', '.opencode']) {
    assert.equal(await fs.pathExists(path.join(projectDir, platform, 'skills', 'keep', 'SKILL.md')), true)
    assert.equal(await fs.pathExists(path.join(projectDir, platform, 'skills', 'unselected')), false)
  }
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'hooks', 'check.sh')), true)
  assert.equal(await fs.pathExists(path.join(projectDir, '.codex', 'hooks', 'check.sh')), true)
  assert.equal(await fs.pathExists(path.join(projectDir, '.opencode', 'hooks')), false)
  const claudeSettings = await fs.readJson(path.join(projectDir, '.claude', 'settings.json'))
  const codexSettings = await fs.readJson(path.join(projectDir, '.codex', 'hooks.json'))
  assert.equal(claudeSettings.hooks.PreToolUse[0].hooks.length, 1)
  assert.equal(codexSettings.hooks.PreToolUse[0].hooks.length, 1)
  const state = await fs.readJson(path.join(projectDir, '.dwy', 'sync-state.json'))
  assert.deepEqual(state.platforms.claude.hooks, ['check.sh'])
  assert.equal('packs' in state, false)
  await syncAll({ ...options, contentTypes: ['rules'], selectedPlatforms: ['cursor'], selected: { skills: [], rules: [], commands: [], hooks: [] } })
  for (const platform of ['.claude', '.opencode']) {
    assert.equal(await fs.readFile(path.join(projectDir, platform, 'commands', 'old.md'), 'utf-8'), '# Local command')
  }
})


test('全局旧 Rules 不会成为新项目的默认选择', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-rule-defaults-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates')
  const projectDir = path.join(root, 'project')
  const homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# Baseline')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# Skill')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# Rule')
  await fs.outputJson(path.join(homeDir, '.dwy/sync-state.json'), {
    version: 1, platforms: { claude: { rules: ['sample.md'] } },
  })
  const options = { sourceDir, projectDir, homeDir, selectedPlatforms: ['claude'], scope: 'project', contentTypes: ['skills', 'rules'], confirmed: true }
  await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)});
    console.log('RESULT:{}');
  `, [{ label: 'Skills', keys: '\r' }, { label: 'Rules', keys: '\r' }])
  assert.equal(await fs.pathExists(path.join(projectDir, 'AGENTS.md')), false)
  const state = await fs.readJson(path.join(projectDir, '.dwy/sync-state.json'))
  assert.deepEqual(state.platforms.claude.rules, [])
})

test('主交互按范围、平台、内容类型、逐项选择和确认完成，取消前不写入', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-flow-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates')
  const projectDir = path.join(root, 'project')
  const homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'skills', '通用', 'sample', 'SKILL.md'), '# Skill')
  await fs.outputFile(path.join(sourceDir, 'rules', '通用', 'sample.md'), '# Rule')
  const { transcript } = await runProgram(t, `
    import { runDwy } from './dwy-cli/src/sync-all.js';
    await runDwy(${JSON.stringify({ sourceDir, projectDir, homeDir })});
    console.log('RESULT:{}');
  `, [
    { message: '选择同步范围', keys: '\r' },
    { message: '选择要同步的平台', keys: '\r' },
    { message: '选择本次处理内容', keys: '\u001b[B \r' },
    { label: 'Skills', keys: ' \r' },
    { label: 'Rules', keys: ' \r' },
    { message: '确认同步？', keys: '\u001b' },
  ])
  const messages = ['选择同步范围', '选择要同步的平台', '选择本次处理内容', '选择 Skills', '选择 Rules', '确认同步？']
  for (let i = 1; i < messages.length; i++) assert.ok(transcript.indexOf(messages[i - 1]) < transcript.indexOf(messages[i]))
  assert.doesNotMatch(transcript, /选择要做的事|是否在此初始化|哪些 skill 额外同步到全局|完整同步还是仅 Skills/)
  assert.match(transcript, /Skills：sample/)
  assert.match(transcript, /Rules：sample.md/)
  assert.deepEqual(await fs.readdir(projectDir), [])
  assert.equal(await fs.pathExists(homeDir), false)
})

test('全局主交互首次默认 Skills 和通用规范，确认后不写项目或 Hooks', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-global-flow-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# global skill')
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# baseline')
  const { transcript } = await runProgram(t, `
    import { runDwy } from './dwy-cli/src/sync-all.js';
    await runDwy(${JSON.stringify({ sourceDir, projectDir, homeDir })});
    console.log('RESULT:{}');
  `, [
    { message: '选择同步范围', keys: '\u001b[B\r' },
    { message: '选择要同步的平台', keys: '\r' },
    { message: '选择本次处理内容', keys: '\r' },
    { label: 'Skills', keys: ' \r' },
    { message: '选择 AGENTS.md 通用规范 操作', keys: '\r' },
    { message: '确认同步？', keys: '\r' },
  ])
  assert.match(transcript, /同步范围：全局/)
  assert.match(transcript, /处理内容：Skills、AGENTS.md 通用规范/)
  assert.doesNotMatch(transcript, /选择 Rules|选择 Hooks/)
  assert.deepEqual(await fs.readdir(projectDir), [])
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude/skills/sample/SKILL.md')), true)
  assert.equal(await fs.pathExists(path.join(homeDir, '.agents/skills/sample/SKILL.md')), true)
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude/CLAUDE.md')), true)
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude/settings.json')), false)
})

test('全局和项目只恢复自身默认勾选，不把另一范围的 Skills 带过来', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-scope-defaults-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  for (const name of ['global-only', 'project-only']) await fs.outputFile(path.join(sourceDir, 'skills/通用', name, 'SKILL.md'), '# ' + name)
  await fs.outputFile(path.join(homeDir, '.claude/skills/global-only/SKILL.md'), '# global original')
  await fs.outputFile(path.join(projectDir, '.claude/skills/project-only/SKILL.md'), '# project original')
  const options = { sourceDir, projectDir, homeDir, selectedPlatforms: ['claude'], contentTypes: ['skills'], confirmed: true }
  for (const scope of ['global', 'project']) {
    const { transcript } = await runProgram(t, `
      import { syncAll } from './dwy-cli/src/sync-all.js';
      await syncAll(${JSON.stringify({ ...options, scope })}); console.log('RESULT:{}');
    `, [{ label: 'Skills', keys: '\r' }])
    if (scope === 'project') assert.match(transcript, /global-only（全局已启用）/)
  }
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude/skills/project-only')), false)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude/skills/global-only')), false)
  assert.equal((await fs.lstat(path.join(projectDir, '.claude/skills/project-only'))).isSymbolicLink(), true)
})

test('部分平台全局已提供时仍能勾选，只为缺少入口的平台安装', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-partial-global-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# new')
  await fs.outputFile(path.join(homeDir, '.claude/skills/sample/SKILL.md'), '# existing global')
  const options = { sourceDir, projectDir, homeDir, scope: 'project', selectedPlatforms: ['claude', 'codex'], contentTypes: ['skills'], confirmed: true }
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)}); console.log('RESULT:{}');
  `, [{ label: 'Skills', keys: ' \r' }])
  assert.match(transcript, /Codex 可安装到项目/)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude/skills/sample')), false)
  assert.equal((await fs.lstat(path.join(projectDir, '.agents/skills/sample'))).isSymbolicLink(), true)
  assert.equal(await fs.readFile(path.join(homeDir, '.claude/skills/sample/SKILL.md'), 'utf8'), '# existing global')
})

test('全局规范移除后默认不复选，混合新平台也不重新启用', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-baseline-defaults-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# baseline')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# sample')
  await syncAll({ sourceDir, projectDir, homeDir, scope: 'global', selectedPlatforms: ['claude'], selected: {},
    contentTypes: ['baseline'], contentActions: { baseline: 'remove' } })
  const options = { sourceDir, projectDir, homeDir, scope: 'global', selectedPlatforms: ['claude', 'codex'], confirmed: true }
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)}); console.log('RESULT:{}');
  `, [{ message: '选择本次处理内容', keys: '\r' }, { label: 'Skills', keys: '\r' }])
  assert.doesNotMatch(transcript, /选择 AGENTS.md 通用规范 操作/)
  assert.match(transcript, /处理内容：Skills\s/)
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude/CLAUDE.md')), false)
  assert.equal(await fs.pathExists(path.join(homeDir, '.codex/AGENTS.md')), false)
  assert.equal((await fs.readJson(path.join(homeDir, '.dwy/sync-state.json'))).platforms.claude.baseline, false)
})

test('项目发现任一所选 CLI 已有全局规范时，动作页只能继承或移除', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-inherit-baseline-ui-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'AGENTS.md'), '# baseline')
  await syncAll({ sourceDir, projectDir, homeDir, scope: 'global', selectedPlatforms: ['claude'], selected: {}, contentTypes: ['baseline'] })
  const options = { sourceDir, projectDir, homeDir, scope: 'project', selectedPlatforms: ['claude', 'codex'], contentTypes: ['baseline'], confirmed: true }
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)}); console.log('RESULT:{}');
  `, [{ message: '选择 AGENTS.md 通用规范 操作', keys: '\r' }])
  assert.match(transcript, /使用全局，仅清理项目重复基线/)
  assert.doesNotMatch(transcript, /启用 \/ 更新/)
  assert.equal(await fs.pathExists(path.join(projectDir, 'AGENTS.md')), false)
})

test('Hooks 移除通过动作页选择，最终取消保持脚本、配置和同步记录', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-remove-hooks-ui-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '#!/bin/sh\necho hook')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', event: 'PreToolUse', platforms: ['claude'] }])
  const options = { sourceDir, projectDir, homeDir, selectedPlatforms: ['claude'], contentTypes: ['hooks'] }
  await syncAll({ ...options, selected: {} })
  const files = ['.claude/hooks/check.sh', '.claude/settings.json', '.dwy/sync-state.json']
  const before = await Promise.all(files.map(file => fs.readFile(path.join(projectDir, file), 'utf8')))
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)}); console.log('RESULT:{}');
  `, [{ message: '选择 Hooks 操作', keys: '\u001b[B\r' }, { message: '确认同步？', keys: '\u001b' }])
  assert.match(transcript, /移除 Claude Code 项目 托管 Hooks/)
  assert.deepEqual(await Promise.all(files.map(file => fs.readFile(path.join(projectDir, file), 'utf8'))), before)
})

test('项目 Hooks 全部已有全局提供者时，动作页只提供继承清理', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-inherit-hooks-ui-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '#!/bin/sh\necho hook')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', event: 'PreToolUse', platforms: ['claude'] }])
  const options = { sourceDir, projectDir, homeDir, selectedPlatforms: ['claude'], contentTypes: ['hooks'] }
  await syncAll({ ...options, scope: 'global', selected: {} })
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify({ ...options, confirmed: true })}); console.log('RESULT:{}');
  `, [{ message: '选择 Hooks 操作', keys: '\r' }])
  assert.match(transcript, /使用全局，仅清理项目重复 Hooks/)
  assert.doesNotMatch(transcript, /启用 \/ 更新/)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude')), false)
})
