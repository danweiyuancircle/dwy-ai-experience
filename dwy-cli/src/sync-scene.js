/**
 * 按包勾选交互：技术栈包 → 场景包 → 确认/微调。
 * 由 dwy / dwy sync 在「按技术栈 / 场景包」模式下调用。
 */

import { isCancel } from '@clack/prompts'
import { SEARCH_PLACEHOLDER, searchableMultiselect, searchableSelect } from './searchable-select.js'
import { SCENE_PACKS, STACK_PACKS, expandPackSelection, normalizePacks } from './sync-packs.js'
import { promptSelection } from './sync.js'
import { chalk } from './utils.js'

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
 * 打印包展开条数。确认步默认用这些预选项，微调再加减。
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
 * 按包选择条目。
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
  /** 微调后的展开结果；返回改包时丢弃，重新 expand。 */
  let selected = null

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
      selected = null

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
      selected = null
      step = 'confirm'
      continue
    }

    selected = selected || expandPackSelection(scans, { stacks, scenes, skillsOnly })
    printPackSummary(stacks, scenes, selected)

    const confirmOptions = [
      { label: '确认提交（用上面勾好的）', value: 'confirm' },
      { label: '微调 Skills（可加减）', value: 'skills' },
      ...(!skillsOnly ? [
        { label: '微调 Rules（可加减）', value: 'rules' },
        { label: '微调 Hooks（可加减）', value: 'hooks' },
      ] : []),
      { label: '返回改技术栈', value: 'stacks' },
      { label: '返回改场景包', value: 'scenes' },
      { label: '取消同步', value: 'cancel' },
    ]
    const final = await searchableSelect({
      message: '包已帮你勾好。确认提交，或微调加减条目：',
      options: confirmOptions,
      initialValue: 'confirm',
      placeholder: SEARCH_PLACEHOLDER,
    })
    if (isCancel(final) || final === 'cancel') return null
    if (final === 'confirm') {
      return {
        ...selected,
        commands: [],
        packs: { stacks, scenes },
      }
    }
    if (final === 'stacks' || final === 'scenes') {
      step = final
      selected = null
      continue
    }

    // 完整清单 + 包内项预勾：可减包内项，也可加包外项
    const catalog = scans[final] || []
    const tuned = await promptSelection(
      catalog,
      final === 'skills' ? 'Skills' : final === 'rules' ? 'Rules' : 'Hooks',
      new Set(selected[final].map(item => item.name)),
    )
    if (tuned === null) return null
    selected = { ...selected, [final]: tuned }
  }
}
