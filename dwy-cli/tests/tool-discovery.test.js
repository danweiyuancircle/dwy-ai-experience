import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { scanSkills } from '../src/sync.js'
import { syncAll } from '../src/sync-all.js'

test('工具发现 Skill 可被分类发现并通过已有同步流程完整安装到各 CLI', async t => {
  const sourceDir = path.resolve('templates/ai-tools')
  const skill = (await scanSkills(sourceDir)).find(item => item.name === 'dwy-tool-discovery')
  assert.ok(skill, '新增 Skill 必须能被 CLI 发现')
  assert.equal(skill.category, '通用')
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-tool-discovery-'))
  t.after(() => fs.remove(root))
  const homeDir = path.join(root, 'home'), projectDir = path.join(root, 'project')
  const codexHome = path.join(homeDir, '.codex')
  await fs.ensureDir(projectDir)
  await syncAll({ sourceDir, projectDir, homeDir, codexHome,
    selectedPlatforms: ['claude', 'codex', 'opencode'], selected: { skills: [skill] }, contentTypes: ['skills'] })
  const original = await fs.readFile(path.join(skill.sourcePath, 'SKILL.md'), 'utf8')
  for (const dir of ['.claude/skills', '.agents/skills', '.opencode/skills']) {
    assert.equal(await fs.readFile(path.join(projectDir, dir, skill.name, 'SKILL.md'), 'utf8'), original)
  }
})
