import fs from 'fs-extra'
import os from 'node:os'
import path from 'node:path'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { randomUUID } from 'node:crypto'
import { spinner } from '@clack/prompts'
import { PACKAGE_ROOT } from './utils.js'

const execFileAsync = promisify(execFile)
const REMOTE = 'https://github.com/danweiyuancircle/dwy-ai-experience.git'
const TEMPLATE_PATH = ['dwy-cli', 'templates', 'ai-tools']
const REVISION_FILE = '.dwy-source-revision'

async function statEntry(file) {
  return fs.lstat(file).catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
}

async function requireDirectory(directory) {
  const stat = await fs.lstat(directory)
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error(`模板目录不能是软链接或文件：${directory}`)
}

async function validateTemplates(directory) {
  await requireDirectory(directory)
  await validateTree(directory)
  for (const name of ['skills', 'rules', 'hooks']) await requireDirectory(path.join(directory, name))
  const baseline = path.join(directory, 'AGENTS.md')
  if (!(await fs.lstat(baseline)).isFile() || !(await fs.readFile(baseline, 'utf8')).trim()) {
    throw new Error('模板缺少有效 AGENTS.md')
  }
}

async function validateTree(directory) {
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    if (entry.isSymbolicLink()) throw new Error(`模板不能包含软链接：${entry.name}`)
    if (entry.isDirectory()) await validateTree(path.join(directory, entry.name))
  }
}

async function deadLockExists(lockPath) {
  const stat = await statEntry(lockPath)
  if (!stat) return false
  if (!stat.isFile()) throw new Error(`模板锁无效，保留原文件：${lockPath}`)
  const owner = await fs.readFile(lockPath, 'utf8').catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (owner === null) return false
  const pid = Number(owner.trim())
  if (!/^[1-9]\d*\s*$/.test(owner) || !Number.isSafeInteger(pid) || pid > 2147483647) {
    throw new Error(`模板锁无效，保留原文件：${lockPath}`)
  }
  try {
    process.kill(pid, 0)
  } catch (error) {
    if (error.code === 'ESRCH') return true
    if (error.code !== 'EPERM') throw error
  }
  throw new Error(`进程 ${pid} 正在更新模板，保留现有锁。`)
}

async function acquireLock(lockPath, candidate) {
  while (true) {
    try {
      await fs.link(candidate, lockPath)
      return
    } catch (error) {
      if (error.code !== 'EEXIST') throw error
    }
    if (!await deadLockExists(lockPath)) continue
    // 回收也须互斥，避免两个进程删掉对方的新锁；回收中断时按同一协议恢复。
    const recovery = `${lockPath}.recovery`
    await acquireLock(recovery, candidate)
    try {
      if (await deadLockExists(lockPath)) await fs.unlink(lockPath)
      try {
        await fs.link(candidate, lockPath)
        return
      } catch (error) {
        if (error.code !== 'EEXIST') throw error
      }
    } finally {
      await fs.unlink(recovery)
    }
  }
}

