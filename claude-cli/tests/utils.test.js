import test from 'node:test'
import assert from 'node:assert/strict'
import { needsRepoReclone, DWY_REPO_URL } from '../src/utils.js'

test('needsRepoReclone returns false when origin matches target repo', async () => {
  const git = {
    async getRemotes(verbose) {
      assert.equal(verbose, true)
      return [{
        name: 'origin',
        refs: {
          fetch: DWY_REPO_URL,
          push: DWY_REPO_URL,
        },
      }]
    },
  }

  assert.equal(await needsRepoReclone(git, DWY_REPO_URL), false)
})

test('needsRepoReclone returns true when origin fetch points to another repo', async () => {
  const git = {
    async getRemotes(verbose) {
      assert.equal(verbose, true)
      return [{
        name: 'origin',
        refs: {
          fetch: 'https://gitee.com/snailyuanyuan/dwy-shared.git',
          push: 'https://gitee.com/snailyuanyuan/dwy-shared.git',
        },
      }]
    },
  }

  assert.equal(await needsRepoReclone(git, DWY_REPO_URL), true)
})

test('needsRepoReclone returns true when origin push differs from fetch', async () => {
  const git = {
    async getRemotes(verbose) {
      assert.equal(verbose, true)
      return [{
        name: 'origin',
        refs: {
          fetch: DWY_REPO_URL,
          push: 'https://gitee.com/snailyuanyuan/dwy-ai-experience.git',
        },
      }]
    },
  }

  assert.equal(await needsRepoReclone(git, DWY_REPO_URL), true)
})
