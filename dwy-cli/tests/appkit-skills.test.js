import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { fileURLToPath } from 'node:url'
import { scanSkills } from '../src/sync.js'
import { copySkillsToProjectPlatforms } from '../src/sync-global-skills.js'

const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../templates/ai-tools')
const retired = ['dwy-eapi', 'dwy-auth', 'dwy-payment', 'dwy-notify', 'dwy-webhooks', 'dwy-apple-notify',
  'dwy-email-notify', 'dwy-wechatpay-notify', 'dwy-device-fingerprint', 'dwy-eui', 'dwy-ekit', 'dwy-admin-kit', 'dwy-auth-web']

test('Python 和 Vue 基础库仅保留统一入口，接入资料随安装分发且引用有效', async t => {
  const skills = await scanSkills(source)
  for (const name of retired) assert.ok(!skills.some(skill => skill.name === name), `旧入口仍可发现：${name}`)
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-appkit-skills-'))
  t.after(() => fs.rm(root, { recursive: true, force: true }))
  async function checkReferences(dir) {
    for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name)
      if (entry.isDirectory()) await checkReferences(file)
      else if (entry.name.endsWith('.md')) {
        const content = await fs.readFile(file, 'utf8')
        for (const [, link] of content.matchAll(/\]\(([^)#]+\.md)(?:#[^)]*)?\)/g)) {
          if (!/^https?:/.test(link)) await fs.access(path.resolve(dir, link))
        }
      }
    }
  }
  for (const [name, documents] of [
    ['dwy-python-appkit', ['eapi/guide.md', 'eapi/v0/breaking.md', 'auth/v0/0.2.0.md', 'payment/v0/0.3.0.md']],
    ['dwy-vue-appkit', ['eui/guide.md', 'eui/v2/breaking.md', 'ekit/guide.md', 'admin-kit/v0/0.3.0.md']],
  ]) {
    const skill = skills.find(item => item.name === name)
    assert.ok(skill, `缺少 ${name}`)
    const projectDir = path.join(root, name)
    await copySkillsToProjectPlatforms({ projectDir, homeDir: path.join(root, 'home'), platforms: ['codex'], skills: [skill] })
    const installed = path.join(projectDir, '.agents/skills', name)
    for (const document of documents) await fs.access(path.join(installed, 'references', document))
    await checkReferences(installed)
  }
})
