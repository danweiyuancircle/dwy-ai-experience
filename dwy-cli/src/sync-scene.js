/**
 * 按包勾选交互：技术栈包 → 场景包（包下挂子条目）→ 预勾子条目可取消。
 * 由 dwy / dwy sync 在「按场景和技术栈」模式下调用。
 */

import { isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import {
  SCENE_PACKS,
  STACK_PACKS,
  expandPackSelection,
  listPackItems,
  normalizePacks,
  packLabelForItem,
} from './sync-packs.js'
import { chalk } from './utils.js'

/**
 * 包名 + 其下子条目。子条目 disabled，只展示不参与勾选；勾的是整包。
 *
 * @param {object[]} packs
 * @param {object} scans
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export function packOptionsWithChildren(packs, scans, { skillsOnly = false } = {}) {
  const rows = []
  for (const pack of packs) {
    const items = listPackItems(pack, scans, { skillsOnly })
    const names = items.map(item => item.name)
    rows.push({
      value: pack.id,
      label: `${pack.label}（${items.length}）`,
      description: names.length > 0 ? names.join('、') : pack.description,
    })
    for (const item of items) {
      rows.push({
        value: `hint:${pack.id}:${item.type}:${item.name}`,
        label: `  ${item.name}`,
        description: item.description || pack.label,
        disabled: true,
      })
    }
  }
  return rows
}

/**
 * 子条目在多选里的稳定 key。类型前缀避免 skill/rule 重名撞车。
 *
 * @param {'skills' | 'rules' | 'hooks'} type
 * @param {string} name
 */
export function packItemKey(type, name) {
  return `${type}:${name}`
}

/**
 * 把包展开结果打成一条可搜索列表，按包名分组，便于对照取消。
 *
 * @param {{ skills: object[], rules: object[], hooks: object[] }} selected
 * @param {string[]} packIds
 */
export function buildPackItemOptions(selected, packIds = []) {
  const rows = []
  for (const type of ['skills', 'rules', 'hooks']) {
    for (const item of selected[type] || []) {
      const packLabel = packLabelForItem(item, type, packIds)
      rows.push({
        value: packItemKey(type, item.name),
        label: `${packLabel} / ${item.name}`,
        description: item.description,
      })
    }
  }
  rows.sort((a, b) => a.label.localeCompare(b.label, 'zh'))
  return rows
}

/**
 * 按用户勾选的 key 从展开结果里筛子条目。未勾的丢掉。
 *
 * @param {{ skills: object[], rules: object[], hooks: object[] }} expanded
 * @param {string[]} keys
 */
export function splitPackItemKeys(expanded, keys) {
  const set = new Set(keys)
  return {
    skills: expanded.skills.filter(item => set.has(packItemKey('skills', item.name))),
    rules: expanded.rules.filter(item => set.has(packItemKey('rules', item.name))),
    hooks: expanded.hooks.filter(item => set.has(packItemKey('hooks', item.name))),
    commands: [],
  }
}

/**
 * 打印包展开条数，随后立刻列出预勾子条目。
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
 * 按包选择条目。选包时列出包下子条目；确认后默认全勾，用户可取消。
 * 返回 { skills, rules, commands, hooks, packs } 或 null（取消）。
 *
 * @param {object} scans
 * @param {{ packs?: { stacks?: string[], scenes?: string[] } }} syncState
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export async function interactiveSelectByPacks(scans, syncState, { skillsOnly = false } = {}) {
  const previous = normalizePacks(syncState?.packs)
  let stacks = previous.stacks.length > 0 ? previous.stacks : ['common']
  let scenes = previous.scenes
  let step = 'stacks'
  const packOpts = { skillsOnly }

  while (true) {
    if (step === 'stacks') {
      const result = await searchableMultiselect({
        message: '选择技术栈（通用默认勾选；包下列出子条目，下一步可逐条取消）',
        options: packOptionsWithChildren(STACK_PACKS, scans, packOpts),
        initialValues: stacks,
        required: true,
        maxItems: 15,
        placeholder: SEARCH_PLACEHOLDER,
        descLines: 8,
      })
      if (isCancel(result)) return null
      stacks = result.filter(id => !String(id).startsWith('hint:'))

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

    if (step === 'scenes') {
      const result = await searchableMultiselect({
        message: '选择场景包（可全不选；包下列出子条目，下一步可逐条取消）',
        options: packOptionsWithChildren(SCENE_PACKS, scans, packOpts),
        initialValues: scenes,
        required: false,
        maxItems: 15,
        placeholder: SEARCH_PLACEHOLDER,
        descLines: 8,
      })
      if (isCancel(result)) return null
      scenes = result.filter(id => !String(id).startsWith('hint:'))
      step = 'items'
      continue
    }

    const expanded = expandPackSelection(scans, { stacks, scenes, skillsOnly })
    printPackSummary(stacks, scenes, expanded)
    const packIds = [...stacks, ...scenes]
    const options = buildPackItemOptions(expanded, packIds)
    if (options.length === 0) {
      return { skills: [], rules: [], commands: [], hooks: [], packs: { stacks, scenes } }
    }

    const keys = await searchableMultiselect({
      message: '已按包预勾子条目，取消不需要的即可',
      options,
      initialValues: options.map(option => option.value),
      required: false,
      maxItems: 15,
      placeholder: SEARCH_PLACEHOLDER,
    })
    if (isCancel(keys)) return null
    return {
      ...splitPackItemKeys(expanded, keys),
      packs: { stacks, scenes },
    }
  }
}
