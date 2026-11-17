import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { syncAll, refreshAll } from '../src/sync-all.js'

test('refresh 按实际差异列出共享 Skill、全局 Hook 和项目规则，重复刷新报告无变更', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-changes-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), projectDir = path.join(root, 'project'), homeDir = path.join(root, 'home')
  const codexHome = path.join(homeDir, '.codex')
  const options = { sourceDir, projectDir, homeDir, codexHome }
  await fs.ensureDir(projectDir)
  await fs.outputFile(path.join(sourceDir, 'skills/通用/changed/SKILL.md'), '# Same skill')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/changed/references/guide.md'), 'old guide')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/unchanged/SKILL.md'), '# Same skill')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# Old rule')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '# old hook')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests/hooks.json'), [{ name: 'check.sh', platforms: ['codex'] }])
  await syncAll({ ...options, scope: 'global', selectedPlatforms: ['codex'], selected: { skills: [{ name: 'changed' }, { name: 'unchanged' }] }, contentTypes: ['skills', 'hooks'] })
  await syncAll({ ...options, selectedPlatforms: ['codex'], selected: { rules: [{ name: 'sample.md' }] }, contentTypes: ['rules'] })
  await fs.outputFile(path.join(sourceDir, 'skills/通用/changed/references/guide.md'), 'new guide')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/new-skill/SKILL.md'), '# New skill')
  await fs.outputFile(path.join(sourceDir, 'rules/通用/sample.md'), '# New rule')
  await fs.outputFile(path.join(sourceDir, 'hooks/Git/check.sh'), '# new hook')
  const run = () => execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), 'refresh'], {
    cwd: projectDir, encoding: 'utf8',
    env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: codexHome, NO_COLOR: '1', FORCE_COLOR: '0',
      DWY_HOME: path.join(homeDir, '.dwy'), DWY_TEMPLATE_SOURCE_DIR: sourceDir },
  })
  const output = run()
  const changes = output.split('\n').filter(line => /^\s+(新增|更新|移除) /.test(line))
  for (const [action, dest] of [
    ['新增', path.join(homeDir, '.dwy/skills/new-skill')],
    ['更新', path.join(homeDir, '.dwy/skills/changed')],
    ['更新', path.join(codexHome, 'hooks/check.sh')],
    ['更新', path.join(await fs.realpath(projectDir), 'AGENTS.md')],
  ]) assert.ok(changes.includes(`  ${action} ${dest}`), `应报告 ${action} ${dest}，实际输出：\n${output}`)
  assert.ok(!changes.some(line => line.includes('/unchanged')), '内容未变的 Skill 不应列入变更')
  assert.ok(!output.includes('new guide'), '变更报告不能输出文件正文')
  const repeated = run()
  assert.match(repeated, /无变更/)
  assert.equal(repeated.split('\n').filter(line => /^\s+(新增|更新|移除) /.test(line)).length, 0, repeated)
  assert.equal(await fs.readFile(path.join(homeDir, '.agents/skills/changed/references/guide.md'), 'utf8'), 'new guide')
})

test('refresh 报告 Skill 内文件删除和执行权限变化，忽略修改时间变化', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-file-changes-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home')
  const skill = path.join(sourceDir, 'skills/通用/sample')
  const dest = path.join(homeDir, '.dwy/skills/sample')
  await fs.ensureDir(homeDir)
  await fs.outputFile(path.join(skill, 'SKILL.md'), '# Sample')
  await fs.outputFile(path.join(skill, 'script.sh'), '# script', { mode: 0o644 })
  await fs.outputFile(path.join(skill, 'removed.txt'), 'old')
  const run = () => execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), 'refresh'], {
    cwd: homeDir, encoding: 'utf8',
    env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: path.join(homeDir, '.codex'), NO_COLOR: '1', FORCE_COLOR: '0',
      DWY_HOME: path.join(homeDir, '.dwy'), DWY_TEMPLATE_SOURCE_DIR: sourceDir },
  })
  run()
  await fs.remove(path.join(skill, 'removed.txt'))
  assert.ok(run().includes(`  更新 ${dest}`))
  await fs.chmod(path.join(skill, 'script.sh'), 0o755)
  if (process.platform !== 'win32') assert.ok(run().includes(`  更新 ${dest}`))
  await fs.utimes(path.join(skill, 'SKILL.md'), new Date(0), new Date(0))
  assert.match(run(), /无变更/)
})

