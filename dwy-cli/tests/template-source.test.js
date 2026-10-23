import test from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { syncAll } from '../src/sync-all.js'
import { readBaselineDoc } from '../src/sync.js'
import { renderTemplate } from '../src/utils.js'

const cliRoot = fileURLToPath(new URL('../', import.meta.url))
const syncURL = new URL('../src/sync.js', import.meta.url).href

function resolveInConsumer(t, sourceDir = '') {
  const directory = mkdtempSync(path.join(tmpdir(), 'dwy-template-source-'))
  t.after(() => rmSync(directory, { recursive: true, force: true }))
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

test('默认读取随包模板，在无 Git、无仓库权限的消费目录也能解析', t => {
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

test('随包基线只使用 AGENTS.md，并保留工具发现与风险评估规则', async () => {
  const sourceDir = path.join(cliRoot, 'templates', 'ai-tools')
  const baseline = await readBaselineDoc(sourceDir)
  assert.equal(baseline, readFileSync(path.join(sourceDir, 'AGENTS.md'), 'utf8'))
  assert.match(baseline, /新功能开发前先找工具/)
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
