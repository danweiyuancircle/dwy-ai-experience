import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import {
  DEFAULT_SKILL_DESTINATIONS,
  GLOBAL_SKILL_DEST_IDS,
  listSkillDestOptions,
  normalizeSkillScope,
  resolveGlobalSkillDir,
  copySkillsToGlobalDirs,
} from '../src/sync-global-skills.js'
import {
  ACTION_INSTALL_SKILLS,
  ACTION_SYNC,
  ACTION_UPGRADE,
  DEFAULT_SELECTION_STYLE,
  DEFAULT_SYNC_MODE,
  normalizeAction,
  normalizeSelectionStyle,
  normalizeSyncMode,
  syncAll,
} from '../src/sync-all.js'

test('default skill destinations is project only', () => {
  assert.deepEqual(DEFAULT_SKILL_DESTINATIONS, ['project'])
  assert.ok(GLOBAL_SKILL_DEST_IDS.includes('grok'))
  assert.ok(GLOBAL_SKILL_DEST_IDS.includes('claude'))
})

test('normalizeSkillScope defaults to project and drops unknown dests', () => {
  assert.deepEqual(normalizeSkillScope(undefined), {
    destinations: ['project'],
    globalSkills: [],
  })
  assert.deepEqual(
    normalizeSkillScope({
      destinations: ['project', 'grok', 'not-a-dest'],
      globalSkills: ['dwy-doubao-tts', ''],
    }),
    {
      destinations: ['project', 'grok'],
      globalSkills: ['dwy-doubao-tts'],
    },
  )
})

test('resolveGlobalSkillDir maps dest ids under injected home', () => {
  const homeDir = '/tmp/dwy-home-fake'
  assert.equal(resolveGlobalSkillDir('project', homeDir), null)
  assert.equal(resolveGlobalSkillDir('claude', homeDir), path.join(homeDir, '.claude', 'skills'))
  assert.equal(resolveGlobalSkillDir('grok', homeDir), path.join(homeDir, '.grok', 'skills'))
  assert.equal(resolveGlobalSkillDir('agents', homeDir), path.join(homeDir, '.agents', 'skills'))
  assert.equal(resolveGlobalSkillDir('cursor', homeDir), path.join(homeDir, '.cursor', 'skills'))
  assert.equal(resolveGlobalSkillDir('opencode', homeDir), path.join(homeDir, '.config', 'opencode', 'skills'))
})

test('listSkillDestOptions puts project first and includes home paths', () => {
  const options = listSkillDestOptions('/tmp/dwy-home-fake')
  assert.equal(options[0].value, 'project')
  assert.ok(options.some(opt => opt.value === 'grok' && opt.description.includes('.grok/skills')))
})

test('copySkillsToGlobalDirs writes only named skills to selected global dests', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-global-skills-'))
  t.after(() => fs.remove(tempDir))
  const homeDir = path.join(tempDir, 'home')
  const skillA = path.join(tempDir, 'src', 'skill-a')
  const skillB = path.join(tempDir, 'src', 'skill-b')
  await fs.outputFile(path.join(skillA, 'SKILL.md'), '# A\n')
  await fs.outputFile(path.join(skillB, 'SKILL.md'), '# B\n')

  const count = await copySkillsToGlobalDirs({
    skills: [
      { name: 'skill-a', sourcePath: skillA },
    ],
    destIds: ['project', 'grok', 'claude'],
    homeDir,
  })

  assert.equal(count, 2)
  assert.equal(await fs.readFile(path.join(homeDir, '.grok', 'skills', 'skill-a', 'SKILL.md'), 'utf-8'), '# A\n')
  assert.equal(await fs.readFile(path.join(homeDir, '.claude', 'skills', 'skill-a', 'SKILL.md'), 'utf-8'), '# A\n')
  assert.equal(await fs.pathExists(path.join(homeDir, '.grok', 'skills', 'skill-b')), false)
  assert.equal(await fs.pathExists(path.join(tempDir, 'project')), false)
})

