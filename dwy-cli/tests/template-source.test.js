import test from 'node:test'
import assert from 'node:assert/strict'
import { execFile, execFileSync, spawnSync } from 'node:child_process'
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, renameSync, rmSync, symlinkSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { syncAll } from '../src/sync-all.js'
import { readBaselineDoc } from '../src/sync.js'
import { renderTemplate } from '../src/utils.js'

const cliRoot = fileURLToPath(new URL('../', import.meta.url))
const syncURL = new URL('../src/sync.js', import.meta.url).href

function removeTemporaryPath(directory, target) {
  assert.equal(path.dirname(directory), tmpdir())
  const relative = path.relative(directory, target)
  assert.ok(relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative))
  rmSync(target, { recursive: true, force: true })
}

test('fixture 清理拒绝解析结果回退到真实包内目录', t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-cleanup-guard-'))
  t.after(() => removeTemporaryPath(directory, directory))
  const bundled = path.join(cliRoot, 'templates', 'ai-tools')
  assert.throws(() => removeTemporaryPath(directory, bundled), assert.AssertionError)
  assert.ok(existsSync(path.join(bundled, 'AGENTS.md')))
})

function resolveInConsumer(t, sourceDir = '') {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-template-source-'))
  t.after(() => removeTemporaryPath(directory, directory))
  return execFileSync(process.execPath, ['--input-type=module', '-e', `
    import { resolveSourceDir } from ${JSON.stringify(syncURL)};
    console.log(await resolveSourceDir());
  `], {
    cwd: directory,
    env: { ...process.env, PATH: directory, DWY_HOME: directory, DWY_TEMPLATE_SOURCE_DIR: sourceDir },
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: 5000,
  }).trim()
}

test('无 Git、无缓存时可从消费目录回退到有效随包模板', t => {
  assert.equal(resolveInConsumer(t), path.join(cliRoot, 'templates', 'ai-tools'))
})

test('显式模板目录覆盖随包模板', t => {
  assert.equal(resolveInConsumer(t, cliRoot), cliRoot)
})

test('显式模板目录不存在时保留清楚的错误', t => {
  assert.throws(() => resolveInConsumer(t, path.join(cliRoot, 'missing-template-source')), error => {
    assert.match(error.stderr.toString(), /DWY_TEMPLATE_SOURCE_DIR not found/)
    return true
  })
})

