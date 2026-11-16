import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { fileURLToPath } from 'node:url'
import { scanSkills } from '../src/sync.js'
import { copySkillsToProjectPlatforms } from '../src/sync-global-skills.js'

const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../templates/ai-tools')
const names = ['dwy-dart-development', 'dwy-flutter-architecture', 'dwy-flutter-development', 'dwy-flutter-appkit']

test('Flutter 四个职责入口可发现，随同步安装后本地引用仍可访问', async t => {
  const skills = (await scanSkills(source)).filter(skill => names.includes(skill.name))
  assert.deepEqual(skills.map(skill => skill.name).sort(), [...names].sort())
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-flutter-skills-'))
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
  for (const skill of skills) {
    const projectDir = path.join(root, skill.name)
    await copySkillsToProjectPlatforms({ projectDir, homeDir: path.join(root, 'home'), platforms: ['codex'], skills: [skill] })
    await checkReferences(path.join(projectDir, '.agents/skills', skill.name))
  }
})