test('copySkillsToGlobalDirs does not delete unmanaged personal skills', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-global-keep-'))
  t.after(() => fs.remove(tempDir))
  const homeDir = path.join(tempDir, 'home')
  const personal = path.join(homeDir, '.grok', 'skills', 'my-own', 'SKILL.md')
  await fs.outputFile(personal, '# mine\n')
  const skillA = path.join(tempDir, 'src', 'skill-a')
  await fs.outputFile(path.join(skillA, 'SKILL.md'), '# A\n')

  await copySkillsToGlobalDirs({
    skills: [{ name: 'skill-a', sourcePath: skillA }],
    destIds: ['grok'],
    homeDir,
  })

  assert.equal(await fs.readFile(personal, 'utf-8'), '# mine\n')
})

test('syncAll with default skillScope does not write global home skills', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-no-global-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'ai-tools')
  const projectDir = path.join(tempDir, 'project')
  const homeDir = path.join(tempDir, 'home')

  await fs.outputFile(
    path.join(sourceDir, 'skills', '基础', 'dwy-shared', 'SKILL.md'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [])

  await syncAll({
    sourceDir,
    projectDir,
    homeDir,
    selected: { skills: [{ name: 'dwy-shared' }], rules: [], commands: [], hooks: [] },
    selectedPlatforms: ['claude'],
  })

  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md')), true)
  assert.equal(await fs.pathExists(path.join(homeDir, '.grok', 'skills', 'dwy-shared')), false)
  assert.equal(await fs.pathExists(path.join(homeDir, '.claude', 'skills', 'dwy-shared')), false)
})

test('syncAll copies subset of skills to chosen global dests and records scope', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-global-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'ai-tools')
  const projectDir = path.join(tempDir, 'project')
  const homeDir = path.join(tempDir, 'home')

  await fs.outputFile(
    path.join(sourceDir, 'skills', '基础', 'dwy-shared', 'SKILL.md'),
    '---\ndescription: Shared skill\n---\n# Shared skill\n',
  )
  await fs.outputFile(
    path.join(sourceDir, 'skills', '自媒体', 'dwy-doubao-tts', 'SKILL.md'),
    '---\ndescription: TTS\n---\n# TTS\n',
  )
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [])

  await syncAll({
    sourceDir,
    projectDir,
    homeDir,
    selected: {
      skills: [{ name: 'dwy-shared' }, { name: 'dwy-doubao-tts' }],
      rules: [],
      commands: [],
      hooks: [],
    },
    selectedPlatforms: ['claude'],
    skillScope: {
      destinations: ['project', 'grok'],
      globalSkills: ['dwy-doubao-tts'],
    },
  })

  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md')), true)
  assert.equal(await fs.pathExists(path.join(projectDir, '.claude', 'skills', 'dwy-doubao-tts', 'SKILL.md')), true)
  assert.equal(
    await fs.readFile(path.join(homeDir, '.grok', 'skills', 'dwy-doubao-tts', 'SKILL.md'), 'utf-8'),
    '---\ndescription: TTS\n---\n# TTS\n',
  )
  assert.equal(await fs.pathExists(path.join(homeDir, '.grok', 'skills', 'dwy-shared')), false)

  const state = await fs.readJson(path.join(projectDir, '.dwy', 'sync-state.json'))
  assert.deepEqual(state.skillScope.destinations, ['project', 'grok'])
  assert.deepEqual(state.skillScope.globalSkills, ['dwy-doubao-tts'])
})

test('normalizeSyncMode defaults to all and rejects unknown values', () => {
  assert.equal(DEFAULT_SYNC_MODE, 'all')
  assert.equal(normalizeSyncMode(undefined), 'all')
  assert.equal(normalizeSyncMode('skills'), 'skills')
  assert.equal(normalizeSyncMode('nope'), 'all')
})

test('normalizeSelectionStyle defaults to packs and keeps items', () => {
  assert.equal(DEFAULT_SELECTION_STYLE, 'packs')
  assert.equal(normalizeSelectionStyle(undefined), 'packs')
  assert.equal(normalizeSelectionStyle('items'), 'items')
  assert.equal(normalizeSelectionStyle('nope'), 'packs')
})

