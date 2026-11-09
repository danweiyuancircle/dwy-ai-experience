import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { scanSkills } from '../src/sync.js'

test('项目经验技能可被发现，基线引导按项目读取和保存经验', async () => {
  const source = path.resolve('templates/ai-tools')
  const skill = (await scanSkills(source)).find(item => item.name === 'dwy-project-learning')
  assert.ok(skill)
  const content = await fs.readFile(path.join(skill.sourcePath, 'SKILL.md'), 'utf8')
  assert.match(content, /\.dwy\/dwy-project-learning\/lessons\.md/)
  assert.match(content, /AGENTS\.md/)
  const baseline = await fs.readFile(path.join(source, 'AGENTS.md'), 'utf8')
  assert.match(baseline, /dwy-project-learning/)
  assert.doesNotMatch(baseline, /追加到 `project-rules\.md`/)
})
