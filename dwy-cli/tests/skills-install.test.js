import test from 'node:test'
import assert from 'node:assert/strict'
import {
  buildInstallCommand,
  buildUpdateCommand,
  buildRemoveCommand,
  runCommands,
} from '../src/skills-install.js'

test('skills-cli install maps to npx skills add -g', () => {
  const cmd = buildInstallCommand({
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
    skills: ['web-design'],
    agents: ['claude-code', 'codex'],
  })
  assert.deepEqual(cmd, {
    cmd: 'npx',
    args: ['skills', 'add', 'vercel-labs/agent-skills', '-g', '-a', 'claude-code,codex', '-s', 'web-design', '-y'],
    label: 'skills-cli: vercel-labs/agent-skills',
  })
})

test('skills-cli install omits -a when agents missing', () => {
  const cmd = buildInstallCommand({
    kind: 'skills-cli',
    source: 'vercel-labs/agent-skills',
  })
  assert.deepEqual(cmd.args, ['skills', 'add', 'vercel-labs/agent-skills', '-g', '-y'])
})

test('claude-plugin install/update/remove', () => {
  assert.deepEqual(
    buildInstallCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'install', 'feature-dev@claude-plugins-official'],
  )
  assert.equal(buildInstallCommand({ kind: 'claude-plugin', source: 'x' }).cmd, 'claude')
  assert.deepEqual(
    buildUpdateCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'update', 'feature-dev@claude-plugins-official'],
  )
  assert.deepEqual(
    buildRemoveCommand({ kind: 'claude-plugin', source: 'feature-dev@claude-plugins-official' }).args,
    ['plugin', 'uninstall', 'feature-dev@claude-plugins-official'],
  )
})

test('claude-marketplace commands', () => {
  assert.deepEqual(
    buildInstallCommand({ kind: 'claude-marketplace', source: 'anthropics/claude-plugins-official' }).args,
    ['plugin', 'marketplace', 'add', 'anthropics/claude-plugins-official'],
  )
  assert.deepEqual(
    buildUpdateCommand({ kind: 'claude-marketplace', source: 'anthropics/claude-plugins-official' }).args,
    ['plugin', 'marketplace', 'update', 'anthropics/claude-plugins-official'],
  )
  assert.deepEqual(
    buildRemoveCommand({ kind: 'claude-marketplace', source: 'anthropics/claude-plugins-official' }).args,
    ['plugin', 'marketplace', 'remove', 'anthropics/claude-plugins-official'],
  )
})

test('codex-plugin install/remove and update expands to remove+add', () => {
  assert.deepEqual(
    buildInstallCommand({ kind: 'codex-plugin', source: 'browser@openai-bundled' }),
    {
      cmd: 'codex',
      args: ['plugin', 'add', 'browser@openai-bundled'],
      label: 'codex-plugin: browser@openai-bundled',
    },
  )
  assert.deepEqual(
    buildRemoveCommand({ kind: 'codex-plugin', source: 'browser@openai-bundled' }).args,
    ['plugin', 'remove', 'browser@openai-bundled'],
  )
  const update = buildUpdateCommand({ kind: 'codex-plugin', source: 'browser@openai-bundled' })
  assert.deepEqual(update.args, ['plugin', 'add', 'browser@openai-bundled'])
  assert.deepEqual(update.prelude[0].args, ['plugin', 'remove', 'browser@openai-bundled'])
})

test('codex-marketplace commands', () => {
  assert.deepEqual(
    buildInstallCommand({ kind: 'codex-marketplace', source: 'owner/repo' }).args,
    ['plugin', 'marketplace', 'add', 'owner/repo'],
  )
  assert.deepEqual(
    buildUpdateCommand({ kind: 'codex-marketplace', source: 'codex-warp' }).args,
    ['plugin', 'marketplace', 'upgrade', 'codex-warp'],
  )
  assert.deepEqual(
    buildRemoveCommand({ kind: 'codex-marketplace', source: 'codex-warp' }).args,
    ['plugin', 'marketplace', 'remove', 'codex-warp'],
  )
})

test('runCommands continues after failure and summarizes', async () => {
  const calls = []
  const result = await runCommands(
    [
      { cmd: 'a', args: ['1'], label: 'one' },
      { cmd: 'b', args: ['2'], label: 'two' },
    ],
    {
      runCommand: async (cmd, args) => {
        calls.push([cmd, ...args])
        if (cmd === 'a') throw new Error('boom')
      },
    },
  )
  assert.deepEqual(calls, [['a', '1'], ['b', '2']])
  assert.equal(result.ok.length, 1)
  assert.equal(result.failed.length, 1)
  assert.match(result.failed[0].error, /boom/)
})
