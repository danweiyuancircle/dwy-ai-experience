import test from 'node:test'
import assert from 'node:assert/strict'
import { ensureRepoOrigin, DWY_REPO_URL } from '../src/utils.js'

test('ensureRepoOrigin updates legacy origin to GitHub', async () => {
  const calls = []
  const git = {
    async getRemotes(verbose) {
      calls.push(['getRemotes', verbose])
      return [{
        name: 'origin',
        refs: {
          fetch: 'https://gitee.com/snailyuanyuan/dwy-shared.git',
          push: 'https://gitee.com/snailyuanyuan/dwy-shared.git',
        },
      }]
    },
    async remote(args) {
      calls.push(['remote', args])
    },
  }

  await ensureRepoOrigin(git, DWY_REPO_URL)

  assert.deepEqual(calls, [
    ['getRemotes', true],
    ['remote', ['set-url', 'origin', DWY_REPO_URL]],
  ])
})

test('ensureRepoOrigin keeps origin when already on GitHub', async () => {
  const calls = []
  const git = {
    async getRemotes(verbose) {
      calls.push(['getRemotes', verbose])
      return [{
        name: 'origin',
        refs: {
          fetch: DWY_REPO_URL,
          push: DWY_REPO_URL,
        },
      }]
    },
    async remote(args) {
      calls.push(['remote', args])
    },
  }

  await ensureRepoOrigin(git, DWY_REPO_URL)

  assert.deepEqual(calls, [
    ['getRemotes', true],
  ])
})
