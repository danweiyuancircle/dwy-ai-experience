import test from 'node:test'
import assert from 'node:assert/strict'
import {
  PACKAGE_NAME,
  buildUpgradeCommand,
  compareVersions,
  detectInstaller,
  selfUpgrade,
} from '../src/self-upgrade.js'

test('detectInstaller 先认 pnpm/yarn/bun 全局路径，再认 npm node_modules', () => {
  assert.equal(detectInstaller('/Users/a/Library/pnpm/global/5/node_modules/create-dwy'), 'pnpm')
  assert.equal(detectInstaller('/Users/a/.local/share/pnpm/global/5/node_modules/create-dwy'), 'pnpm')
  assert.equal(detectInstaller('/Users/a/.yarn/global/node_modules/create-dwy'), 'yarn')
  assert.equal(detectInstaller('/Users/a/.bun/install/global/node_modules/create-dwy'), 'bun')
  assert.equal(detectInstaller('/Users/a/.nvm/versions/node/v22.0.0/lib/node_modules/create-dwy'), 'npm')
  assert.equal(detectInstaller('/Users/a/WebstormProjects/dwy-shared/dwy-cli'), 'unknown')
})

test('buildUpgradeCommand 只装 npm latest 正式版', () => {
  assert.deepEqual(buildUpgradeCommand('npm'), ['npm', ['install', '-g', `${PACKAGE_NAME}@latest`]])
  assert.deepEqual(buildUpgradeCommand('pnpm'), ['pnpm', ['add', '-g', `${PACKAGE_NAME}@latest`]])
  assert.equal(buildUpgradeCommand('unknown'), null)
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
  })
  assert.equal(result.status, 'up-to-date')
  assert.equal(calls.length, 0)
})

test('selfUpgrade 落后则按安装器升级到 latest', async () => {
  const calls = []
  const result = await selfUpgrade({
    currentVersion: '1.0.0',
    pkgRoot: '/usr/local/lib/node_modules/create-dwy',
    fetchLatest: async () => '1.2.3',
    runCommand: async (cmd, args) => { calls.push([cmd, args]) },
  })
  assert.equal(result.status, 'upgraded')
  assert.deepEqual(calls, [['npm', ['install', '-g', 'create-dwy@latest']]])
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
