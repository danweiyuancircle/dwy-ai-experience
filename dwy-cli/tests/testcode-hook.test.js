import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const hook = fileURLToPath(new URL('../templates/ai-tools/hooks/Git/pre-git-commit-testcode-check.sh', import.meta.url))

test('TESTCODE 根据暂存内容拦截，确认只适用于同一棵树', t => {
  const cwd = mkdtempSync(path.join(tmpdir(), 'dwy-testcode-'))
  t.after(() => rmSync(cwd, { recursive: true, force: true }))
  const git = (...args) => execFileSync('git', args, { cwd, encoding: 'utf8' }).trim()
  const check = command => spawnSync('bash', [hook], {
    cwd, encoding: 'utf8', input: JSON.stringify({ cwd, tool_input: { command } }),
  })
  git('init', '-q')
  const file = path.join(cwd, 'Sample Activity.java')
  const marker = '// TESTCODE: liuyongjie 2026/11/26'
  writeFileSync(file, [marker, 'ToastUtil.show(this, "patch success", true);', marker].join('\n'))
  git('add', '.')
  writeFileSync(file, 'showNormalMessage();\n')
  const command = 'git commit -m fix'
  const blocked = check(command)
  assert.equal(blocked.status, 2)
  assert.match(blocked.stderr, /Sample Activity\.java:1:/)
  const approved = 'git -c dwy.testcodeConfirmed=' + git('write-tree') + ' commit -m fix'
  assert.equal(check(approved).status, 0)
  writeFileSync(path.join(cwd, 'other'), 'change')
  git('add', 'other')
  assert.equal(check(approved).status, 2)
  assert.equal(check('git add . && git commit -m fix').status, 2)
  assert.equal(check('git commit -am fix').status, 2)
  git('add', '.')
  assert.equal(check(command).status, 0)

  for (const temporary of ['// MOCK: 临时返回成功', '# mock：联调', '// MOCK']) {
    writeFileSync(file, temporary + '\n')
    git('add', '.')
    assert.equal(check(command).status, 2, temporary)
    assert.equal(check(approved).status, 2)
    assert.equal(check('git -c dwy.testcodeConfirmed=' + git('write-tree') + ' commit -m fix').status, 0)
  }
  writeFileSync(file, '// mock server for this test\n')
  writeFileSync(path.join(cwd, 'service.test.js'), "vi.mock('./service');\n")
  writeFileSync(path.join(cwd, 'fixture.json'), '{"mock": true}\n')
  git('add', '.')
  assert.equal(check(command).status, 0)
})
