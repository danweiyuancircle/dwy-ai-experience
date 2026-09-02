/**
 * 按包勾选交互：技术栈包 → 场景包 → 展示已预勾的子条目（可取消）。
 * 由 dwy / dwy sync 在「按场景和技术栈」模式下调用。
 */

import { isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import { SCENE_PACKS, STACK_PACKS, expandPackSelection, normalizePacks } from './sync-packs.js'
import { chalk } from './utils.js'

const TYPE_LABELS = {
  skills: 'Skills',
  rules: 'Rules',
  hooks: 'Hooks',
}

/**
 * 把包目录转成可搜索选项。
 *
 * @param {Array<{ id: string, label: string, description: string }>} packs
 */
function packOptions(packs) {
  return packs.map(pack => ({
    value: pack.id,
    label: pack.label,
    description: pack.description,
  }))
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
 * 把包展开结果打成一条可搜索列表。label 含类型 + 分类 + 名字。
 *
 * @param {{ skills: object[], rules: object[], hooks: object[] }} selected
 */
export function buildPackItemOptions(selected) {
  const rows = []
  for (const type of ['skills', 'rules', 'hooks']) {
    for (const item of selected[type] || []) {
      rows.push({
        value: packItemKey(type, item.name),
        label: `${TYPE_LABELS[type]} / ${item.category || '其他'} / ${item.name}`,
        description: item.description,
      })
    }
  }
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
 * 按包选择条目。栈/场景选完后展示聚合子条目，默认全勾，用户可取消。
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

  while (true) {
    if (step === 'stacks') {
      const result = await searchableMultiselect({
        message: '选择技术栈（通用默认勾选）',
        options: packOptions(STACK_PACKS),
        initialValues: stacks,
        required: true,
        maxItems: 12,
        placeholder: SEARCH_PLACEHOLDER,
      })
      if (isCancel(result)) return null
      stacks = result

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
        message: '选择场景包（可全不选）',
        options: packOptions(SCENE_PACKS),
        initialValues: scenes,
        required: false,
        maxItems: 10,
        placeholder: SEARCH_PLACEHOLDER,
      })
      if (isCancel(result)) return null
      scenes = result
      step = 'items'
      continue
    }

    const expanded = expandPackSelection(scans, { stacks, scenes, skillsOnly })
    printPackSummary(stacks, scenes, expanded)
    const options = buildPackItemOptions(expanded)
    if (options.length === 0) {
      return { skills: [], rules: [], commands: [], hooks: [], packs: { stacks, scenes } }
    }

    const keys = await searchableMultiselect({
      message: '包已预勾子条目，取消不需要的即可',
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
