import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import { renderTemplate, chalk, PACKAGE_ROOT } from './utils.js'

export async function createProject(name) {
  console.log(chalk.blue('Creating a new project...\n'))

  // Step 1: common questions
  const common = await inquirer.prompt([
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
        { name: 'web      — Vue 3 前端 (pnpm monorepo, eui + ekit + Tailwind)', value: 'web' },
        { name: 'backend  — FastAPI 后端 (eapi + PostgreSQL + Redis + Docker)', value: 'backend' },
        { name: 'mobile   — 移动端 (暂未实现)', value: 'mobile', disabled: '即将推出' },
      ],
    },
  ])

  // Step 2: template-specific questions
  let extra = {}

  if (common.template === 'backend') {
    extra = await inquirer.prompt([
      {
        type: 'input',
        name: 'sshAlias',
        message: 'SSH 部署别名:',
        default: `${common.projectName}-server`,
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
  }

  if (common.template === 'web') {
    extra = await inquirer.prompt([
      {
        type: 'input',
        name: 'apiProxy',
        message: 'API 代理地址 (后端):',
        default: 'http://127.0.0.1:8000',
      },
    ])
  }

  const answers = { ...common, ...extra }

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

  if (context.template === 'backend') {
    console.log(chalk.gray('  docker compose -f docker-compose.dev.yml up -d'))
    console.log(chalk.gray('  uv venv && uv pip install -e ".[dev]"'))
    console.log(chalk.gray('  uvicorn app.main:app --reload'))
  }

  if (context.template === 'web') {
    console.log(chalk.gray('  pnpm install'))
    console.log(chalk.gray('  pnpm dev'))
  }
}
