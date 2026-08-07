/**
 * @dwydev/admin-kit
 * 通用后台管理系统骨架：模块装配 + 内置顶栏 chrome + AdminShell 布局。
 * 与 @dwydev/admin-shell 并存；本包为完整骨架方案，原包保持不动。
 */

export {
  createAdminShell,
  collectMenuItems,
  collectRoutes,
  normalizeRoutePath,
  normalizeRoutes,
  resolveFeatures,
} from './create-admin-shell'
export { defineAdminModule } from './define-admin-module'
export { useAdminActiveKey } from './composables/useAdminActiveKey'
export { useAdminBreadcrumb } from './composables/useAdminBreadcrumb'
export { asMenuIcon } from './menu-icon'
export {
  DEFAULT_COLLAPSED_STORAGE_KEY,
  DEFAULT_FEATURES,
  DEFAULT_LOGO_TO,
  DEFAULT_MODULE_ORDER,
  DEFAULT_PAGE_HERO,
} from './model/constants'
export type {
  AdminBreadcrumbItem,
  AdminModule,
  AdminNotificationItem,
  AdminRouteMeta,
  AdminShellFeatures,
  AdminShellProps,
  AdminUserInfo,
  AdminUserMenuItem,
  CreateAdminShellOptions,
  CreateAdminShellResult,
  MenuIconSource,
} from './model/types'

export { default as AdminShell } from './components/AdminShell.vue'
export { default as AdminPageHero } from './components/AdminPageHero.vue'
export { default as AdminBreadcrumb } from './components/AdminBreadcrumb.vue'
export { default as AdminPageHeader } from './components/AdminPageHeader.vue'
