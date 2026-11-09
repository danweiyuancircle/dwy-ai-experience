import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'

test('发布缓存读写不要求项目配置忽略规则', async () => {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-publish-cache-'))
  try {
    const script = path.resolve('templates/ai-tools/skills/发布发版/dwy-publish/scripts/release_config.sh')
    const output = execFileSync('bash', [script, 'set', dir, '.', 'generic', 'github-action-oidc', 'npm', 'true'], { encoding: 'utf8' })
    assert.doesNotMatch(output, /gitignore/i)
    const data = JSON.parse(execFileSync('bash', [script, 'get', dir, '.'], { encoding: 'utf8' }))
    assert.equal(data.method, 'github-action-oidc')
    const guide = await fs.readFile(path.resolve('templates/ai-tools/skills/发布发版/dwy-publish/references/publish-config.md'), 'utf8')
    assert.doesNotMatch(guide, /gitignore/i)
  } finally {
    await fs.rm(dir, { recursive: true, force: true })
  }
})
