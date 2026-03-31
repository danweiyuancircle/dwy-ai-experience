# dwy-shared 文档门户设计

## 概述

将 `frontend/playground` 从纯 EUI 组件展示改造为 dwy-shared monorepo 文档门户，面向团队成员，覆盖 5 个模块。站点 UI 全部使用 `@danweiyuan/eui` 组件构建。

## 导航架构

顶部 Tab 切换 5 个顶级模块，左侧栏显示当前模块的子页面列表。

```
┌──────────────────────────────────────────────────────────────┐
│ DWY Shared  [EUI 组件] [Core] [Backend] [CLI] [Claude Code]  🔍 🌙 │
├───────────┬──────────────────────────────────────────────────┤
│ 侧边栏     │ 内容区                                           │
│ (按模块变化) │                                                 │
└───────────┴──────────────────────────────────────────────────┘
```

- 顶部栏：站点标题 + 模块 Tab + 搜索按钮 (Ctrl/Cmd+K) + 暗色模式切换 + 主题色选择
- 侧边栏：当前模块的分类 + 子页面列表，使用 EMenu 组件
- 内容区：路由视图

## 模块与页面

### EUI 组件 (38 页)

保持现有 37 个 demo 页不变，新增概览首页。路由前缀从 `/button` 改为 `/eui/button`。

侧边栏分类：基础 / 表单 / 数据展示 / 导航 / 反馈 / 其他

### Core 工具 (6 页)

- 概览首页
- request — Axios 插件化封装
- storage — localStorage 响应式封装
- validators — 校验函数集
- date — 日期格式化
- hooks — Vue Composables (useDebounce/useClickOutside/useEventListener)

### Backend (9 页)

- 概览首页
- config — Pydantic Settings
- database — 异步 SQLAlchemy
- security — JWT + bcrypt
- exceptions — 异常体系
- response — 统一响应
- pagination — 分页工具
- cache — 异步 Redis
- dependencies — FastAPI 依赖注入

### CLI (2 页)

- 概览首页
- create-dwy — `dwy create` 和 `dwy sync` 命令说明

### Claude Code (12 页)

- 概览首页
- **Skills** (3 页): dwy-frontend-eui / dwy-frontend-core / dwy-backend-base
- **Rules** (5 页): server-security / git-security / python-code-style / vue-code-style / backend-security
- **Hooks** (1 页): pre-git-commit-sensitive-check
- **Settings** (1 页): settings.json 配置说明

## 数据源策略

| 内容类型 | 方式 |
|---------|------|
| EUI 组件 demo | 手写 Vue 交互示例（现有代码不变） |
| Core / Backend 文档 | 构建时 `import.meta.glob` 读取对应 SKILL.md，运行时 markdown-it 渲染 |
| Claude Code (skills/rules/hooks) | 构建时 glob 读取 `claude-cli/templates/claude-global/` 下 .md 文件渲染 |
| CLI 说明 | 手写 Vue 页面 |

## 全局搜索

- **触发**: 顶部搜索按钮 + `Ctrl+K` / `Cmd+K` 快捷键
- **UI**: ECommand 命令面板组件，弹出式搜索对话框
- **搜索范围**: 所有模块的页面标题 + Markdown 内容文本
- **索引**: 构建时生成搜索索引（标题、模块分类、内容摘要），运行时纯前端 Fuse.js 模糊匹配
- **结果**: 按模块分组展示，点击跳转对应页面

## UI 组件使用

整站使用 @danweiyuan/eui 组件构建：

| 场景 | 使用组件 |
|------|---------|
| 顶部模块 Tab | EButton 组 + router-link 样式切换 |
| 侧边栏导航 | EMenu (items + collapsed) |
| 搜索弹窗 | ECommand 命令面板 |
| 文档容器 | ECard |
| 代码展示/折叠 | ECollapsible + 主题色代码高亮 |
| 暗色切换 | useTheme() composable |
| 主题色选择 | 色块按钮组（现有实现） |
| 提示信息 | ETooltip / EBadge |
| 空状态 | EEmpty |

## 技术实现

### 新增依赖

- `markdown-it` — Markdown 渲染
- `fuse.js` — 模糊搜索

### 路由结构

```
/                     → 站点首页（总览仪表盘）
/eui                  → EUI 概览
/eui/button           → Button demo
/eui/input            → Input demo
...（现有 37 个 demo 页加 /eui 前缀）

/core                 → Core 概览
/core/request         → request 模块文档
/core/storage         → storage 模块文档
...

/backend              → Backend 概览
/backend/config       → config 模块文档
/backend/database     → database 模块文档
...

/cli                  → CLI 概览
/cli/create-dwy       → create-dwy 命令说明

/claude               → Claude Code 概览
/claude/skills/:name  → Skill 详情
/claude/rules/:name   → Rule 详情
/claude/hooks/:name   → Hook 详情
/claude/settings      → Settings 说明
```

### 关键文件变更

| 文件 | 变更 |
|------|------|
| `src/App.vue` | 重写：顶部 Tab 导航 + 动态侧边栏 + 搜索快捷键 |
| `src/router.ts` | 重写：按模块分组路由，现有 EUI 路由加 /eui 前缀 |
| `src/views/HomeView.vue` | 重写：总览仪表盘，展示各模块统计和快捷入口 |
| `src/views/` 现有 demo 页 | 不改动，仅路由路径变化 |

### 新增文件

| 文件 | 用途 |
|------|------|
| `src/components/DocPage.vue` | 通用文档页壳：接收 Markdown 字符串，markdown-it 渲染，ECard 包裹 |
| `src/components/SearchDialog.vue` | 全局搜索：ECommand 组件 + Fuse.js |
| `src/components/ModuleSidebar.vue` | 侧边栏：根据当前模块渲染 EMenu |
| `src/components/TopNav.vue` | 顶部导航栏：模块 Tab + 搜索 + 主题 |
| `src/data/search-index.ts` | 搜索索引：构建时 glob 读取所有 .md 生成 |
| `src/data/nav-config.ts` | 导航配置：各模块的侧边栏菜单数据 |
| `src/views/core/*.vue` | Core 模块 6 个页面 |
| `src/views/backend/*.vue` | Backend 模块 9 个页面 |
| `src/views/cli/*.vue` | CLI 模块 2 个页面 |
| `src/views/claude/*.vue` | Claude Code 模块 12 个页面 |

## 不做的事

- 不做 SSR/SSG，保持纯 SPA
- 不写后端模块的交互示例（Python 代码前端无法运行）
- 不对现有 EUI demo 页面内容做修改
