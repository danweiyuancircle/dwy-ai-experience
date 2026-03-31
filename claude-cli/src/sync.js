import fs from 'fs-extra'
import path from 'path'
import { ensureRepoCache, copyDir, chalk } from './utils.js'

export async function syncClaude() {
  console.log(chalk.blue('Syncing global Claude configuration...'))

  const repoDir = await ensureRepoCache()
  const sourceDir = path.join(repoDir, 'claude-cli', 'templates', 'claude-global')
  const targetDir = path.join(process.env.HOME, '.claude')

  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red('Error: claude-global templates not found in repo'))
    process.exit(1)
  }

  const subdirs = ['rules', 'skills', 'commands', 'hooks']
  let syncedCount = 0

  for (const subdir of subdirs) {
    const src = path.join(sourceDir, subdir)
    if (await fs.pathExists(src)) {
      const dest = path.join(targetDir, subdir)
      await copyDir(src, dest)
      const files = await fs.readdir(src).catch(() => [])
      syncedCount += files.length
      console.log(chalk.green(`  ✓ ${subdir}/ — ${files.length} files`))
    }
  }

  // Sync CLAUDE.md
  const claudeMdSrc = path.join(sourceDir, 'CLAUDE.md')
  if (await fs.pathExists(claudeMdSrc)) {
    await fs.copy(claudeMdSrc, path.join(targetDir, 'CLAUDE.md'))
    syncedCount++
    console.log(chalk.green('  ✓ CLAUDE.md'))
  }

  const settingsSrc = path.join(sourceDir, 'settings.json')
  if (await fs.pathExists(settingsSrc)) {
    const settingsDest = path.join(targetDir, 'settings.json')
    const newSettings = await fs.readJson(settingsSrc)

    if (await fs.pathExists(settingsDest)) {
      const existing = await fs.readJson(settingsDest)
      const merged = { ...existing, ...newSettings }
      await fs.writeJson(settingsDest, merged, { spaces: 2 })
      console.log(chalk.green('  ✓ settings.json — merged'))
    } else {
      await fs.writeJson(settingsDest, newSettings, { spaces: 2 })
      console.log(chalk.green('  ✓ settings.json — created'))
    }
    syncedCount++
  }

  console.log(chalk.blue(`\nDone! Synced ${syncedCount} items to ~/.claude/`))
}

export async function syncProjectClaude() {
  console.log(chalk.blue('Syncing project Claude configuration...'))

  const dwyFile = path.join(process.cwd(), '.dwy')
  if (!await fs.pathExists(dwyFile)) {
    console.error(chalk.red('Error: .dwy marker file not found. Is this a dwy project?'))
    console.error(chalk.gray('Run "dwy create" to create a new project, or create .dwy manually.'))
    process.exit(1)
  }

  const marker = await fs.readJson(dwyFile)
  const template = marker.template || 'web'

  const repoDir = await ensureRepoCache()
  const sourceDir = path.join(repoDir, 'claude-cli', 'templates', 'project', template, '.claude')
  const targetDir = path.join(process.cwd(), '.claude')

  if (!await fs.pathExists(sourceDir)) {
    console.error(chalk.red(`Error: template "${template}" not found in repo`))
    process.exit(1)
  }

  await copyDir(sourceDir, targetDir)
  console.log(chalk.blue('Done! Synced .claude/ for current project.'))
}
