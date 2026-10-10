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

test('中途取消终止整次选择，不进入下一类', async t => {
  const { result, transcript } = await runSelection(t, scans, defaults, [
    { label: 'Skills', keys: '\u001b' },
  ])
  assert.equal(result, null)
  assert.doesNotMatch(transcript, /选择 Rules/)
})


test('完整同步自动安装 Hooks，旧包记录不展开；停用 Commands 后原文件保留', async t => {
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
    sourceDir, projectDir, selectedPlatforms: ['claude', 'codex', 'opencode'], syncMode: 'all',
    skillScope: { destinations: ['project'], globalSkills: [] }, staleRemovals: {}, confirmed: true,
  }
  const { transcript } = await runProgram(t, `
    import { syncAll } from './dwy-cli/src/sync-all.js';
    await syncAll(${JSON.stringify(options)});
    console.log('RESULT:{}');
  `, [{ label: 'Skills', keys: '\r' }, { label: 'Rules', keys: '\r' }])
  assert.doesNotMatch(transcript, /项目配置怎么勾|选择技术栈和场景包|选择 Commands|选择 Hooks/)
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
  await syncAll({ ...options, selectedPlatforms: ['cursor'], selected: { skills: [], rules: [], commands: [], hooks: [] } })
  for (const platform of ['.claude', '.opencode']) {
    assert.equal(await fs.readFile(path.join(projectDir, platform, 'commands', 'old.md'), 'utf-8'), '# Local command')
  }
})


test('主交互按内容、位置、平台、确认完成，取消前不写入', async t => {
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
    { label: 'Skills', keys: ' \r' },
    { label: 'Rules', keys: ' \r' },
    { message: '选择同步位置', keys: '\r' },
    { message: '选择要同步的平台', keys: '\r' },
    { message: '确认同步？', keys: '\u001b' },
  ])
  const messages = ['选择 Skills', '选择 Rules', '选择同步位置', '选择要同步的平台', '确认同步？']
  for (let i = 1; i < messages.length; i++) assert.ok(transcript.indexOf(messages[i - 1]) < transcript.indexOf(messages[i]))
  assert.doesNotMatch(transcript, /选择要做的事|是否在此初始化|哪些 skill 额外同步到全局|完整同步还是仅 Skills/)
  assert.match(transcript, /Skills：sample/)
  assert.match(transcript, /Rules：sample.md/)
  assert.deepEqual(await fs.readdir(projectDir), [])
  assert.equal(await fs.pathExists(homeDir), false)
})
