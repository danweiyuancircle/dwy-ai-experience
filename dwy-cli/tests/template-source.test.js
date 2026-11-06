import test from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
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

test('无 Git、无缓存时可从消费目录读取随包模板', t => {
  assert.equal(resolveInConsumer(t), path.join(cliRoot, 'templates', 'ai-tools'))
})

test('启动直接使用随包模板，不联网、不读取历史模板缓存或锁', t => {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-bundled-source-'))
  t.after(() => removeTemporaryPath(directory, directory))
  const cache = path.join(directory, '.dwy', 'template-source')
  for (const name of ['skills', 'rules', 'hooks']) mkdirSync(path.join(cache, name), { recursive: true })
  writeFileSync(path.join(cache, 'AGENTS.md'), '# Obsolete cache')
  writeFileSync(path.join(directory, '.dwy/template-source.lock'), String(process.pid))
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', `
    import { resolveSourceDir } from ${JSON.stringify(syncURL)};
    globalThis.fetch = () => { throw new Error('Unexpected network'); };
    console.log(await resolveSourceDir({ homeDir: ${JSON.stringify(directory)} }));
  `], { cwd: directory, env: { ...process.env, DWY_HOME: directory, DWY_TEMPLATE_SOURCE_DIR: '', PATH: directory },
    encoding: 'utf8', timeout: 5000 })
  assert.equal(result.status, 0, result.stderr)
  assert.equal(result.stdout.trim(), path.join(cliRoot, 'templates', 'ai-tools'))
  assert.equal(result.stderr, '')
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
