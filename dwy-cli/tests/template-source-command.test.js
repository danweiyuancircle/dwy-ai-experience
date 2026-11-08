import test from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

test('source 命令查看、修改和清除本地模板路径，并保护无效输入', t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'dwy-source-command-'))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  const home = path.join(root, 'home')
  const repo = path.join(root, 'repository with spaces')
  const templates = path.join(repo, 'dwy-cli/templates/ai-tools')
  fs.mkdirSync(path.join(templates, 'skills'), { recursive: true })
  fs.mkdirSync(path.join(templates, 'hooks'))
  fs.writeFileSync(path.join(templates, 'AGENTS.md'), '# baseline')
  const bin = fileURLToPath(new URL('../bin/index.js', import.meta.url))
  const run = (...args) => spawnSync(process.execPath, [bin, ...args], {
    cwd: root, encoding: 'utf8', env: { ...process.env, HOME: home, DWY_HOME: '', DWY_TEMPLATE_SOURCE_DIR: '' },
  })
  assert.match(run('source').stdout, /未配置/)
  assert.equal(run('source', repo).status, 0)
  const config = path.join(home, '.dwy/template-source.json')
  assert.equal(JSON.parse(fs.readFileSync(config, 'utf8')).localPath, repo)
  fs.writeFileSync(config, JSON.stringify({ localPath: repo, note: '保留' }))
  assert.match(run('source').stdout, /repository with spaces/)
  assert.notEqual(run('source', path.join(root, 'missing')).status, 0)
  assert.equal(JSON.parse(fs.readFileSync(config, 'utf8')).localPath, repo)
  assert.equal(run('source', '--clear').status, 0)
  assert.equal(JSON.parse(fs.readFileSync(config, 'utf8')).note, '保留')
  assert.match(run('source').stdout, /未配置/)
  fs.writeFileSync(config, '{')
  assert.notEqual(run('source', repo).status, 0)
  assert.equal(fs.readFileSync(config, 'utf8'), '{')
})
