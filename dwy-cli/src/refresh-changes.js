import fs from 'fs-extra'
import path from 'node:path'
import { createHash } from 'node:crypto'
import { chalk } from './utils.js'

async function fingerprint(dest) {
  const stat = await fs.lstat(dest).catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (!stat) return null
  // 入口链接只比较指向；共享内容单独报告，避免重复读取和跟随外部链接。
  if (stat.isSymbolicLink()) return `link:${await fs.readlink(dest)}`
  const hash = createHash('sha256')
  if (stat.isDirectory()) {
    for (const name of (await fs.readdir(dest)).sort()) {
      hash.update(JSON.stringify([name, await fingerprint(path.join(dest, name))]))
    }
    return `directory:${hash.digest('hex')}`
  }
  if (!stat.isFile()) throw new Error(`无法比较非普通文件：${dest}`)
  hash.update(await fs.readFile(dest))
  return `file:${stat.mode & 0o111}:${hash.digest('hex')}`
}

/** 只读记录刷新计划中的目标；目录比较全部内容，忽略修改时间，不遍历软链接。 */
export async function snapshotRefreshPaths(paths) {
  const result = new Map()
  for (const dest of new Set(paths)) result.set(dest, await fingerprint(dest))
  return result
}

/** 按实际前后快照输出变更路径；不输出配置正文或将未变内容计入变更。 */
export function reportRefreshChanges(label, before, after) {
  const changes = []
  for (const [dest, signature] of after) {
    if (before.get(dest) === signature) continue
    changes.push({ dest, action: before.get(dest) === null ? '新增' : signature === null ? '移除' : '更新' })
  }
  if (!changes.length) {
    console.log(chalk.gray(`${label}：无变更（检查 ${after.size} 项）。`))
    return
  }
  const counts = ['新增', '更新', '移除'].map(action => `${action} ${changes.filter(item => item.action === action).length} 项`)
  console.log(chalk.green(`${label}：${counts.join('，')}。`))
  for (const { dest, action } of changes) console.log(`  ${action} ${dest}`)
}