test('normalizeAction defaults to sync', () => {
  assert.equal(normalizeAction(undefined), ACTION_SYNC)
  assert.equal(normalizeAction(ACTION_INSTALL_SKILLS), ACTION_INSTALL_SKILLS)
  assert.equal(normalizeAction(ACTION_UPGRADE), ACTION_UPGRADE)
  assert.equal(normalizeAction('nope'), ACTION_SYNC)
})

test('skills-only mode writes skills and leaves rules commands hooks untouched', async t => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'dwy-sync-skills-only-'))
  t.after(() => fs.remove(tempDir))
  const sourceDir = path.join(tempDir, 'templates', 'ai-tools')
  const projectDir = path.join(tempDir, 'project')
  const homeDir = path.join(tempDir, 'home')

  await fs.outputFile(
    path.join(sourceDir, 'skills', '基础', 'dwy-shared', 'SKILL.md'),
    '---\ndescription: Shared skill\n---\n# Shared skill new\n',
  )
  await fs.outputFile(
    path.join(sourceDir, 'rules', 'Vue', 'dwy-vue.md'),
    '---\ndescription: Vue rule\n---\n# should not apply\n',
  )
  await fs.outputFile(path.join(sourceDir, 'commands', 'release.md'), '# should not apply\n')
  await fs.outputFile(path.join(sourceDir, 'hooks', 'Git', 'pre-check.sh'), '#!/bin/sh\necho new\n')
  await fs.outputJson(path.join(sourceDir, 'hook-manifests', 'hooks.json'), [
    { name: 'pre-check.sh', event: 'PreToolUse', matcher: 'Bash', platforms: ['claude', 'codex'] },
  ])

  await fs.outputFile(path.join(projectDir, '.claude', 'rules', 'dwy-vue.md'), '# keep rule\n')
  await fs.outputFile(path.join(projectDir, '.claude', 'commands', 'release.md'), '# keep command\n')
  await fs.outputFile(path.join(projectDir, '.claude', 'hooks', 'pre-check.sh'), '#!/bin/sh\necho old\n')
  await fs.outputFile(path.join(projectDir, 'AGENTS.md'), '# keep agents\n')

  await syncAll({
    sourceDir,
    projectDir,
    homeDir,
    syncMode: 'skills',
    selected: {
      skills: [{ name: 'dwy-shared' }],
      rules: [{ name: 'dwy-vue.md' }],
      commands: [{ name: 'release.md' }],
      hooks: [{ name: 'pre-check.sh' }],
    },
    selectedPlatforms: ['claude', 'codex'],
    skillScope: { destinations: ['project'], globalSkills: [] },
  })

  assert.equal(
    await fs.readFile(path.join(projectDir, '.claude', 'skills', 'dwy-shared', 'SKILL.md'), 'utf-8'),
    '---\ndescription: Shared skill\n---\n# Shared skill new\n',
  )
  assert.equal(
    await fs.readFile(path.join(projectDir, '.agents', 'skills', 'dwy-shared', 'SKILL.md'), 'utf-8'),
    '---\ndescription: Shared skill\n---\n# Shared skill new\n',
  )
  assert.equal(await fs.readFile(path.join(projectDir, '.claude', 'rules', 'dwy-vue.md'), 'utf-8'), '# keep rule\n')
  assert.equal(await fs.readFile(path.join(projectDir, '.claude', 'commands', 'release.md'), 'utf-8'), '# keep command\n')
  assert.equal(await fs.readFile(path.join(projectDir, '.claude', 'hooks', 'pre-check.sh'), 'utf-8'), '#!/bin/sh\necho old\n')
  assert.equal(await fs.readFile(path.join(projectDir, 'AGENTS.md'), 'utf-8'), '# keep agents\n')
  assert.equal(await fs.pathExists(path.join(projectDir, '.codex', 'hooks', 'pre-check.sh')), false)

  const state = await fs.readJson(path.join(projectDir, '.dwy', 'sync-state.json'))
  assert.equal(state.syncMode, 'skills')
})

