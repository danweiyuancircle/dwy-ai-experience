import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import {
  PACKAGE_NAME,
  buildUpgradeCommand,
  compareVersions,
  detectInstaller,
  fetchLatestVersion,
  selfUpgrade,
} from '../src/self-upgrade.js'

function registryEnvironment(t, value) {
  const previous = process.env.npm_config_registry
  if (value === undefined) delete process.env.npm_config_registry
  else process.env.npm_config_registry = value
  t.after(() => {
    if (previous === undefined) delete process.env.npm_config_registry
    else process.env.npm_config_registry = previous
  })
}

test('detectInstaller 先认 pnpm/yarn/bun 全局路径，再认 npm node_modules', () => {
  assert.equal(detectInstaller('/Users/a/Library/pnpm/global/5/node_modules/create-dwy'), 'pnpm')
  assert.equal(detectInstaller('/Users/a/.local/share/pnpm/global/5/node_modules/create-dwy'), 'pnpm')
  assert.equal(detectInstaller('/Users/a/.yarn/global/node_modules/create-dwy'), 'yarn')
  assert.equal(detectInstaller('/Users/a/.bun/install/global/node_modules/create-dwy'), 'bun')
  assert.equal(detectInstaller('/Users/a/.nvm/versions/node/v22.0.0/lib/node_modules/create-dwy'), 'npm')
  assert.equal(detectInstaller('/Users/a/WebstormProjects/dwy-shared/dwy-cli'), 'unknown')
})

test('升级命令固定查询所得版本，显式使用同一 registry，覆盖滞后镜像配置', t => {
  registryEnvironment(t, undefined)
  const spec = `${PACKAGE_NAME}@1.2.3`, registry = '--registry=https://registry.npmjs.org/'
  assert.deepEqual(buildUpgradeCommand('npm', '1.2.3'), ['npm', ['install', '-g', spec, registry]])
  assert.deepEqual(buildUpgradeCommand('pnpm', '1.2.3'), ['pnpm', ['add', '-g', spec, registry]])
  assert.deepEqual(buildUpgradeCommand('yarn', '1.2.3'), ['yarn', ['global', 'add', spec, registry]])
  assert.deepEqual(buildUpgradeCommand('bun', '1.2.3'), ['bun', ['add', '-g', spec, registry]])
  assert.equal(buildUpgradeCommand('unknown', '1.2.3'), null)
})

test('显式 registry 环境覆盖同时用于查询和精确版本安装', async t => {
  registryEnvironment(t, 'https://registry.example.invalid/')
  let requested
  const latest = await fetchLatestVersion(async url => {
    requested = url
    return { ok: true, json: async () => ({ version: '1.2.3' }) }
  })
  assert.equal(requested, 'https://registry.example.invalid/create-dwy/latest')
  assert.deepEqual(buildUpgradeCommand('npm', latest), ['npm', ['install', '-g', 'create-dwy@1.2.3', '--registry=https://registry.example.invalid/']])
})

test('registry 版本响应必须是正式版本，不能把外部任意字符串传入安装命令', async () => {
  for (const version of ['1.2.3;echo injected', '1.2.3-beta.1', '', null]) {
    await assert.rejects(fetchLatestVersion(async () => ({ ok: true, json: async () => ({ version }) })), /version/)
  }
})

test('registry 内嵌凭据在请求前被拒绝，错误不暴露原地址', async t => {
  registryEnvironment(t, 'https://USER:PASSWORD@registry.example.invalid/')
  let requested = false
  await assert.rejects(fetchLatestVersion(async url => { requested = true; return fetch(url) }), error => {
    assert.match(error.message, /不支持 URL 内嵌凭据/)
    return !/USER|PASSWORD/.test(error.message)
  })
  assert.equal(requested, false)
  assert.throws(() => buildUpgradeCommand('npm', '1.2.3'), /不支持 URL 内嵌凭据/)
})

test('registry 外部地址必须是 HTTP(S) 基地址', async t => {
  registryEnvironment(t, undefined)
  for (const value of ['not-a-url', 'file:///tmp/registry', 'https://registry.example.invalid/?token=PLACEHOLDER']) {
    process.env.npm_config_registry = value
    await assert.rejects(fetchLatestVersion(), /npm_config_registry/)
  }
})

