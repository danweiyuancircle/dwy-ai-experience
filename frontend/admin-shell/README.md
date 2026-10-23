# @dwydev/admin-kit

Vue 3 **管理框架与通用组合组件**：模块装配菜单与路由，统一壳布局、页头、面包屑、列表状态和管理页面展示。不读取产品 API、store 或领域模型。

视觉底座用 [`@dwydev/eui`](https://www.npmjs.com/package/@dwydev/eui) 的 `EAdminLayout`，**不并入 eui**（eui 只提供 UI 原语）。

## 安装

```bash
pnpm add @dwydev/admin-kit
# peers
pnpm add vue vue-router @dwydev/eui @dwydev/ekit lucide-vue-next
```

宿主需接入 eui theme（`@dwydev/eui/theme`）与 Tailwind。若 shell 类名未生效，把 content 扫到：

```txt
./node_modules/@dwydev/admin-kit/dist/**/*.{js,mjs}
```

### Vite 跨仓联调注意（file: / 源码 alias）

若用 `file:` 或 alias 指 monorepo **源码**（而非已发布 dist），宿主 `vite.config` 必须 **dedupe 并钉死 `vue` / `vue-router`** 到应用自身 `node_modules`，否则会出现两份 vue-router，`useRoute()` inject 为 `undefined`，控制台页读 `.meta` 白屏：

```ts
resolve: {
  dedupe: ['vue', 'vue-router'],
  alias: {
    vue: fileURLToPath(new URL('./node_modules/vue', import.meta.url)),
    'vue-router': fileURLToPath(new URL('./node_modules/vue-router', import.meta.url)),
  },
}
```

发 npm 后消费 dist、peer 由宿主安装时通常无此问题。
## 快速接入（壳组件模式，适合营销 + 控制台共存）

```ts
import { createAdminShell, defineAdminModule, asMenuIcon, AdminShell } from '@dwydev/admin-kit'
import { LayoutDashboard } from 'lucide-vue-next'

export const appShell = createAdminShell({
  title: 'My App',
  logo: '/logo.png',
  collapsedStorageKey: 'myapp:admin:sidebar:collapsed',
  routeMetaDefaults: { requiresAuth: true, layout: 'admin' },
  modules: [
    defineAdminModule({
      id: 'dashboard',
      order: 10,
      menu: { key: '/dashboard', label: '概览', icon: asMenuIcon(LayoutDashboard) },
      routes: [{
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('./pages/Dashboard.vue'),
        meta: { title: '概览' },
      }],
    }),
    // 隐藏菜单、仅保留直访路由
    defineAdminModule({
      id: 'hidden-page',
      showInMenu: false,
      routes: [{ path: '/internal', name: 'internal', component: () => import('./pages/Internal.vue'), meta: { title: '内部' } }],
    }),
  ],
})

// router: [...publicRoutes, ...appShell.routes]
// layout:
// <AdminShell v-bind="appShell.shellProps">
//   <template #header-extra>…用户菜单…</template>
// </AdminShell>
```

## 纯后台父子路由

首版以**扁平绝对 path + 宿主渲染 AdminShell** 为主（与 quant-cloud 一致）。  
`path: '/'` + `children` 形态可在后续版本用 `createAdminShellRoute` 增强。

## 导出

| API | 说明 |
|-----|------|
| `createAdminShell` / `defineAdminModule` | 菜单 + 路由装配 |
| `AdminShell` | 布局组件 |
| `AdminPageHero` / `AdminBreadcrumb` / `AdminPageHeader` | 页头与面包屑 |
| `asMenuIcon` / `useAdminActiveKey` / `useAdminBreadcrumb` | 工具 |

## meta 约定

| 字段 | 说明 |
|------|------|
| `title` | 页头标题 |
| `description` | 页头副标题 |
| `menuKey` | 侧栏高亮（嵌套子页） |
| `pageHero` | 默认 true；false 时页面自管页头 |
| `breadcrumb` | 覆盖自动面包屑 |

## 不负责

鉴权守卫、角色模型、业务 header 内容、HTTP / Pinia。

## 0.3 通用管理组件

0.3 保留原根入口，新增以下显式子路径。EUI peer 下限为已修复标签关联与键盘输入操作的 2.7.2。

```ts
import { PagedTable, RecordSearch, RequestFeedback, ConfigFieldControl } from '@dwydev/admin-kit/components'
import { usePagedList } from '@dwydev/admin-kit/composables'
import { STATUS_TONE } from '@dwydev/admin-kit/status/tone'
```

`components` 还提供总览/统计卡、记录详情/代码/省略/日期展示、状态徽章、筛选器、图表容器及确认执行。`OverviewCard` 与 `WindowToggle` 旧名保持兼容；图表容器不引入 Plotly。密码字段和产品领域页面不在本包内。

加载样式并让 Tailwind 扫描实际安装的构建产物：

```css
@import '@dwydev/eui/theme';
@import '@dwydev/admin-kit/style.css';
@source '../node_modules/@dwydev/eui/dist/**/*.js';
@source '../node_modules/@dwydev/admin-kit/dist/**/*.js';
```

扫描路径以宿主 CSS 文件为基准。产品已有相应配置时只调整路径，不重复加载主题。

### 分页状态

`RecordSearch` 的 `label` 提供持久、视觉隐藏的输入标签；省略时沿用 `placeholder`。输入法合成回车不提交。用户手动删空或点击清空按钮时会先更新 `modelValue`，再各发一次 `clear` 与 `search`；`clear` 只用于通知，宿主统一在 `search` 中请求，避免重复加载。外部直接清空 `modelValue` 不触发搜索。

`PagedTable` 在实际横向溢出时显示滑动提示，并使滚动区可键盘聚焦。需要常驻的行操作列直接使用既有列属性 `{ key: 'actions', title: '操作', width: 80, fixed: 'right' }`；仅固定较窄的操作列，避免占满窄屏。列定义及 `#cell-*` 插槽仍原样转交 EUI。

`RecordEllipsis` 仅在文本实际截断时开启全文提示与键盘停靠，完整文本与占位符不增加 Tab 次数。

```ts
const list = usePagedList({
  fetcher: async ({ page, pageSize, keyword }, request) => {
    const result = await hostApi.list({ page, pageSize, keyword })
    if (request.isCurrent()) hostSummary.value = result.summary
    return { items: result.items, total: result.total }
  },
})
```

`hostApi` 与 `hostSummary` 由产品提供。单参数 fetcher 继续兼容；`paged-list` 子路径与 `composables` 导出同一实现。

- `error` 保留原始失败对象；当前失败清空数据但不向调用方抛出，便于页面区分失败和零条记录。
- 每次 `load` 开始清旧错误，旧请求成功/失败/finally 不得覆盖新请求。
- `invalidate()` 停止 loading 并淘汰在途请求，保留数据、错误与筛选，允许之后再次加载。
- `reset()` 另清空数据/错误/关键词，恢复初始每页条数和排序。
- Vue 作用域销毁时自动 invalidate；底层 HTTP 不会被取消。

### 构建与实际制品验收

在仓库根执行：

```sh
pnpm --dir frontend/eui build
pnpm --dir frontend/ekit build
pnpm --dir frontend/admin-shell test
pnpm --dir frontend/admin-shell build
pnpm --dir frontend/admin-shell smoke:pack
```

smoke 将本轮实际 admin-kit/EUI/ekit tgz 安装到干净目录，检查根/子入口、类型、分页生命周期和 Vite 打包后的真实 EUI SSR；不依赖源码 alias 或共享仓库外的私有产物。它验证 Vue/Vite 消费模式，不承诺现有 ekit 可由原生 Node 无打包直接加载。其他固定依赖从官方 npm registry 安装，冷缓存需要网络。

两产品可暂保留 `@dwy/components` 转出口；本地准备脚本将本包 tgz 复制到各自 `.shared-packages`，不把临时绝对路径写进 package/lock。正式 registry 接入在另行发行后切换，制品验收通过不表示已经发布。

## 开发

```bash
cd frontend/admin-shell
pnpm test
pnpm build
```