function remoteFixture(t) {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-template-remote-'))
  t.after(() => removeTemporaryPath(directory, directory))
  const remote = path.join(directory, 'remote')
  mkdirSync(remote)
  const git = args => execFileSync('git', ['-C', remote, ...args], { encoding: 'utf8', stdio: 'pipe' })
  git(['init', '--initial-branch=master'])
  const source = path.join(remote, 'dwy-cli', 'templates', 'ai-tools')
  const write = (relative, content) => {
    const file = path.join(source, relative)
    mkdirSync(path.dirname(file), { recursive: true })
    writeFileSync(file, content)
  }
  write('AGENTS.md', '# Remote baseline\n')
  write('skills/Vue/example/SKILL.md', '# Remote example\n')
  write('rules/General/example.md', '# Remote rule\n')
  write('hooks/Codex/example.sh', '#!/bin/sh\nexit 0\n')
  const commit = () => {
    git(['add', '--all'])
    git(['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture'])
  }
  commit()
  const homeDir = path.join(directory, 'home')
  const env = {
    ...process.env,
    DWY_HOME: '',
    DWY_TEMPLATE_SOURCE_DIR: '',
    GIT_CONFIG_NOSYSTEM: '1',
    GIT_CONFIG_GLOBAL: path.join(directory, 'no-global-gitconfig'),
    GIT_CONFIG_COUNT: '1',
    GIT_CONFIG_KEY_0: `url.${pathToFileURL(remote).href}.insteadOf`,
    GIT_CONFIG_VALUE_0: 'https://github.com/danweiyuancircle/dwy-ai-experience.git',
  }
  const diagnostics = []
  const resolve = (overrides = {}) => {
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', `
      import { resolveSourceDir, scanSkills } from ${JSON.stringify(syncURL)};
      import fs from 'node:fs/promises';
      const source = await resolveSourceDir({ homeDir: ${JSON.stringify(homeDir)} });
      console.log(JSON.stringify({ source, baseline: await fs.readFile(source + '/AGENTS.md', 'utf8'),
        skills: (await scanSkills(source)).map(skill => skill.name) }));
    `], { cwd: directory, env: { ...env, ...overrides }, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 10000 })
    assert.equal(result.status, 0, result.stderr)
    diagnostics.push(result.stderr)
    return JSON.parse(result.stdout.trim())
  }
  return { directory, remote, source, homeDir, write, commit, resolve, diagnostics, env }
}

test('首次从固定远端 master 获取模板，新增 Skill 与内容更新无需升级 CLI', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.equal(initial.baseline, '# Remote baseline\n')
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  assert.deepEqual(initial.skills, ['example'])

  fixture.write('skills/Vue/new-skill/SKILL.md', '# New skill\n')
  fixture.write('AGENTS.md', '# Updated remote baseline\n')
  fixture.commit()
  const updated = fixture.resolve()
  assert.equal(updated.source, initial.source)
  assert.equal(updated.baseline, '# Updated remote baseline\n')
  assert.deepEqual(updated.skills.sort(), ['example', 'new-skill'])
})

test('master 没有变化时只检查版本，复用已验证缓存', t => {
  const fixture = remoteFixture(t)
  const trace = path.join(fixture.directory, 'git.trace')
  const first = fixture.resolve({ GIT_TRACE: trace })
  assert.ok(first.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  assert.deepEqual(fixture.resolve({ GIT_TRACE: trace }), first)
  const clones = readFileSync(trace, 'utf8').split('\n').filter(line => /built-in: git .*clone /.test(line))
  assert.equal(clones.length, 1)
})

test('master 更新时复用 Git 对象，只获取增量而不重新克隆整套模板', t => {
  const fixture = remoteFixture(t)
  const trace = path.join(fixture.directory, 'git.trace')
  fixture.resolve({ GIT_TRACE: trace })
  fixture.write('skills/Vue/new-skill/SKILL.md', '# New skill\n')
  fixture.commit()
  assert.deepEqual(fixture.resolve({ GIT_TRACE: trace }).skills.sort(), ['example', 'new-skill'])
  const clones = readFileSync(trace, 'utf8').split('\n').filter(line => /built-in: git .*clone /.test(line))
  assert.equal(clones.length, 1)
})

test('缓存内容损坏时不会只凭相同版本标记跳过校验', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  writeFileSync(path.join(initial.source, 'AGENTS.md'), '')
  assert.deepEqual(fixture.resolve(), initial)
})

test('获取模板不会执行 Git 用户钩子或模板脚本', t => {
  const fixture = remoteFixture(t)
  const hooks = path.join(fixture.directory, 'git-hooks')
  const marker = path.join(fixture.directory, 'executed')
  mkdirSync(hooks)
  writeFileSync(path.join(hooks, 'post-checkout'), `#!/bin/sh\ntouch '${marker}'\n`, { mode: 0o755 })
  fixture.write('hooks/Codex/example.sh', `#!/bin/sh\ntouch '${marker}'\n`)
  fixture.commit()
  const resolved = fixture.resolve({ GIT_CONFIG_COUNT: '2', GIT_CONFIG_KEY_1: 'core.hooksPath', GIT_CONFIG_VALUE_1: hooks })
  assert.ok(resolved.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  assert.equal(existsSync(marker), false)
})

test('网络失败保留有效缓存，无缓存时回退随包模板', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  removeTemporaryPath(fixture.directory, fixture.remote)
  assert.deepEqual(fixture.resolve(), initial)
  assert.match(fixture.diagnostics.at(-1), /更新失败.*缓存/)
  removeTemporaryPath(fixture.directory, path.join(fixture.homeDir, '.dwy'))
  assert.equal(fixture.resolve().source, path.join(cliRoot, 'templates', 'ai-tools'))
  assert.match(fixture.diagnostics.at(-1), /更新失败.*随包模板/)
})

