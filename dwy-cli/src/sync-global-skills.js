/**
 * 将已选 skill 额外拷到用户全局目录。
 * 项目目录同步仍由各平台 sync 负责；本模块只处理 ~/.claude / ~/.grok 等 home 下目录。
 * 只覆盖本次点名的 skill，不删除全局目录里其它个人 skill。
 */

import fs from 'fs-extra'
import os from 'node:os'
import path from 'path'
import { copyFilter, logAction } from './sync.js'

/** 项目目录：随所选平台落到 .claude/skills、.agents/skills 等 */
export const SKILL_DEST_PROJECT = 'project'

/** 默认同步位置：只写项目，不碰用户 home */
export const DEFAULT_SKILL_DESTINATIONS = [SKILL_DEST_PROJECT]

/**
 * 全局 dest id → home 下相对路径。
 * 路径跟各工具官方发现目录对齐；测试通过 homeDir 注入，避免写真实 $HOME。
 */
const GLOBAL_SKILL_DIR_SEGMENTS = {
  claude: ['.claude', 'skills'],
  grok: ['.grok', 'skills'],
  agents: ['.agents', 'skills'],
  cursor: ['.cursor', 'skills'],
  opencode: ['.config', 'opencode', 'skills'],
}

export const GLOBAL_SKILL_DEST_IDS = Object.keys(GLOBAL_SKILL_DIR_SEGMENTS)

/**
 * 项目内 skill 目录（按已选平台）。Cursor 无 skills，不列入。
 * 仅 Skills 模式用这张表写项目，避免走完整 sync 误改 rules/commands/hooks。
 */
export const PROJECT_SKILL_DIR_BY_PLATFORM = {
  claude: ['.claude', 'skills'],
  codex: ['.agents', 'skills'],
  opencode: ['.opencode', 'skills'],
}

/**
 * 解析某平台在项目内的 skills 目录。不支持的平台返回 null。
 *
 * @param {string} projectDir
 * @param {string} platform
 */
export function resolveProjectSkillDir(projectDir, platform) {
  const segments = PROJECT_SKILL_DIR_BY_PLATFORM[platform]
  if (!segments) return null
  return path.join(projectDir, ...segments)
}

const DEST_LABELS = {
  project: '项目目录',
  claude: 'Claude Code 全局',
  grok: 'Grok 全局',
  agents: 'Codex / 跨运行时全局',
  cursor: 'Cursor 全局',
  opencode: 'OpenCode 全局',
}

/**
 * 规范化交互/缓存里的 skill 同步范围。
 * 未知 dest、空 skill 名丢弃；无 destinations 时回退到仅项目。
 *
 * @param {{ destinations?: string[], globalSkills?: string[] } | null | undefined} raw
 */
export function normalizeSkillScope(raw) {
  const allowed = new Set([SKILL_DEST_PROJECT, ...GLOBAL_SKILL_DEST_IDS])
  const destinations = (raw?.destinations || [])
    .filter(id => allowed.has(id))
  const globalSkills = [...new Set((raw?.globalSkills || []).filter(name => typeof name === 'string' && name.trim()))]

  return {
    destinations: destinations.length > 0 ? destinations : [...DEFAULT_SKILL_DESTINATIONS],
    globalSkills,
  }
}

/**
 * 解析全局 dest 的绝对目录。project 返回 null（由平台 sync 写项目）。
 *
 * @param {string} destId
 * @param {string} [homeDir]
 */
export function resolveGlobalSkillDir(destId, homeDir = os.homedir()) {
  const segments = GLOBAL_SKILL_DIR_SEGMENTS[destId]
  if (!segments) return null
  return path.join(homeDir, ...segments)
}

/**
 * 最后一步 UI 的位置选项。project 放第一项，默认勾选。
 *
 * @param {string} [homeDir]
 * @returns {Array<{ value: string, label: string, description: string }>}
 */
export function listSkillDestOptions(homeDir = os.homedir()) {
  return [
    {
      value: SKILL_DEST_PROJECT,
      label: DEST_LABELS.project,
      description: '默认。随上面所选平台写入项目 .claude/skills、.agents/skills 等',
    },
    ...GLOBAL_SKILL_DEST_IDS.map(id => {
      const dir = resolveGlobalSkillDir(id, homeDir)
      return {
        value: id,
        label: DEST_LABELS[id],
        description: dir,
      }
    }),
  ]
}

/**
 * 把 skill 目录拷到已选全局 dest。destIds 含 project 时跳过（项目侧已同步）。
 * 只写传入的 skills，不清理目标根目录里其它条目。
 *
 * @param {{ skills: Array<{ name: string, sourcePath: string }>, destIds: string[], homeDir?: string }} opts
 * @returns {Promise<number>} 写入次数（每个 dest × 每个 skill）
 */
export async function copySkillsToGlobalDirs({ skills, destIds, homeDir = os.homedir() }) {
  let count = 0

  for (const destId of destIds) {
    const destRoot = resolveGlobalSkillDir(destId, homeDir)
    if (!destRoot) continue

    for (const skill of skills) {
      const dest = path.join(destRoot, skill.name)
      await fs.ensureDir(path.dirname(dest))
      await fs.copy(skill.sourcePath, dest, { overwrite: true, filter: copyFilter })
      logAction(`${DEST_LABELS[destId] || destId}/${skill.name}`)
      count++
    }
  }

  return count
}

/**
 * 仅 Skills 模式：把 skill 拷到项目内已选平台的 skills 目录。
 * 不写 rules / commands / hooks。
 *
 * @param {{ projectDir: string, platforms: string[], skills: Array<{ name: string, sourcePath: string }> }} opts
 * @returns {Promise<number>}
 */
export async function copySkillsToProjectPlatforms({ projectDir, platforms, skills }) {
  let count = 0

  for (const platform of platforms) {
    const destRoot = resolveProjectSkillDir(projectDir, platform)
    if (!destRoot) continue

    for (const skill of skills) {
      const dest = path.join(destRoot, skill.name)
      await fs.ensureDir(path.dirname(dest))
      await fs.copy(skill.sourcePath, dest, { overwrite: true, filter: copyFilter })
      logAction(`${path.relative(projectDir, destRoot)}/${skill.name}`)
      count++
    }
  }

  return count
}
