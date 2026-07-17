/**
 * @dwydev/admin-shell
 * 管理系统扩展站路由框架：模块装配 + AdminShell 布局（EAdminLayout）+ 页头/面包屑约定。
 * 不并入 eui：本包是应用壳框架，eui 只提供 EAdminLayout 等视觉原语。
 */

export { createAdminShell, collectMenuItems, collectRoutes, normalizeRoutePath, normalizeRoutes } from './create-admin-shell'
export { defineAdminModule } from './define-admin-module'
export { useAdminActiveKey } from './composables/useAdminActiveKey'
export { useAdminBreadcrumb } from './composables/useAdminBreadcrumb'
export { asMenuIcon } from './menu-icon'
export { DEFAULT_COLLAPSED_STORAGE_KEY, DEFAULT_MODULE_ORDER, DEFAULT_PAGE_HERO } from './model/constants'
export type {
  AdminBreadcrumbItem,
  AdminModule,
  AdminRouteMeta,
  AdminShellProps,
  CreateAdminShellOptions,
  CreateAdminShellResult,
  MenuIconSource,
} from './model/types'

export { default as AdminShell } from './components/AdminShell.vue'
export { default as AdminPageHero } from './components/AdminPageHero.vue'
export { default as AdminBreadcrumb } from './components/AdminBreadcrumb.vue'
export { default as AdminPageHeader } from './components/AdminPageHeader.vue'
