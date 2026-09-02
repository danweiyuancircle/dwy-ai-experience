/**
 * 按包勾选交互：技术栈包 → 场景包。
 * 用 @clack/prompts groupMultiselect：勾父级=全选子项，子项可单独取消。
 * 由 dwy / dwy sync 在「按场景和技术栈」模式下调用。
 */

import { groupMultiselect, isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableSelect } from './searchable-select.js'
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
 * 子条目在 groupMultiselect 里的稳定 value。
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
 * groupMultiselect 的 options：key 是分组标题（包名），value 是可单独勾的子项。
 * 空包跳过——clack 空组 `every()` 恒 true，会显示成已全选。
 *
 * @param {object[]} packs
 * @param {object} scans
 * @param {{ skillsOnly?: boolean }} [opts]
 * @returns {Record<string, { value: string, label: string, hint?: string }[]>}
 */
export function packGroupOptions(packs, scans, { skillsOnly = false } = {}) {
  const groups = {}
  for (const pack of packs) {
    const items = listPackItems(pack, scans, { skillsOnly })
    if (items.length === 0) continue
    groups[`${pack.label}（${items.length}）`] = items.map(item => ({
      value: packChildKey(pack.id, item.type, item.name),
      label: item.name,
      hint: item.description || undefined,
    }))
  }
  return groups
}

/**
 * 已选包 → 其下全部子 value，给 groupMultiselect initialValues。
 * 父级勾选态由 clack 根据「子是否全在 value 里」推导，不要传包名。
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
 * 按包选择条目。Space 勾父级=该包全部子项；光标在子项上可单独取消。
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
  let stacks = defaultStacks
  let scenes = previous.scenes
  // 返回重选时保留已取消的子项，不要用包 id 重新全勾
  let stackKeys = initialChildValues(STACK_PACKS, scans, defaultStacks, packOpts)
  let sceneKeys = initialChildValues(SCENE_PACKS, scans, scenes, packOpts)
  let step = 'stacks'

  while (true) {
    if (step === 'stacks') {
      const options = packGroupOptions(STACK_PACKS, scans, packOpts)
      const result = await groupMultiselect({
        message: '选择技术栈（Space 勾整包，也可单独取消某个子项）',
        options,
        initialValues: stackKeys,
        required: true,
        maxItems: 15,
        selectableGroups: true,
      })
      if (isCancel(result)) return null
      stackKeys = result
      stacks = STACK_PACKS.map(pack => pack.id).filter(id =>
        stackKeys.some(key => parsePackChildKey(key)?.packId === id),
      )

      const nav = await searchableSelect({
        message: `已选 ${stacks.length} 个技术栈。下一步：`,
        options: [
          { label: '继续选场景包', value: 'next' },
          { label: '返回重选技术栈', value: 'back' },
          { label: '取消同步', value: 'cancel' },
        ],
        initialValue: 'next',
        placeholder: SEARCH_PLACEHOLDER,
      })
      if (isCancel(nav) || nav === 'cancel') return null
      step = nav === 'back' ? 'stacks' : 'scenes'
      continue
    }

    const sceneOptions = packGroupOptions(SCENE_PACKS, scans, packOpts)
    if (Object.keys(sceneOptions).length > 0) {
      const result = await groupMultiselect({
        message: '选择场景包（可全不选；Space 勾整包，也可单独取消某个子项）',
        options: sceneOptions,
        initialValues: sceneKeys,
        required: false,
        maxItems: 15,
        selectableGroups: true,
      })
      if (isCancel(result)) return null
      sceneKeys = result
      scenes = SCENE_PACKS.map(pack => pack.id).filter(id =>
        sceneKeys.some(key => parsePackChildKey(key)?.packId === id),
      )
    } else {
      sceneKeys = []
      scenes = []
    }

    const selected = itemsFromChildKeys([...stackKeys, ...sceneKeys], scans, packOpts)
    printPackSummary(stacks, scenes, selected)
    return {
      skills: selected.skills,
      rules: selected.rules,
      commands: selected.commands,
      hooks: selected.hooks,
      packs: { stacks, scenes },
    }
  }
}