test('没有缓存且随包模板缺失时明确失败，不返回不存在的目录', t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-missing-bundle-'))
  t.after(() => removeTemporaryPath(directory, directory))
  const sourceDir = path.join(directory, 'src')
  mkdirSync(sourceDir)
  writeFileSync(path.join(directory, 'package.json'), '{"type":"module"}')
  symlinkSync(path.join(cliRoot, 'node_modules'), path.join(directory, 'node_modules'))
  for (const name of ['template-source.js', 'utils.js']) copyFileSync(path.join(cliRoot, 'src', name), path.join(sourceDir, name))
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', `
    import { resolveTemplateSource } from ${JSON.stringify(pathToFileURL(path.join(sourceDir, 'template-source.js')).href)};
    console.log(await resolveTemplateSource({ homeDir: ${JSON.stringify(path.join(directory, 'home'))} }));
  `], { cwd: directory, env: { ...process.env, PATH: directory, DWY_HOME: '', DWY_TEMPLATE_SOURCE_DIR: '' },
    encoding: 'utf8', timeout: 5000 })
  assert.equal(result.status, 1)
  assert.match(result.stderr, /ENOENT/)
  assert.ok(result.stderr.includes(path.join(directory, 'templates', 'ai-tools')))
})

test('上次替换中断留下的旧目录会先恢复，不丢失有效缓存', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const previous = path.join(fixture.homeDir, '.dwy', '.template-source.previous')
  renameSync(initial.source, previous)
  removeTemporaryPath(fixture.directory, fixture.remote)
  assert.deepEqual(fixture.resolve(), initial)
  assert.equal(existsSync(previous), false)
})

test('已退出进程遗留的模板锁会自动回收并获取最新 master', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const exited = spawnSync(process.execPath, ['-e', 'console.log(process.pid)'], { encoding: 'utf8' })
  assert.equal(exited.status, 0)
  const pid = Number(exited.stdout.trim())
  assert.throws(() => process.kill(pid, 0), error => error.code === 'ESRCH')
  const lock = path.join(fixture.homeDir, '.dwy', 'template-source.lock')
  writeFileSync(lock, `${pid}\n`)
  writeFileSync(`${lock}.recovery`, `${pid}\n`)
  fixture.write('AGENTS.md', '# After interrupted update\n')
  fixture.commit()
  assert.equal(fixture.resolve().baseline, '# After interrupted update\n')
  assert.equal(existsSync(lock), false)
  assert.equal(existsSync(`${lock}.recovery`), false)
})

test('多个真实进程同时回收死锁时只有一个进程写入新模板', async t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const exited = spawnSync(process.execPath, ['-e', 'console.log(process.pid)'], { encoding: 'utf8' })
  assert.equal(exited.status, 0)
  const pid = Number(exited.stdout.trim())
  assert.throws(() => process.kill(pid, 0), error => error.code === 'ESRCH')
  const lock = path.join(fixture.homeDir, '.dwy', 'template-source.lock')
  writeFileSync(lock, `${pid}\n`)
  fixture.write('AGENTS.md', '# Concurrent update\n')
  fixture.commit()
  const trace = path.join(fixture.directory, 'git.trace')
  const code = `
    import { resolveSourceDir } from ${JSON.stringify(syncURL)};
    console.log(await resolveSourceDir({ homeDir: ${JSON.stringify(fixture.homeDir)} }));
  `
  const sources = await Promise.all(Array.from({ length: 4 }, () => new Promise((resolve, reject) => {
    execFile(process.execPath, ['--input-type=module', '-e', code], {
      cwd: fixture.directory, env: { ...fixture.env, GIT_TRACE: trace }, encoding: 'utf8', timeout: 10000,
    }, (error, stdout) => error ? reject(error) : resolve(stdout.trim()))
  })))
  for (const source of sources) assert.ok([initial.source, path.join(cliRoot, 'templates', 'ai-tools')].includes(source))
  const fetches = readFileSync(trace, 'utf8').split('\n').filter(line => /built-in: git .*fetch --depth=1 --filter=blob:none /.test(line))
  assert.equal(fetches.length, 1)
  assert.equal(fixture.resolve().baseline, '# Concurrent update\n')
  assert.equal(existsSync(lock), false)
})

test('存活进程持有的模板锁保留原样，并阻止第二个更新写入', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const lock = path.join(fixture.homeDir, '.dwy', 'template-source.lock')
  const owner = `${process.pid}\n`
  writeFileSync(lock, owner)
  fixture.write('AGENTS.md', '# Must wait for owner\n')
  fixture.commit()
  assert.deepEqual(fixture.resolve(), initial)
  assert.equal(readFileSync(lock, 'utf8'), owner)
  assert.match(fixture.diagnostics.at(-1), /进程.*正在.*模板/)
  removeTemporaryPath(fixture.directory, lock)
  assert.equal(fixture.resolve().baseline, '# Must wait for owner\n')
})

test('未知或无效模板锁明确提示并保留，不猜测删除', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const lock = path.join(fixture.homeDir, '.dwy', 'template-source.lock')
  for (const owner of ['', 'unknown\n', '0\n', '-1\n']) {
    writeFileSync(lock, owner)
    assert.deepEqual(fixture.resolve(), initial)
    assert.equal(readFileSync(lock, 'utf8'), owner)
    assert.match(fixture.diagnostics.at(-1), /无效.*锁|锁.*无效/)
    removeTemporaryPath(fixture.directory, lock)
  }
})

test('远端模板无效时不替换已验证缓存', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  removeTemporaryPath(fixture.directory, path.join(fixture.source, 'AGENTS.md'))
  fixture.commit()
  assert.deepEqual(fixture.resolve(), initial)
  assert.match(fixture.diagnostics.at(-1), /更新失败/)
})

test('显式 DWY_HOME 优先于注入 homeDir，模板目录覆盖跳过远端更新', t => {
  const fixture = remoteFixture(t)
  const dwyHome = path.join(fixture.directory, 'custom-dwy')
  assert.ok(fixture.resolve({ DWY_HOME: dwyHome }).source.startsWith(dwyHome + path.sep))
  assert.equal(existsSync(path.join(fixture.homeDir, '.dwy')), false)
  assert.equal(fixture.resolve({ DWY_TEMPLATE_SOURCE_DIR: fixture.source, PATH: fixture.directory }).source, fixture.source)
  assert.equal(existsSync(path.join(fixture.homeDir, '.dwy')), false)
})

test('远端软链接不能覆盖有效缓存，缓存入口软链接不能删除外部目录', t => {
  const fixture = remoteFixture(t)
  const initial = fixture.resolve()
  assert.ok(initial.source.startsWith(path.join(fixture.homeDir, '.dwy') + path.sep))
  const outside = path.join(fixture.directory, 'outside')
  mkdirSync(outside)
  writeFileSync(path.join(outside, 'keep.txt'), 'keep')
  symlinkSync(outside, path.join(fixture.source, 'skills', 'Vue', 'outside'))
  fixture.commit()
  assert.deepEqual(fixture.resolve(), initial)
  removeTemporaryPath(fixture.directory, initial.source)
  symlinkSync(outside, initial.source)
  assert.equal(fixture.resolve().source, path.join(cliRoot, 'templates', 'ai-tools'))
  assert.equal(readFileSync(path.join(outside, 'keep.txt'), 'utf8'), 'keep')
})

test('随包基线读取 AGENTS.md 的实际内容，不另维护 CLAUDE.md 副本', async () => {
  const sourceDir = path.join(cliRoot, 'templates', 'ai-tools')
  const baseline = await readBaselineDoc(sourceDir)
  assert.equal(baseline, readFileSync(path.join(sourceDir, 'AGENTS.md'), 'utf8'))
  assert.equal(existsSync(path.join(sourceDir, 'CLAUDE.md')), false)
})

test('项目脚手架统一生成 AGENTS.md，包含嵌套的前后端说明', async t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-agents-templates-'))
  t.after(() => rmSync(directory, { recursive: true, force: true }))
  const context = { projectName: 'example', projectDescription: 'Example', portPrefix: '3',
    scopePrefix: 'example', initialDomain: 'users' }
  for (const [template, expected] of [
    ['backend', ['AGENTS.md']],
    ['web', ['AGENTS.md']],
    ['fullstack-monorepo', ['AGENTS.md', 'backend/AGENTS.md', 'frontend/AGENTS.md']],
  ]) {
    const destination = path.join(directory, template)
    mkdirSync(destination)
    await renderTemplate(path.join(cliRoot, 'templates', 'project', template), destination, context)
    for (const relative of expected) assert.ok(existsSync(path.join(destination, relative)), `${template}/${relative}`)
    const generated = readdirSync(destination, { recursive: true })
    assert.equal(generated.some(name => path.basename(name) === 'CLAUDE.md'), false, template)
  }
})

test('安装在 node_modules 中的模板能同步到各平台，并排除模板内部依赖', async t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-installed-template-'))
  t.after(() => rmSync(directory, { recursive: true, force: true }))
  const sourceDir = path.join(directory, 'node_modules', 'create-dwy', 'templates', 'ai-tools')
  const skillDir = path.join(sourceDir, 'skills', 'Vue', 'example')
  mkdirSync(path.join(skillDir, 'node_modules'), { recursive: true })
  writeFileSync(path.join(skillDir, 'SKILL.md'), '# Example\n')
  writeFileSync(path.join(skillDir, 'node_modules', 'excluded.js'), 'unused')
  const projectDir = path.join(directory, 'project')
  await syncAll({
    sourceDir,
    projectDir,
    homeDir: path.join(directory, 'home'),
    scope: 'project',
    selected: { skills: [{ name: 'example' }], rules: [], commands: [], hooks: [] },
    selectedPlatforms: ['claude', 'codex', 'opencode'],
    confirmed: true,
  })
  for (const platformDir of ['.claude', '.agents', '.opencode']) {
    const destination = path.join(projectDir, platformDir, 'skills', 'example')
    assert.ok(existsSync(path.join(destination, 'SKILL.md')), platformDir)
    assert.equal(existsSync(path.join(destination, 'node_modules')), false, platformDir)
  }
})
