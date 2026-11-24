/**
 * 将收藏条目映射为官方安装命令，并按序执行。
 * dwy 不下载第三方内容；失败单条记录后继续。
 */

import { spawn } from 'node:child_process'

/**
 * @typedef {{ cmd: string, args: string[], label: string }} OfficialCommand
 * @typedef {{ kind: string, source: string, skills?: string[], agents?: string[], id?: string }} CatalogLike
 */

/** @param {CatalogLike} entry @returns {OfficialCommand} */
export function buildInstallCommand(entry) {
  if (entry.kind === 'skills-cli') {
    const args = ['skills', 'add', entry.source, '-g']
    if (entry.agents?.length) args.push('-a', entry.agents.join(','))
    if (entry.skills?.length) args.push('-s', entry.skills.join(','))
    args.push('-y')
    return { cmd: 'npx', args, label: `skills-cli: ${entry.source}` }
  }
  if (entry.kind === 'claude-plugin') {
    return {
      cmd: 'claude',
      args: ['plugin', 'install', entry.source],
      label: `claude-plugin: ${entry.source}`,
    }
  }
  if (entry.kind === 'claude-marketplace') {
    return {
      cmd: 'claude',
      args: ['plugin', 'marketplace', 'add', entry.source],
      label: `claude-marketplace: ${entry.source}`,
    }
  }
  if (entry.kind === 'codex-plugin') {
    return {
      cmd: 'codex',
      args: ['plugin', 'add', entry.source],
      label: `codex-plugin: ${entry.source}`,
    }
  }
  if (entry.kind === 'codex-marketplace') {
    return {
      cmd: 'codex',
      args: ['plugin', 'marketplace', 'add', entry.source],
      label: `codex-marketplace: ${entry.source}`,
    }
  }
  throw new Error(`未知 kind: ${entry.kind}`)
}

/** @param {CatalogLike} entry @returns {OfficialCommand} */
export function buildUpdateCommand(entry) {
  if (entry.kind === 'skills-cli') {
    const names = entry.skills?.length ? entry.skills : []
    const args = ['skills', 'update', ...names, '-g', '-y']
    return { cmd: 'npx', args, label: `skills-cli update: ${entry.source}` }
  }
  if (entry.kind === 'claude-plugin') {
    return {
      cmd: 'claude',
      args: ['plugin', 'update', entry.source],
      label: `claude-plugin update: ${entry.source}`,
    }
  }
  if (entry.kind === 'claude-marketplace') {
    return {
      cmd: 'claude',
      args: ['plugin', 'marketplace', 'update', entry.source],
      label: `claude-marketplace update: ${entry.source}`,
    }
  }
  if (entry.kind === 'codex-plugin') {
    // Codex 无 plugin update；用 remove + add 刷新到 marketplace 当前版本。
    return {
      cmd: 'codex',
      args: ['plugin', 'add', entry.source],
      label: `codex-plugin update(add): ${entry.source}`,
      prelude: [{
        cmd: 'codex',
        args: ['plugin', 'remove', entry.source],
        label: `codex-plugin update(remove): ${entry.source}`,
      }],
    }
  }
  if (entry.kind === 'codex-marketplace') {
    return {
      cmd: 'codex',
      args: ['plugin', 'marketplace', 'upgrade', entry.source],
      label: `codex-marketplace upgrade: ${entry.source}`,
    }
  }
  throw new Error(`未知 kind: ${entry.kind}`)
}

/** @param {CatalogLike} entry @returns {OfficialCommand} */
export function buildRemoveCommand(entry) {
  if (entry.kind === 'skills-cli') {
    const names = entry.skills?.length ? entry.skills : [entry.id || entry.source]
    return {
      cmd: 'npx',
      args: ['skills', 'remove', ...names, '-g', '-y'],
      label: `skills-cli remove: ${names.join(',')}`,
    }
  }
  if (entry.kind === 'claude-plugin') {
    return {
      cmd: 'claude',
      args: ['plugin', 'uninstall', entry.source],
      label: `claude-plugin remove: ${entry.source}`,
    }
  }
  if (entry.kind === 'claude-marketplace') {
    return {
      cmd: 'claude',
      args: ['plugin', 'marketplace', 'remove', entry.source],
      label: `claude-marketplace remove: ${entry.source}`,
    }
  }
  if (entry.kind === 'codex-plugin') {
    return {
      cmd: 'codex',
      args: ['plugin', 'remove', entry.source],
      label: `codex-plugin remove: ${entry.source}`,
    }
  }
  if (entry.kind === 'codex-marketplace') {
    return {
      cmd: 'codex',
      args: ['plugin', 'marketplace', 'remove', entry.source],
      label: `codex-marketplace remove: ${entry.source}`,
    }
  }
  throw new Error(`未知 kind: ${entry.kind}`)
}

function defaultRunCommand(cmd, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      stdio: 'inherit',
      shell: process.platform === 'win32',
    })
    child.on('error', reject)
    child.on('exit', code => {
      if (code === 0) resolve()
      else reject(new Error(`${cmd} ${args.join(' ')} 退出码 ${code}`))
    })
  })
}

/**
 * 顺序执行命令；单条失败记录后继续。
 *
 * @param {OfficialCommand[]} commands
 * @param {{ runCommand?: (cmd: string, args: string[]) => Promise<void> }} [opts]
 */
/** 展开 prelude（如 Codex update = remove 再 add）。 */
export function expandCommands(commands) {
  const out = []
  for (const item of commands) {
    if (Array.isArray(item.prelude)) out.push(...item.prelude)
    out.push({ cmd: item.cmd, args: item.args, label: item.label })
  }
  return out
}

export async function runCommands(commands, { runCommand = defaultRunCommand } = {}) {
  const ok = []
  const failed = []
  for (const item of expandCommands(commands)) {
    try {
      await runCommand(item.cmd, item.args)
      ok.push(item)
    } catch (error) {
      failed.push({ ...item, error: error?.message || String(error) })
    }
  }
  return { ok, failed }
}

/** 预览用：一行可复制命令（含 prelude）。 */
export function formatCommand(command) {
  const lines = []
  if (Array.isArray(command.prelude)) {
    for (const step of command.prelude) lines.push(`${step.cmd} ${step.args.join(' ')}`)
  }
  lines.push(`${command.cmd} ${command.args.join(' ')}`)
  return lines.join(' && ')
}
