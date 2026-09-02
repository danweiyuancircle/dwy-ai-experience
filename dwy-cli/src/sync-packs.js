/**
 * 按包勾选的包目录：技术栈包 + 场景包。
 * 展开结果写入现有 skills/rules/hooks 选择，不改平台 sync 的按名增删。
 * 条目按扫描结果的 category / name 匹配，模板里不存在的名字直接跳过。
 */

/** 技术栈包（含通用）。Tab 顺序：通用第一，Android、Vue 随后，其余保持原相对顺序。 */
export const STACK_PACKS = [
  {
    id: 'common',
    label: '通用',
    description: '开发流程 rules、Git hooks、跨栈 skill（dwy-shared / semver / 流程文档）',
    ruleCategories: ['开发流程'],
    hookCategories: ['Git'],
    skillCategories: ['通用'],
    skillNames: ['dwy-semver'],
  },
  {
    id: 'android',
    label: 'Android',
    description: 'Android rules',
    ruleCategories: ['Android'],
  },
  {
    id: 'vue',
    label: 'Vue',
    description: 'Vue rules + dwy-eui / dwy-ekit / 全栈脚手架',
    ruleCategories: ['Vue'],
    skillCategories: ['Vue'],
  },
  {
    id: 'python',
    label: 'Python',
    description: 'Python rules + dwy-eapi / 全栈脚手架',
    ruleCategories: ['Python'],
    skillCategories: ['Python'],
    skillNames: ['dwy-fullstack-scaffold'],
  },
  {
    id: 'ios',
    label: 'iOS',
    description: 'iOS / Swift rules。上架 skill 在场景包「发布发版」',
    ruleCategories: ['iOS'],
  },
  {
    id: 'flutter',
    label: 'Flutter',
    description: 'Flutter rules',
    ruleCategories: ['Flutter'],
  },
  {
    id: 'harmony',
    label: 'HarmonyOS',
    description: 'HarmonyOS / ArkTS rules',
    ruleCategories: ['HarmonyOS'],
  },
  {
    id: 'docker',
    label: 'Docker / 运维',
    description: 'Docker rule + 镜像/部署 skill',
    ruleCategories: ['Docker'],
    skillCategories: ['Docker'],
  },
  {
    id: 'database',
    label: '数据库',
    description: 'Postgres / Redis / 迁移 rules。DolphinDB skill 在场景包',
    ruleCategories: ['数据库'],
  },
]

/** 场景包。和栈包同一屏 Tab，默认不预勾。 */
export const SCENE_PACKS = [
  {
    id: 'product-0to1',
    label: '产品0到1',
    description: '立项到上线的阶段 skill（launcher / PRD / 架构 / TDD…）',
    skillCategories: ['产品0到1'],
  },
  {
    id: 'media',
    label: '自媒体',
    description: '单位圆自媒体流水线 + 豆包配音',
    skillCategories: ['自媒体'],
  },
  {
    id: 'release',
    label: '发布发版',
    description: 'dwy-publish / App Store / SDK 检查 / semver / GitHub Action',
    skillCategories: ['发布发版'],
  },
  {
    id: 'security',
    label: '安全',
    description: '部署巡检与白帽渗透',
    skillCategories: ['安全'],
  },
  {
    id: 'article',
    label: '内容创作',
    description: '技术文章写作 skill',
    skillCategories: ['内容创作'],
  },
  {
    id: 'dolphindb',
    label: 'DolphinDB',
    description: 'DolphinDB 开发与审查 skill（体量大，不跟数据库栈绑定）',
    skillCategories: ['DolphinDB'],
  },
]

const STACK_IDS = new Set(STACK_PACKS.map(pack => pack.id))
const SCENE_IDS = new Set(SCENE_PACKS.map(pack => pack.id))

/**
 * 规范化 sync-state 里的 packs。未知 id 丢弃，避免旧状态撑爆交互默认勾选。
 *
 * @param {{ stacks?: string[], scenes?: string[] } | null | undefined} raw
 */
export function normalizePacks(raw) {
  return {
    stacks: [...new Set((raw?.stacks || []).filter(id => STACK_IDS.has(id)))],
    scenes: [...new Set((raw?.scenes || []).filter(id => SCENE_IDS.has(id)))],
  }
}

/**
 * 判断扫描项是否属于某个包。
 * 约束：只看本类型对应的 category / 显式名字，避免 skill 目录名误伤 rules。
 *
 * @param {{ name: string, category?: string }} item
 * @param {object} pack
 * @param {'skills' | 'rules' | 'hooks'} type
 */
export function itemInPack(item, pack, type) {
  if (type === 'skills') {
    if ((pack.skillNames || []).includes(item.name)) return true
    return (pack.skillCategories || []).includes(item.category)
  }
  if (type === 'rules') return (pack.ruleCategories || []).includes(item.category)
  return (pack.hookCategories || []).includes(item.category)
}

/**
 * 按名字去重合并，保持扫描原序。
 *
 * @param {Array<{ name: string }>} items
 */
function uniqueByName(items) {
  const seen = new Set()
  const result = []
  for (const item of items) {
    if (seen.has(item.name)) continue
    seen.add(item.name)
    result.push(item)
  }
  return result
}

/**
 * 把已选栈 + 场景包展开成 sync 用的条目。
 * skillsOnly 时 rules/hooks 必须空数组，调用方不得据此删除项目已有项。
 *
 * @param {{ skills: object[], rules: object[], commands?: object[], hooks: object[] }} scans
 * @param {{ stacks?: string[], scenes?: string[], skillsOnly?: boolean }} selection
 */
/**
 * 列出某包在当前扫描结果里的子条目，带 type，供界面展示「包下面有哪些」。
 *
 * @param {object} pack
 * @param {{ skills?: object[], rules?: object[], hooks?: object[] }} scans
 * @param {{ skillsOnly?: boolean }} [opts]
 */
export function listPackItems(pack, scans, { skillsOnly = false } = {}) {
  const types = skillsOnly ? ['skills'] : ['skills', 'rules', 'hooks']
  const items = []
  for (const type of types) {
    for (const item of scans[type] || []) {
      if (itemInPack(item, pack, type)) items.push({ ...item, type })
    }
  }
  return items
}

/**
 * 条目属于已选包时，用包的中文名做分组前缀。
 *
 * @param {{ name: string, category?: string }} item
 * @param {'skills' | 'rules' | 'hooks'} type
 * @param {string[]} packIds
 */
export function packLabelForItem(item, type, packIds) {
  const packs = [...STACK_PACKS, ...SCENE_PACKS]
  const hit = packs.find(pack => packIds.includes(pack.id) && itemInPack(item, pack, type))
  return hit?.label || item.category || '其他'
}

export function expandPackSelection(scans, { stacks = [], scenes = [], skillsOnly = false } = {}) {
  const packById = new Map([...STACK_PACKS, ...SCENE_PACKS].map(pack => [pack.id, pack]))
  const selectedPacks = [...stacks, ...scenes]
    .map(id => packById.get(id))
    .filter(Boolean)

  const pick = (type) => uniqueByName(
    selectedPacks.flatMap(pack => (scans[type] || []).filter(item => itemInPack(item, pack, type))),
  )

  if (skillsOnly) {
    return {
      skills: pick('skills'),
      rules: [],
      commands: [],
      hooks: [],
    }
  }

  return {
    skills: pick('skills'),
    rules: pick('rules'),
    commands: [],
    hooks: pick('hooks'),
  }
}
