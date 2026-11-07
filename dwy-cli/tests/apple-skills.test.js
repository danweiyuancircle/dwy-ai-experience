import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { scanRules, scanSkills } from '../src/sync.js'
import { copySkillsToProjectPlatforms } from '../src/sync-global-skills.js'

const source = path.resolve('templates/ai-tools')
const names = ['dwy-swift-development', 'dwy-apple-architecture', 'dwy-ios-development', 'dwy-macos-development']

test('Apple 开发技能可发现且引用的本地资料存在，旧规则不再作为独立规则分发', async () => {
  const skills = await scanSkills(source)
  const rules = await scanRules(source)
  for (const name of names) {
    const skill = skills.find(item => item.name === name)
    assert.ok(skill, `缺少 ${name}`)
    const content = await fs.readFile(path.join(skill.sourcePath, 'SKILL.md'), 'utf8')
    assert.match(content, new RegExp(`name: ${name}`))
    for (const [, reference] of content.matchAll(/\]\((references\/[^)]+)\)/g)) {
      await fs.access(path.join(skill.sourcePath, reference))
    }
  }
  for (const name of ['dwy-swift-core.md', 'dwy-apple-layering.md', 'dwy-ios-layout-adaptation.md', 'dwy-ios-pitfalls.md']) {
    assert.ok(!rules.some(rule => rule.name === name), `旧规则仍被发现: ${name}`)
  }
})

test('四个技能经现有同步流程安装后参考文件可访问', async () => {
  const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-apple-skills-'))
  try {
    const skills = (await scanSkills(source)).filter(item => names.includes(item.name))
    await copySkillsToProjectPlatforms({ projectDir: path.join(temp, 'project'), homeDir: path.join(temp, 'home'), platforms: ['codex'], skills })
    for (const skill of skills) {
      const entry = path.join(temp, 'project', '.agents', 'skills', skill.name)
      const content = await fs.readFile(path.join(entry, 'SKILL.md'), 'utf8')
      for (const [, reference] of content.matchAll(/\]\((references\/[^)]+)\)/g)) {
        await fs.access(path.join(entry, reference))
      }
    }
    assert.equal(skills.length, names.length)
  } finally {
    await fs.rm(temp, { recursive: true, force: true })
  }
})
