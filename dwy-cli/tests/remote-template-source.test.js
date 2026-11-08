import test from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const moduleUrl = new URL('../src/sync.js', import.meta.url).href

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'dwy-remote-template-'))
  t.after(() => {
    assert.equal(path.dirname(root), os.tmpdir())
    assert.ok(path.basename(root).startsWith('dwy-remote-template-'))
    fs.rmSync(root, { recursive: true, force: true })
  })
  const repo = path.join(root, 'remote'), home = path.join(root, 'home')
  fs.mkdirSync(repo)
  const env = Object.fromEntries(Object.entries(process.env).filter(([name]) => !name.startsWith('GIT_')))
  Object.assign(env, { GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null', GIT_TERMINAL_PROMPT: '0' })
  const git = args => execFileSync('git', ['-c', 'core.hooksPath=/dev/null', '-C', repo, ...args], { env, stdio: 'pipe', encoding: 'utf8' })
  git(['init', '--initial-branch=develop'])
  const source = path.join(repo, 'dwy-cli/templates/ai-tools')
  const write = (name, text) => {
    const dest = path.join(source, name)
    fs.mkdirSync(path.dirname(dest), { recursive: true })
    fs.writeFileSync(dest, text)
  }
  const commit = () => {
    git(['add', '--all'])
    git(['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture'])
  }
  write('AGENTS.md', '# 基线\n')
  write('skills/General/first/SKILL.md', '# first\n')
  write('hooks/General/check.sh', '#!/bin/sh\n')
  commit()
  const resolve = (overrides = {}) => {
    const env = { ...process.env, HOME: home, DWY_HOME: '', DWY_TEMPLATE_SOURCE_DIR: '', ...overrides }
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', `
      import { resolveSourceDir } from ${JSON.stringify(moduleUrl)};
      console.log(await resolveSourceDir({ homeDir: ${JSON.stringify(home)}, repository: ${JSON.stringify(repo)} }));
    `], { env, encoding: 'utf8', timeout: 20000 })
    assert.equal(result.status, 0, result.stderr)
    return { directory: result.stdout.trim().split('\n').at(-1), stderr: result.stderr }
  }
  return { root, repo, home, write, commit, resolve }
}

test('从 develop 获取最新 Skills，更新后无需升级 CLI', t => {
  const f = fixture(t)
  const first = f.resolve()
  assert.equal(fs.readFileSync(path.join(first.directory, 'skills/General/first/SKILL.md'), 'utf8'), '# first\n')
  const repository = path.join(f.home, '.dwy/template-repository-v2/.git')
  const inode = fs.statSync(repository).ino
  f.write('skills/General/second/SKILL.md', '# second\n')
  f.commit()
  const second = f.resolve()
  assert.equal(second.directory, first.directory)
  assert.equal(fs.readFileSync(path.join(second.directory, 'skills/General/second/SKILL.md'), 'utf8'), '# second\n')
  assert.equal(fs.statSync(repository).ino, inode)
})

test('远端不可用时保留有效缓存，首次离线回退随包模板', t => {
  const f = fixture(t)
  const first = f.resolve()
  fs.renameSync(f.repo, f.repo + '-offline')
  const cached = f.resolve()
  assert.equal(cached.directory, first.directory)
  assert.match(cached.stderr, /缓存/)
  assert.equal(path.relative(f.root, path.join(f.home, '.dwy')), path.join('home', '.dwy'))
  fs.rmSync(path.join(f.home, '.dwy'), { recursive: true, force: true })
  const bundled = f.resolve()
  assert.match(bundled.directory, /templates\/ai-tools$/)
  assert.match(bundled.stderr, /随包模板/)
})

test('远端存在软链接时不覆盖有效缓存或外部文件', t => {
  const f = fixture(t)
  const first = f.resolve()
  const outside = path.join(f.root, 'outside')
  fs.writeFileSync(outside, '保留')
  fs.symlinkSync(outside, path.join(f.repo, 'dwy-cli/templates/ai-tools/skills/General/evil'))
  f.commit()
  const next = f.resolve()
  assert.equal(next.directory, first.directory)
  assert.equal(fs.readFileSync(outside, 'utf8'), '保留')
  assert.equal(fs.existsSync(path.join(next.directory, 'skills/General/evil')), false)
})

test('未标记的用户目录不作为缓存使用或被覆盖', t => {
  const f = fixture(t)
  const cache = path.join(f.home, '.dwy/template-source')
  fs.mkdirSync(path.join(cache, 'skills'), { recursive: true })
  fs.mkdirSync(path.join(cache, 'hooks'))
  fs.writeFileSync(path.join(cache, 'AGENTS.md'), '# 用户内容')
  const result = f.resolve()
  assert.notEqual(result.directory, cache)
  assert.equal(fs.readFileSync(path.join(cache, 'AGENTS.md'), 'utf8'), '# 用户内容')
  assert.match(result.stderr, /回退随包模板/)
})

test('获取模板不执行环境注入的 Git 配置或远端脚本', t => {
  const f = fixture(t)
  const hooks = path.join(f.root, 'git-hooks'), marker = path.join(f.root, 'executed')
  fs.mkdirSync(hooks)
  fs.writeFileSync(path.join(hooks, 'post-checkout'), `#!/bin/sh\ntouch '${marker}'\n`, { mode: 0o755 })
  f.write('hooks/General/check.sh', `#!/bin/sh\ntouch '${marker}'\n`)
  f.commit()
  f.resolve({ GIT_CONFIG_COUNT: '1', GIT_CONFIG_KEY_0: 'core.hooksPath', GIT_CONFIG_VALUE_0: hooks })
  assert.equal(fs.existsSync(marker), false)
})

test('远端模板不完整时不替换已验证的缓存', t => {
  const f = fixture(t)
  const first = f.resolve()
  fs.rmSync(path.join(f.repo, 'dwy-cli/templates/ai-tools/AGENTS.md'))
  f.commit()
  const result = f.resolve()
  assert.equal(result.directory, first.directory)
  assert.equal(fs.readFileSync(path.join(result.directory, 'AGENTS.md'), 'utf8'), '# 基线\n')
  assert.match(result.stderr, /缓存/)
})

test('失效的更新锁可恢复，存活锁不删除', t => {
  const f = fixture(t)
  const first = f.resolve()
  const lock = path.join(f.home, '.dwy/template-source.lock')
  f.write('skills/General/new/SKILL.md', '# new\n')
  f.commit()
  fs.writeFileSync(lock, String(2147483647))
  assert.equal(fs.existsSync(path.join(f.resolve().directory, 'skills/General/new/SKILL.md')), true)
  fs.writeFileSync(lock, String(process.pid))
  assert.equal(f.resolve().directory, first.directory)
  assert.equal(fs.readFileSync(lock, 'utf8'), String(process.pid))
})