test('Windows registry 拒绝命令解释器元字符', t => {
  registryEnvironment(t, undefined)
  const descriptor = Object.getOwnPropertyDescriptor(process, 'platform')
  Object.defineProperty(process, 'platform', { value: 'win32' })
  t.after(() => Object.defineProperty(process, 'platform', descriptor))
  assert.equal(buildUpgradeCommand('npm', '1.2.3')[0], 'npm')
  for (const character of ['&', '|', '<', '>', '^', '%', '!', '"', '(', ')', '\r', '\n', '团队', 'with space']) {
    process.env.npm_config_registry = `https://registry.example.invalid/${character}`
    assert.throws(() => buildUpgradeCommand('npm', '1.2.3'), /Windows 命令解释器/)
  }
})

test('compareVersions 比较三段版本号', () => {
  assert.equal(compareVersions('0.18.0', '0.18.0'), 0)
  assert.equal(compareVersions('0.17.1', '0.18.0'), -1)
  assert.equal(compareVersions('0.18.0', '0.17.1'), 1)
})

test('selfUpgrade 已是最新则不执行安装', async () => {
  const calls = []
  const result = await selfUpgrade({
    currentVersion: '1.2.3',
    pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
    readInstalledVersion: async () => '1.2.3',
  })
  assert.equal(result.status, 'up-to-date')
  assert.deepEqual(calls, [['dwy', ['refresh']]])
})

test('selfUpgrade 安装精确版本，回读实际入口成功后才刷新', async t => {
  registryEnvironment(t, undefined)
  const calls = []
  const result = await selfUpgrade({
    currentVersion: '1.0.0',
    pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
    readInstalledVersion: async () => { calls.push(['read-version']); return '1.2.3' },
  })
  assert.equal(result.status, 'upgraded')
  assert.deepEqual(calls, [['npm', ['install', '-g', 'create-dwy@1.2.3', '--registry=https://registry.npmjs.org/']], ['read-version'], ['dwy', ['refresh']]])
})

test('安装命令成功但实际入口仍为旧版时，不能刷新或显示升级成功', async t => {
  const calls = [], logs = []
  t.mock.method(console, 'log', value => logs.push(value))
  await assert.rejects(selfUpgrade({
    currentVersion: '1.0.0', pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
    readInstalledVersion: async () => '1.0.0',
  }), /升级未生效.*1\.2\.3.*1\.0\.0/)
  assert.equal(calls.length, 1)
  assert.equal(logs.some(value => /已升级到/.test(value)), false)
})

test('默认版本探针实际执行 PATH 中的 dwy，版本一致才刷新', { skip: process.platform === 'win32' }, async t => {
  const bin = mkdtempSync(path.join(os.tmpdir(), 'dwy-upgrade-probe-'))
  const previousPath = process.env.PATH
  process.env.PATH = `${bin}${path.delimiter}${previousPath}`
  t.after(() => {
    process.env.PATH = previousPath
    rmSync(bin, { recursive: true, force: true })
  })
  const calls = []
  const opts = {
    currentVersion: '1.2.3', pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
  }
  writeFileSync(path.join(bin, 'dwy'), '#!/bin/sh\nprintf "1.0.0\\n"\n', { mode: 0o755 })
  await assert.rejects(selfUpgrade(opts), /升级未生效/)
  assert.deepEqual(calls, [])
  writeFileSync(path.join(bin, 'dwy'), '#!/bin/sh\nprintf "1.2.3\\n"\n')
  assert.equal((await selfUpgrade(opts)).status, 'up-to-date')
  assert.deepEqual(calls, [['dwy', ['refresh']]])
})

test('selfUpgrade 刷新失败不能报告完整升级成功', async () => {
  await assert.rejects(selfUpgrade({
    currentVersion: '1.0.0',
    pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async cmd => { if (cmd === 'dwy') throw new Error('refresh failed') },
    readInstalledVersion: async () => '1.2.3',
  }), /刷新失败/)
})

test('selfUpgrade 当前新于 npm 不降级', async () => {
  const calls = []
  const result = await selfUpgrade({
    currentVersion: '2.0.0',
    pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.0.0',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
  })
  assert.equal(result.status, 'newer-local')
  assert.equal(calls.length, 0)
})

test('selfUpgrade 源码目录拒绝自升级', async () => {
  await assert.rejects(
    () => selfUpgrade({
      currentVersion: '1.0.0',
      pkgRoot: '/Users/a/WebstormProjects/dwy-shared/dwy-cli',
      fetchLatest: async () => '1.2.3',
      runCommand: async () => {},
    }),
    /不是全局安装/,
  )
})
