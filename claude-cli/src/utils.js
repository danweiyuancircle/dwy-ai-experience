import fs from 'fs-extra'
import path from 'path'
import Handlebars from 'handlebars'
import chalk from 'chalk'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export const PACKAGE_ROOT = path.resolve(__dirname, '..')

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
