# @dwydev/admin-shell

Vue 3 **管理系统扩展站路由框架**：模块注册侧栏菜单与路由，统一壳布局 / 页头 / 面包屑。

视觉底座用 [`@dwydev/eui`](https://www.npmjs.com/package/@dwydev/eui) 的 `EAdminLayout`，**不并入 eui**（eui 只提供 UI 原语）。

## 安装

```bash
pnpm add @dwydev/admin-shell
# peers
pnpm add vue vue-router @dwydev/eui @dwydev/ekit lucide-vue-next
```

宿主需接入 eui theme（`@dwydev/eui/theme`）与 Tailwind。若 shell 类名未生效，把 content 扫到：

```txt
./node_modules/@dwydev/admin-shell/dist/**/*.{js,mjs}
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
import { createAdminShell, defineAdminModule, asMenuIcon, AdminShell } from '@dwydev/admin-shell'
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

## 开发

```bash
cd frontend/admin-shell
pnpm test
pnpm build
```
