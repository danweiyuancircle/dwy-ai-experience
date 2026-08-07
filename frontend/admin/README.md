# @dwydev/admin-kit

Vue 3 **通用后台管理系统骨架**。

- **内置 chrome**：主题切换、通知下拉、用户下拉、面包屑 / 页头、侧栏折叠
- **扩展方式**：`defineAdminModule` 注册子菜单与路由
- **底座**：`@dwydev/eui` 的 `EAdminLayout`

> 与 `@dwydev/admin-shell` 并存。本包是完整骨架方案；`admin-shell` 保持原样不改。

## 安装

```bash
pnpm add @dwydev/admin-kit
# peers
pnpm add vue vue-router @dwydev/eui @dwydev/ekit lucide-vue-next
```

## 快速开始

```ts
import {
  createAdminShell,
  defineAdminModule,
  asMenuIcon,
  AdminShell,
} from '@dwydev/admin-kit'
import { LayoutDashboard, Users } from 'lucide-vue-next'

export const appShell = createAdminShell({
  title: 'My Admin',
  logo: '/logo.png',
  logoTo: '/dashboard',
  features: {
    theme: true,
    notifications: true,
    userMenu: true,
  },
  routeMetaDefaults: { requiresAuth: true },
  modules: [
    defineAdminModule({
      id: 'dashboard',
      order: 10,
      menu: { key: '/dashboard', label: '概览', icon: asMenuIcon(LayoutDashboard) },
      routes: [{
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('./pages/Dashboard.vue'),
        meta: { title: '数据概览' },
      }],
    }),
    defineAdminModule({
      id: 'ops',
      order: 20,
      menu: {
        key: 'group-ops',
        label: '运营',
        icon: asMenuIcon(Users),
        children: [
          { key: '/ops/users', label: '用户列表' },
          { key: '/ops/plans', label: '套餐' },
        ],
      },
      routes: [
        {
          path: '/ops/users',
          component: () => import('./pages/Users.vue'),
          meta: { title: '用户列表', menuKey: '/ops/users' },
        },
      ],
    }),
  ],
})

// router: [...appShell.routes]
// layout:
// <AdminShell
//   v-bind="appShell.shellProps"
//   :user="{ name: '张三', email: 'a@b.com' }"
//   :notifications="list"
//   @logout="auth.logout()"
// />
```

### 关掉骨架 chrome（兼容「只要布局」）

```ts
features: { theme: false, notifications: false, userMenu: false }
// 再用 #header-extra 自己塞业务顶栏
```

## 不负责

鉴权守卫、角色模型、HTTP / Pinia、业务页面内容。

## 开发

```bash
cd frontend/admin
pnpm test
pnpm build
```

Playground 全屏预览：`/admin`（docs 门户顶部导航「Admin 骨架」）。
