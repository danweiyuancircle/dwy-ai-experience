import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { execFileSync, spawnSync } from 'node:child_process'

test('发布缓存提示只忽略自己的目录，保留其他项目资料', async () => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-publish-cache-'))
  try {
    const script = path.resolve('templates/ai-tools/skills/发布发版/dwy-publish/scripts/release_config.sh')
    const output = execFileSync('bash', [script, 'set', dir, '.', 'generic', 'github-action-oidc', 'npm', 'true'], { encoding: 'utf8' })
    assert.match(output, /\/\.dwy\/publish\//)
    execFileSync('git', ['init', '-q', dir])
    await fs.writeFile(path.join(dir, '.gitignore'), '/.dwy/publish/\n')
    assert.equal(spawnSync('git', ['check-ignore', '-q', '.dwy/publish/config.json'], { cwd: dir }).status, 0)
    assert.equal(spawnSync('git', ['check-ignore', '-q', '.dwy/dwy-project-learning/lessons.md'], { cwd: dir }).status, 1)
  } finally {
    await fs.rm(dir, { recursive: true, force: true })
  }
})