test('refresh 区分重复入口移除与坏链接修复，不把保留的历史 Skill 报为移除', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-links-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home'), projectDir = path.join(root, 'project')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# Latest')
  await fs.outputFile(path.join(homeDir, '.agents/skills/sample/SKILL.md'), '# Old global')
  await fs.outputFile(path.join(projectDir, '.agents/skills/sample/SKILL.md'), '# Duplicate')
  await fs.outputFile(path.join(projectDir, '.agents/skills/removed/SKILL.md'), '# Retained')
  await fs.outputJson(path.join(projectDir, '.dwy/sync-state.json'), { platforms: { codex: { skills: ['sample', 'removed'] } } })
  const run = () => execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), 'refresh'], {
    cwd: projectDir, encoding: 'utf8',
    env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: path.join(homeDir, '.codex'), NO_COLOR: '1', FORCE_COLOR: '0',
      DWY_HOME: path.join(homeDir, '.dwy'), DWY_TEMPLATE_SOURCE_DIR: sourceDir },
  })
  const output = run()
  assert.ok(output.includes(`  更新 ${path.join(homeDir, '.agents/skills/sample')}`))
  assert.ok(output.includes(`  移除 ${path.join(await fs.realpath(projectDir), '.agents/skills/sample')}`))
  assert.ok(!output.split('\n').some(line => /^\s+移除 .*\/removed$/.test(line)))
  assert.equal(await fs.readFile(path.join(projectDir, '.agents/skills/removed/SKILL.md'), 'utf8'), '# Retained')
  const dest = path.join(homeDir, '.agents/skills/sample')
  await fs.unlink(dest)
  await fs.symlink(path.join(root, 'missing'), dest, process.platform === 'win32' ? 'junction' : 'dir')
  assert.ok(run().includes(`  更新 ${dest}`))
  assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), '# Latest')
})

