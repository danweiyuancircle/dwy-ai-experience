/**
 * 按包勾选交互：技术栈包 → 场景包。
 * 每包一个 Tab，Tab 下列 checkbox；←/→ 切包，Space 勾子项，a 全选本包。
 * 由 dwy / dwy sync 在「按场景和技术栈」模式下调用。
 */

import { isCancel } from '@clack/prompts'
import { tabMultiselect } from './tab-multiselect.js'
import {
  SCENE_PACKS,
  STACK_PACKS,
  listPackItems,
  normalizePacks,
} from './sync-packs.js'
import { chalk } from './utils.js'

/** 子 value 三段分隔：packId / type / name。packId 不含冒号。 */
const PACK_CHILD_RE = /^([^:]+):(skills|rules|hooks):(.+)$/

/**
 * 子条目在 Tab 多选里的稳定 value。
 * 带 packId：同一 skill 可同时出现在 Vue 与 Python，取消一边不能误伤另一边。
 *
 * @param {string} packId
 * @param {'skills' | 'rules' | 'hooks'} type
 * @param {string} name
 */
export function packChildKey(packId, type, name) {
  return `${packId}:${type}:${name}`
}

/**
 * 解析 packChildKey。对不上的丢掉，避免脏 initialValues 撑进结果。
 *
 * @param {unknown} key
 * @returns {{ packId: string, type: 'skills' | 'rules' | 'hooks', name: string } | null}
 */
export function parsePackChildKey(key) {
  const match = String(key).match(PACK_CHILD_RE)
  if (!match) return null
  return { packId: match[1], type: match[2], name: match[3] }
}

/**
 * 每个包一个 Tab。空包跳过，避免 Tab 下面没有可选项。
 *
 * @param {object[]} packs
 * @param {object} scans
 * @param {{ skillsOnly?: boolean, group?: string }} [opts]
 * @returns {Array<{ id: string, label: string, group?: string, options: Array<{ value: string, label: string, type: string, description?: string }> }>}
 */
export function packTabs(packs, scans, { skillsOnly = false, group } = {}) {
  const tabs = []
  for (const pack of packs) {
    const items = listPackItems(pack, scans, { skillsOnly })
    if (items.length === 0) continue
    tabs.push({
      id: pack.id,
      label: pack.label,
      ...(group ? { group } : {}),
      options: items.map(item => ({
        value: packChildKey(pack.id, item.type, item.name),
        label: item.name,
        type: item.type,
        description: item.description || pack.description,
      })),
    })
  }
  return tabs
}

/**
 * 已选包 → 其下全部子 value，给 tabMultiselect initialValues。
 * 打开时该包 Tab 显示为全勾，用户可再取消。
 *
 * @param {object[]} packs
 * @param {object} scans
 * @param {string[]} selectedPackIds
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export function initialChildValues(packs, scans, selectedPackIds, { skillsOnly = false } = {}) {
  const selected = new Set(selectedPackIds)
  const values = []
  for (const pack of packs) {
    if (!selected.has(pack.id)) continue
    for (const item of listPackItems(pack, scans, { skillsOnly })) {
      values.push(packChildKey(pack.id, item.type, item.name))
    }
  }
  return values
}

/**
 * 把勾上的子 value 还原成条目 + 所属包。
 * 只认扫描结果里真实存在的名字，防止 key 伪造。
 *
 * @param {string[]} keys
 * @param {object} scans
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export function itemsFromChildKeys(keys, scans, { skillsOnly = false } = {}) {
  const parsed = keys.map(parsePackChildKey).filter(Boolean)
  const packIds = [...new Set(parsed.map(item => item.packId))]
  const names = { skills: new Set(), rules: new Set(), hooks: new Set() }
  for (const item of parsed) names[item.type].add(item.name)
  const pick = (type) => (scans[type] || []).filter(item => names[type].has(item.name))
  if (skillsOnly) {
    return { packIds, skills: pick('skills'), rules: [], commands: [], hooks: [] }
  }
  return {
    packIds,
    skills: pick('skills'),
    rules: pick('rules'),
    commands: [],
    hooks: pick('hooks'),
  }
}

/**
 * 打印本次按包勾选的包名与条数。
 *
 * @param {string[]} stacks
 * @param {string[]} scenes
 * @param {{ skills: object[], rules: object[], hooks: object[] }} selected
 */
function printPackSummary(stacks, scenes, selected) {
  const stackLabels = STACK_PACKS.filter(pack => stacks.includes(pack.id)).map(pack => pack.label)
  const sceneLabels = SCENE_PACKS.filter(pack => scenes.includes(pack.id)).map(pack => pack.label)
  const packText = [...stackLabels, ...sceneLabels].join(' + ') || '（未选包）'
  console.log(chalk.gray('\n包展开：'))
  console.log(chalk.gray(`  ${packText}`))
  console.log(chalk.gray(`  Skills ${selected.skills.length}  Rules ${selected.rules.length}  Hooks ${selected.hooks.length}`))
}

/**
 * 按包选择条目。技术栈 Tab 在左、场景 Tab 在右，同一屏勾选。
 * 返回 { skills, rules, commands, hooks, packs } 或 null（取消）。
 *
 * @param {object} scans
 * @param {{ packs?: { stacks?: string[], scenes?: string[] } }} syncState
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export async function interactiveSelectByPacks(scans, syncState, { skillsOnly = false } = {}) {
  const previous = normalizePacks(syncState?.packs)
  const packOpts = { skillsOnly }
  const defaultStacks = previous.stacks.length > 0 ? previous.stacks : ['common']
  const tabs = [
    ...packTabs(STACK_PACKS, scans, { ...packOpts, group: 'stack' }),
    ...packTabs(SCENE_PACKS, scans, { ...packOpts, group: 'scene' }),
  ]
  const keys = await tabMultiselect({
    message: '选择技术栈和场景包',
    tabs,
    initialValues: [
      ...initialChildValues(STACK_PACKS, scans, defaultStacks, packOpts),
      ...initialChildValues(SCENE_PACKS, scans, previous.scenes, packOpts),
    ],
    required: true,
    maxItems: 12,
  })
  if (isCancel(keys)) return null

  const stacks = STACK_PACKS.map(pack => pack.id).filter(id =>
    keys.some(key => parsePackChildKey(key)?.packId === id),
  )
  const scenes = SCENE_PACKS.map(pack => pack.id).filter(id =>
    keys.some(key => parsePackChildKey(key)?.packId === id),
  )
  const selected = itemsFromChildKeys(keys, scans, packOpts)
  printPackSummary(stacks, scenes, selected)
  return {
    skills: selected.skills,
    rules: selected.rules,
    commands: selected.commands,
    hooks: selected.hooks,
    packs: { stacks, scenes },
  }
}
