import fs from 'fs-extra'
import path from 'path'
import os from 'node:os'
import { createHash } from 'node:crypto'
import { getDwyHomeDir, runGit, chalk } from './utils.js'

function logAction(label) {
  console.log(chalk.green(`  ✓ ${label}`))
}

// 产品 0→1 流程依赖的外部 skill 清单。
// 每项：缓存目录名（= 原子 skill 引用的 ~/.dwy/skills/<name>）→ 来源 repo / stable tag / repo 内目录。
// 只用正式 release tag，不用 main HEAD（定版可复现）。更新版本时改这里的 tag。
const SKILL_SOURCES = {
  'pm-skills': {
    repo: 'https://github.com/phuryn/pm-skills.git',
    tag: 'v2.0.0',
    licenseFile: 'LICENSE',
    licenseDest: 'LICENSE-pm-skills',
    skills: {
      'competitor-analysis': 'pm-market-research/skills/competitor-analysis',
      'market-sizing': 'pm-market-research/skills/market-sizing',
      'sentiment-analysis': 'pm-market-research/skills/sentiment-analysis',
      'interview-script': 'pm-product-discovery/skills/interview-script',
      'prioritize-features': 'pm-product-discovery/skills/prioritize-features',
      'opportunity-solution-tree': 'pm-product-discovery/skills/opportunity-solution-tree',
      'metrics-dashboard': 'pm-product-discovery/skills/metrics-dashboard',
      'create-prd': 'pm-execution/skills/create-prd',
      'outcome-roadmap': 'pm-execution/skills/outcome-roadmap',
      'test-scenarios': 'pm-execution/skills/test-scenarios',
      'release-notes': 'pm-execution/skills/release-notes',
      'gtm-strategy': 'pm-go-to-market/skills/gtm-strategy',
      // 商业分析（dwy-commercial 依赖）：商业模式 / 变现 / 定价 / 创业画布 / 赛道五力
      'business-model': 'pm-product-strategy/skills/business-model',
      'monetization-strategy': 'pm-product-strategy/skills/monetization-strategy',
      'pricing-strategy': 'pm-product-strategy/skills/pricing-strategy',
      'startup-canvas': 'pm-product-strategy/skills/startup-canvas',
      'porters-five-forces': 'pm-product-strategy/skills/porters-five-forces',
      'intended-vs-implemented': 'pm-ai-shipping/skills/intended-vs-implemented',
      'north-star-metric': 'pm-marketing-growth/skills/north-star-metric',
    },
  },
  superpowers: {
    repo: 'https://github.com/obra/superpowers.git',
    tag: 'v6.0.3',
    licenseFile: 'LICENSE',
    licenseDest: 'LICENSE-superpowers',
    skills: {
      brainstorming: 'skills/brainstorming',
      'writing-plans': 'skills/writing-plans',
      'test-driven-development': 'skills/test-driven-development',
      'systematic-debugging': 'skills/systematic-debugging',
    },
  },
}

// 计算 SKILL_SOURCES 清单的内容指纹，用于检测「cli 加了 skill / 改了 tag」→ 需重装。
// SKILL_SOURCES 是源码内固定字面量，JSON.stringify 稳定（插入顺序固定）。
// 取 sha256 前 12 位，足以区分任意清单变更，无碰撞风险。
function computeManifestHash() {
  return createHash('sha256').update(JSON.stringify(SKILL_SOURCES)).digest('hex').slice(0, 12)
}

// 全局外部 skill 安装目录：~/.dwy/skills/
function getGlobalSkillsDir() {
  return path.join(getDwyHomeDir(), 'skills')
}

// 浅克隆指定 tag 到临时目录（--depth 1 + --branch <tag> 只取定版，省带宽）。
async function shallowCloneTag(repoUrl, tag, destDir) {
  await runGit(['clone', '--depth', '1', '--branch', tag, repoUrl, destDir])
}

// 安装/更新全部外部 skill 到 ~/.dwy/skills/。再次运行即覆盖式更新。
export async function installSkills() {
  const targetDir = getGlobalSkillsDir()
  await fs.ensureDir(targetDir)

  const tmpRoot = path.join(os.tmpdir(), `dwy-skills-${process.pid}`)
  await fs.ensureDir(tmpRoot)

  const versions = {}
  try {
    for (const [sourceName, src] of Object.entries(SKILL_SOURCES)) {
      console.log(chalk.gray(`拉取 ${sourceName} @ ${src.tag} ...`))
      const repoDir = path.join(tmpRoot, sourceName)
      await shallowCloneTag(src.repo, src.tag, repoDir)

      // 搬 LICENSE（MIT 要求保留原版权声明）
      const licenseSrc = path.join(repoDir, src.licenseFile)
      if (await fs.pathExists(licenseSrc)) {
        await fs.copy(licenseSrc, path.join(targetDir, src.licenseDest), { overwrite: true })
      }

      // 搬每个 skill 整目录（含 scripts/、配套 .md）
      for (const [skillName, repoPath] of Object.entries(src.skills)) {
        const from = path.join(repoDir, repoPath)
        const to = path.join(targetDir, skillName)
        if (!await fs.pathExists(from)) {
          throw new Error(`${sourceName} @ ${src.tag} 内未找到 ${repoPath}（仓库结构可能变了）`)
        }
        await fs.remove(to)
        await fs.copy(from, to, { overwrite: true })
        logAction(`skills/${skillName}`)
        versions[skillName] = { repo: src.repo, tag: src.tag }
      }
    }

    // 写版本清单 + 清单指纹，供查看与后续更新比对。
    // manifest_hash 变化（cli 加了 skill / 改了 tag）→ 下次 ensureSkillsInstalled 触发重装。
    await fs.writeJson(
      path.join(targetDir, 'VERSIONS.json'),
      { manifest_hash: computeManifestHash(), versions },
      { spaces: 2 },
    )
    console.log(chalk.green(`\n✓ 外部 skill 已安装到 ${targetDir}`))
  } finally {
    await fs.remove(tmpRoot)
  }
}

// 全局 skill 是否已就绪（VERSIONS.json 存在）。
export async function skillsInstalled() {
  return fs.pathExists(path.join(getGlobalSkillsDir(), 'VERSIONS.json'))
}

// 确保 ~/.dwy/skills/ 与 cli 当前 SKILL_SOURCES 清单一致：未装 / 清单变更 → 自动重装。
// hash 一致 → 零开销跳过；失败 → warn 一行不阻塞主流程（离线/网络故障不挡 sync）。
// 返回 true = 本次执行了安装，false = 跳过。
export async function ensureSkillsInstalled() {
  const versionsFile = path.join(getGlobalSkillsDir(), 'VERSIONS.json')
  // 已装：读 manifest_hash 比对，一致即跳过，不联网
  if (await fs.pathExists(versionsFile)) {
    let stored
    try {
      stored = await fs.readJson(versionsFile)
    } catch {
      stored = {}
    }
    // 兼容老格式（无 manifest_hash）→ 视为不一致，触发一次重装补上指纹
    if (stored.manifest_hash === computeManifestHash()) return false
    console.log(chalk.gray('全局外部 skill 清单已更新，重新拉取...'))
  } else {
    console.log(chalk.gray('未检测到全局外部 skill，自动安装...'))
  }
  try {
    await installSkills()
    return true
  } catch (error) {
    // 离线/网络故障：不阻塞主流程，下次再来
    console.log(chalk.yellow(`外部 skill 自动更新失败：${error.message}`))
    return false
  }
}
