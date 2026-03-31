import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import { renderTemplate, chalk, PACKAGE_ROOT } from './utils.js'

export async function createProject(name) {
  console.log(chalk.blue('Creating a new project...\n'))

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'projectName',
      message: '项目名称:',
      default: name || 'my-app',
      validate: (v) => /^[a-z0-9-]+$/.test(v) || '只允许小写字母、数字和连字符',
    },
    {
      type: 'input',
      name: 'projectDescription',
      message: '项目描述:',
      default: '',
    },
    {
      type: 'list',
      name: 'template',
      message: '选择项目模板:',
      choices: [
        { name: 'web     — Vue + FastAPI', value: 'web' },
        { name: 'mobile  — 移动端 + FastAPI (预留)', value: 'mobile', disabled: '即将推出' },
        { name: 'backend — 纯 FastAPI 服务 (预留)', value: 'backend', disabled: '即将推出' },
      ],
    },
    {
      type: 'confirm',
      name: 'includeDolphindb',
      message: '需要 DolphinDB 吗?',
      default: false,
    },
    {
      type: 'input',
      name: 'sshAlias',
      message: 'SSH 部署别名:',
      default: (a) => `${a.projectName}-server`,
    },
    {
      type: 'input',
      name: 'devDbPort',
      message: '本地开发 DB 端口:',
      default: '5432',
    },
    {
      type: 'input',
      name: 'devRedisPort',
      message: '本地开发 Redis 端口:',
      default: '6379',
    },
    {
      type: 'input',
      name: 'backendPort',
      message: '生产 Backend 端口:',
      default: '8001',
    },
  ])

  const context = {
    ...answers,
    dbName: answers.projectName.replace(/-/g, '_'),
    dbUser: answers.projectName.replace(/-/g, '_'),
    year: new Date().getFullYear(),
    createdAt: new Date().toISOString().split('T')[0],
    dwyVersion: '0.1.0',
  }

  const templateDir = path.join(PACKAGE_ROOT, 'templates', 'project', context.template)
  const destDir = path.resolve(process.cwd(), context.projectName)

  if (await fs.pathExists(destDir)) {
    console.error(chalk.red(`Error: directory "${context.projectName}" already exists.`))
    process.exit(1)
  }

  console.log(chalk.gray(`\nGenerating project in ${destDir}...`))
  await fs.ensureDir(destDir)
  await renderTemplate(templateDir, destDir, context)

  console.log(chalk.green(`\n✅ 项目 ${context.projectName} 创建成功!\n`))
  console.log(chalk.gray('Next steps:'))
  console.log(chalk.gray(`  cd ${context.projectName}`))
  console.log(chalk.gray('  git init && git add . && git commit -m "init"'))
  console.log(chalk.gray('  docker compose -f docker-compose.dev.yml up -d'))
  console.log(chalk.gray('  cd backend && uv venv && uv pip install -e ".[dev]"'))
  console.log(chalk.gray('  cd frontend && pnpm install && pnpm dev'))
}
