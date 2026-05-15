import fs from 'fs-extra'
import path from 'path'
import Handlebars from 'handlebars'
import { simpleGit } from 'simple-git'
import chalk from 'chalk'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export const PACKAGE_ROOT = path.resolve(__dirname, '..')
export const CACHE_DIR = path.join(process.env.HOME, '.dwy', 'cache')
export const DWY_REPO_URL = 'https://gitee.com/snailyuanyuan/dwy-shared.git'

export async function ensureRepoCache() {
  await fs.ensureDir(CACHE_DIR)
  const repoDir = path.join(CACHE_DIR, 'dwy')

  if (await fs.pathExists(path.join(repoDir, '.git'))) {
    console.log(chalk.gray('Pulling latest templates...'))
    const git = simpleGit(repoDir)
    await git.pull()
  } else {
    console.log(chalk.gray('Cloning template repo...'))
    await simpleGit().clone(DWY_REPO_URL, repoDir)
  }

  return repoDir
}

export async function renderTemplate(templateDir, destDir, context) {
  const entries = await fs.readdir(templateDir, { withFileTypes: true })

  for (const entry of entries) {
    const srcPath = path.join(templateDir, entry.name)
    let destName = entry.name

    if (destName.includes('{{')) {
      destName = Handlebars.compile(destName)(context)
    }

    if (destName.startsWith('_')) {
      destName = '.' + destName.slice(1)
    }

    if (entry.isDirectory()) {
      const destPath = path.join(destDir, destName)
      await fs.ensureDir(destPath)
      await renderTemplate(srcPath, destPath, context)
      continue
    }

    if (destName.endsWith('.hbs')) {
      destName = destName.slice(0, -4)
      const template = await fs.readFile(srcPath, 'utf-8')
      const rendered = Handlebars.compile(template)(context)
      await fs.writeFile(path.join(destDir, destName), rendered)
    } else if (destName === '.gitkeep') {
      continue
    } else {
      await fs.copy(srcPath, path.join(destDir, destName))
    }
  }
}

export async function copyDir(src, dest) {
  await fs.copy(src, dest, { overwrite: true })
}

export { chalk }