for (const installed of [true, false]) {
  test(`refresh 不下载外部 Skills，${installed ? '完整保留旧文件' : '空安装目录保持为空'}`, async t => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-no-external-'))
    t.after(() => fs.remove(root))
    const homeDir = path.join(root, 'home'), projectDir = path.join(root, 'project')
    const sourceDir = path.join(root, 'templates'), dwyHome = path.join(homeDir, '.dwy')
    const targetDir = path.join(dwyHome, 'skills'), binDir = path.join(root, 'bin'), calls = path.join(root, 'git-calls')
    for (const dir of [homeDir, projectDir, sourceDir, targetDir]) await fs.ensureDir(dir)
    const files = {
      'create-prd/SKILL.md': '# Old PRD',
      'brainstorming/SKILL.md': '# Old brainstorming',
      'LICENSE-pm-skills': 'Old PM license',
      'LICENSE-superpowers': 'Old superpowers license',
      'VERSIONS.json': '{"versions":{"brainstorming":{"tag":"old"}}}\n',
    }
    if (installed) for (const [name, content] of Object.entries(files)) await fs.outputFile(path.join(targetDir, name), content)
    await fs.outputFile(path.join(binDir, 'git'), `#!${process.execPath}\nrequire('node:fs').appendFileSync(${JSON.stringify(calls)}, 'git called\\n'); process.exit(1)\n`, { mode: 0o755 })
    execFileSync(process.execPath, [fileURLToPath(new URL('../bin/index.js', import.meta.url)), 'refresh'], {
      cwd: projectDir, encoding: 'utf8',
      env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: path.join(homeDir, '.codex'),
        DWY_HOME: dwyHome, DWY_TEMPLATE_SOURCE_DIR: sourceDir, PATH: `${binDir}${path.delimiter}${process.env.PATH}` },
    })
    assert.equal(await fs.pathExists(calls), false, '本地模板刷新不得调用 Git 或下载外部依赖')
    if (installed) {
      assert.deepEqual((await fs.readdir(targetDir)).sort(), ['LICENSE-pm-skills', 'LICENSE-superpowers', 'VERSIONS.json', 'brainstorming', 'create-prd'])
      for (const [name, content] of Object.entries(files)) assert.equal(await fs.readFile(path.join(targetDir, name), 'utf8'), content)
    } else assert.deepEqual(await fs.readdir(targetDir), [])
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
  assert.equal(await fs.readFile(path.join(homeDir, '.dwy/skills/unselected/SKILL.md'), 'utf8'), '# Unselected')
  assert.equal(await fs.pathExists(path.join(homeDir, '.agents/skills/unselected')), false)
  assert.equal(await fs.pathExists(path.join(projectDir, '.agents/skills/unselected')), false)
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

test('项目交互终端执行 refresh 无需输入，更新全局链接及当前项目已有 Skills', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-tty-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home'), projectDir = path.join(root, 'project')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# Latest')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/global-sample/SKILL.md'), '# Latest global')
  await fs.outputFile(path.join(sourceDir, 'skills/通用/unselected/SKILL.md'), '# Unselected')
  await fs.outputFile(path.join(homeDir, '.dwy/skills/global-sample/SKILL.md'), '# Old global')
  await fs.ensureDir(path.join(homeDir, '.agents/skills'))
  await fs.symlink(path.join(homeDir, '.dwy/skills/global-sample'), path.join(homeDir, '.agents/skills/global-sample'), process.platform === 'win32' ? 'junction' : 'dir')
  await fs.outputFile(path.join(projectDir, '.agents/skills/sample/SKILL.md'), '# Old project')
  await fs.outputFile(path.join(projectDir, '.agents/skills/personal/SKILL.md'), '# Personal')
  const entry = fileURLToPath(new URL('../bin/index.js', import.meta.url))
  execFileSync(process.execPath, ['--input-type=module', '-e', `
    Object.defineProperty(process.stdin, 'isTTY', { value: true })
    Object.defineProperty(process.stdout, 'isTTY', { value: true })
    process.stdin.on = () => { throw new Error('refresh 不得读取交互输入') }
    process.argv = [process.execPath, ${JSON.stringify(entry)}, 'refresh']
    await import(${JSON.stringify(new URL('../bin/index.js', import.meta.url).href)})
  `], {
    cwd: projectDir, encoding: 'utf8', timeout: 5000,
    env: { ...process.env, HOME: homeDir, USERPROFILE: homeDir, CODEX_HOME: path.join(homeDir, '.codex'),
      DWY_HOME: path.join(homeDir, '.dwy'), DWY_TEMPLATE_SOURCE_DIR: sourceDir },
  })
  assert.equal(await fs.readFile(path.join(homeDir, '.agents/skills/global-sample/SKILL.md'), 'utf8'), '# Latest global')
  assert.equal(await fs.readFile(path.join(projectDir, '.agents/skills/sample/SKILL.md'), 'utf8'), '# Latest')
  for (const dir of [homeDir, projectDir]) {
    assert.equal(await fs.pathExists(path.join(dir, '.agents/skills/unselected')), false)
  }
  assert.equal(await fs.readFile(path.join(projectDir, '.agents/skills/personal/SKILL.md'), 'utf8'), '# Personal')
  const backups = await fs.readdir(path.join(projectDir, '.dwy/skill-backups'))
  assert.equal(backups.length, 1)
  assert.equal(await fs.readFile(path.join(projectDir, '.dwy/skill-backups', backups[0], 'SKILL.md'), 'utf8'), '# Old project')
})

test('在主目录的交互终端只准备全部共享 Skills，不进入项目选择或创建启用入口', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-refresh-home-'))
  t.after(() => fs.remove(root))
  const sourceDir = path.join(root, 'templates'), homeDir = path.join(root, 'home')
  await fs.ensureDir(homeDir)
  await fs.outputFile(path.join(sourceDir, 'skills/通用/sample/SKILL.md'), '# Latest')
  await refreshAll({ sourceDir, homeDir, projectDir: homeDir, codexHome: path.join(homeDir, '.codex') })
  assert.deepEqual(await fs.readdir(homeDir), ['.dwy'])
  assert.equal(await fs.readFile(path.join(homeDir, '.dwy/skills/sample/SKILL.md'), 'utf8'), '# Latest')
  assert.equal(await fs.pathExists(path.join(homeDir, '.dwy/sync-state.json')), false)
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
