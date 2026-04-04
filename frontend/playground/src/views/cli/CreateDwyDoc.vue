<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## dwy create [name]

交互式创建新项目。根据用户选择的模板生成完整项目结构。

### 用法

\`\`\`bash
dwy create [name]
\`\`\`

如果不提供 \`name\`，CLI 会交互式地询问项目名称。

### 交互式参数

| 参数 | 说明 | 默认值 | 校验规则 |
|------|------|--------|----------|
| projectName | 项目名称 | \`my-app\`（或传入的 name） | 只允许小写字母、数字和连字符 |
| projectDescription | 项目描述 | 空 | — |
| template | 项目模板 | — | 见下方模板列表 |
| includeDolphindb | 是否引入 DolphinDB | \`false\` | yes/no |
| sshAlias | SSH 部署别名 | \`{projectName}-server\` | — |
| devDbPort | 本地开发 DB 端口 | \`5432\` | — |
| devRedisPort | 本地开发 Redis 端口 | \`6379\` | — |
| backendPort | 生产 Backend 端口 | \`8001\` | — |

### 模板列表

| 模板 | 说明 | 状态 |
|------|------|------|
| \`web\` | Vue + FastAPI 全栈项目 | 可用 |
| \`mobile\` | 移动端 + FastAPI | 即将推出 |
| \`backend\` | 纯 FastAPI 服务 | 即将推出 |

### 生成内容

选择 \`web\` 模板后，脚手架会生成以下结构：

- **frontend/** — Vue 3 前端项目（含 @danweiyuan/eui + @danweiyuan/ekit）
- **backend/** — FastAPI 后端项目（含 danweiyuan-eapi）
- **docker-compose.yml** — 生产部署配置
- **docker-compose.dev.yml** — 本地开发配置（PostgreSQL + Redis）
- **.claude/** — 项目级 Claude Code 配置
- **.dwy** — 项目标记文件（记录模板类型，供 \`dwy sync\` 使用）

### 模板变量

模板文件中支持以下变量替换：

| 变量 | 说明 | 示例 |
|------|------|------|
| \`projectName\` | 项目名称 | \`my-app\` |
| \`projectDescription\` | 项目描述 | \`My awesome project\` |
| \`dbName\` | 数据库名（连字符转下划线） | \`my_app\` |
| \`dbUser\` | 数据库用户名 | \`my_app\` |
| \`sshAlias\` | SSH 别名 | \`my-app-server\` |
| \`devDbPort\` | 开发 DB 端口 | \`5432\` |
| \`devRedisPort\` | 开发 Redis 端口 | \`6379\` |
| \`backendPort\` | 生产后端端口 | \`8001\` |
| \`year\` | 当前年份 | \`2026\` |
| \`createdAt\` | 创建日期 | \`2026-03-31\` |

### 创建后的下一步

\`\`\`bash
cd my-app
git init && git add . && git commit -m "init"
docker compose -f docker-compose.dev.yml up -d
cd backend && uv venv && uv pip install -e ".[dev]"
cd frontend && pnpm install && pnpm dev
\`\`\`

---

## dwy sync claude

同步全局 Claude Code 配置到 \`~/.claude/\` 目录。

### 用法

\`\`\`bash
dwy sync claude
\`\`\`

### 同步内容

从 dwy-shared 仓库的 \`claude-cli/templates/claude-global/\` 目录同步以下内容：

| 目录/文件 | 说明 | 同步方式 |
|-----------|------|----------|
| \`rules/\` | Claude Code 规则文件 | 目录覆盖 |
| \`skills/\` | Claude Code 技能文件 | 目录覆盖 |
| \`commands/\` | Claude Code 自定义命令 | 目录覆盖 |
| \`hooks/\` | Claude Code 钩子脚本 | 目录覆盖 |
| \`settings.json\` | Claude Code 设置 | **合并**（不覆盖已有字段） |

### settings.json 合并策略

\`settings.json\` 使用浅合并（\`{ ...existing, ...newSettings }\`）：

- 模板中的新字段会被添加
- 用户已自定义的字段**不会被覆盖**
- 如果目标文件不存在则直接创建

### 缓存机制

CLI 会自动从远程仓库拉取最新模板并缓存到本地，确保同步的配置始终是最新版本。

---

## dwy sync project-claude

同步项目级 Claude Code 配置到当前项目的 \`.claude/\` 目录。

### 用法

\`\`\`bash
dwy sync project-claude
\`\`\`

### 前置条件

当前目录必须包含 \`.dwy\` 标记文件。该文件在 \`dwy create\` 时自动生成，格式为 JSON：

\`\`\`json
{
  "template": "web"
}
\`\`\`

如果 \`.dwy\` 文件不存在，CLI 会报错并提示使用 \`dwy create\` 创建项目或手动创建 \`.dwy\` 文件。

### 同步内容

根据 \`.dwy\` 中的 \`template\` 字段，从对应模板目录（如 \`templates/project/web/.claude/\`）同步整个 \`.claude/\` 目录到当前项目根目录。

### 典型使用场景

- 团队成员克隆项目后，运行此命令获取项目级 Claude 配置
- 上游模板更新后，运行此命令同步最新配置
`
</script>

<template>
  <DocPage :content="content" title="CLI 命令文档" />
</template>