async function git(args, cwd) {
  try {
    const { stdout } = await execFileAsync('git', ['-c', 'core.hooksPath=/dev/null', ...args], {
      cwd,
      // 不加载用户安装的 hooks 或过滤器，避免检出远端内容时执行脚本。
      env: { ...process.env, GIT_TERMINAL_PROMPT: '0', GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null' },
      // 首次检出要获取整套模板，不能沿用轻量版本检查的短超时。
      timeout: ['clone', 'checkout', 'fetch', 'reset'].includes(args[0]) ? 300000 : 15000,
      maxBuffer: 1024 * 1024,
    })
    return stdout.trim()
  } catch (error) {
    throw new Error(`Git 获取模板失败（${error.code || error.signal}）`)
  }
}

async function refreshTemplates(root, cache) {
  await fs.ensureDir(root)
  await requireDirectory(root)
  const lockPath = path.join(root, 'template-source.lock')
  const candidate = path.join(root, `.template-source-lock-${randomUUID()}`)
  await fs.writeFile(candidate, `${process.pid}\n`, { flag: 'wx' })
  try {
    await acquireLock(lockPath, candidate)
  } finally {
    await fs.unlink(candidate)
  }
  let staging
  const previous = path.join(root, '.template-source.previous')
  try {
    if (await statEntry(cache)) await requireDirectory(cache)
    if (await statEntry(previous)) {
      await validateTemplates(previous)
      if (await statEntry(cache)) {
        await validateTemplates(cache)
        await fs.remove(previous)
      } else {
        await fs.rename(previous, cache)
      }
    }
    const revision = (await git(['ls-remote', '--exit-code', REMOTE, 'refs/heads/master'], root)).split(/\s/)[0]
    if (!/^[a-f\d]{40,64}$/.test(revision)) throw new Error('远端 master 版本无效')
    if (await statEntry(cache)) {
      try {
        await validateTemplates(cache)
        if ((await fs.readFile(path.join(cache, REVISION_FILE), 'utf8')).trim() === revision) return
      } catch {
        // 本地缓存不完整时重新获取，不能只凭版本标记跳过内容校验。
      }
    }
    staging = await fs.mkdtemp(path.join(root, '.template-source-'))
    const storedRepository = path.join(root, 'template-repository')
    const reuse = !!await statEntry(storedRepository)
    const repository = reuse ? storedRepository : path.join(staging, 'repository')
    if (reuse) {
      await requireDirectory(repository)
      await requireDirectory(path.join(repository, '.git'))
      await git(['fetch', '--depth=1', '--filter=blob:none', REMOTE, 'master'], repository)
      await git(['reset', '--hard', 'FETCH_HEAD'], repository)
    } else {
      await git(['clone', '--depth=1', '--filter=blob:none', '--no-checkout', '--single-branch',
        '--branch', 'master', REMOTE, repository], staging)
      await git(['sparse-checkout', 'set', '--cone', TEMPLATE_PATH.join('/')], repository)
      await git(['checkout', '--force', 'master'], repository)
    }
    let candidate = repository
    for (const segment of TEMPLATE_PATH) {
      candidate = path.join(candidate, segment)
      await requireDirectory(candidate)
    }
    await validateTemplates(candidate)
    const next = path.join(staging, 'templates')
    await fs.copy(candidate, next)
    await fs.writeFile(path.join(next, REVISION_FILE), await git(['rev-parse', 'HEAD'], repository))
    if (!reuse) await fs.rename(repository, storedRepository)
    const hadCache = !!await statEntry(cache)
    if (hadCache) await fs.rename(cache, previous)
    try {
      await fs.rename(next, cache)
    } catch (error) {
      if (hadCache) await fs.rename(previous, cache)
      throw error
    }
    if (hadCache) await fs.remove(previous)
  } finally {
    try {
      if (staging) await fs.remove(staging)
    } finally {
      await fs.unlink(lockPath)
    }
  }
}

/**
 * 从固定公开仓库更新用户模板缓存；只读取已验证的目录，不执行模板脚本。
 * 显式目录优先；DWY_HOME 优先于注入 homeDir，更新失败保留缓存，无有效缓存才用随包模板。
 */
export async function resolveTemplateSource({ homeDir = os.homedir() } = {}) {
  const explicitSourceDir = process.env.DWY_TEMPLATE_SOURCE_DIR
  if (explicitSourceDir) {
    if (!await fs.pathExists(explicitSourceDir)) {
      throw new Error(`DWY_TEMPLATE_SOURCE_DIR not found: ${explicitSourceDir}`)
    }
    return explicitSourceDir
  }
  const root = process.env.DWY_HOME || path.join(homeDir, '.dwy')
  const cache = path.join(root, 'template-source')
  const progress = process.stdout.isTTY ? spinner() : null
  progress?.start('正在检查 AI 模板更新，首次获取可能较慢')
  try {
    await refreshTemplates(root, cache)
    progress?.stop('AI 模板已就绪')
    return cache
  } catch (error) {
    progress?.stop('模板更新未完成，正在检查本地来源')
    try {
      await validateTemplates(cache)
    } catch {
      const bundled = path.join(PACKAGE_ROOT, 'templates', 'ai-tools')
      await validateTemplates(bundled)
      console.warn(`模板更新失败（${error.message}）；无有效缓存，回退随包模板。`)
      return bundled
    }
    console.warn(`模板更新失败（${error.message}）；继续使用本地缓存。`)
    return cache
  }
}
