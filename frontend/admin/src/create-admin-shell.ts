/**
 * createAdminShell：合并 modules 的菜单与路由，产出壳 props + 可注册路由。
 * 不实现鉴权；routeMetaDefaults 仅做 meta 浅合并。
 */
import type { MenuItem } from '@dwydev/eui'
import type { RouteMeta, RouteRecordRaw } from 'vue-router'
import { defineAdminModule } from './define-admin-module'
import {
  DEFAULT_COLLAPSED_STORAGE_KEY,
  DEFAULT_FEATURES,
  DEFAULT_LOGO_TO,
  DEFAULT_PAGE_HERO,
} from './model/constants'
import type {
  AdminModule,
  AdminShellFeatures,
  CreateAdminShellOptions,
  CreateAdminShellResult,
} from './model/types'

/**
 * 将路由 path 归一为以 / 开头的绝对 path。
 */
export function normalizeRoutePath(path: string): string {
  if (!path || path === '/') return '/'
  return path.startsWith('/') ? path : `/${path}`
}

/**
 * 递归把路由树 path 归一为绝对 path，并浅合并默认 meta。
 */
export function normalizeRoutes(
  routes: RouteRecordRaw[],
  metaDefaults: RouteMeta = {},
): RouteRecordRaw[] {
  return routes.map((route) => {
    const path = typeof route.path === 'string' ? normalizeRoutePath(route.path) : route.path
    const meta: RouteMeta = { ...metaDefaults, ...route.meta }
    const next: RouteRecordRaw = {
      ...route,
      path,
      meta,
    }
    if (route.children?.length) {
      next.children = normalizeRoutes(route.children as RouteRecordRaw[], metaDefaults)
    }
    return next
  })
}

/**
 * 按 order 排序 modules，展开 showInMenu 的 menu 贡献。
 */
export function collectMenuItems(modules: AdminModule[]): MenuItem[] {
  const sorted = [...modules].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  const items: MenuItem[] = []
  for (const mod of sorted) {
    if (mod.showInMenu === false || !mod.menu) continue
    if (Array.isArray(mod.menu)) {
      items.push(...mod.menu)
    } else {
      items.push(mod.menu)
    }
  }
  return items
}

/**
 * 按 order 收集并归一化全部模块路由。
 */
export function collectRoutes(
  modules: AdminModule[],
  metaDefaults: RouteMeta = {},
): RouteRecordRaw[] {
  const sorted = [...modules].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  return sorted.flatMap((mod) => normalizeRoutes(mod.routes, metaDefaults))
}

/**
 * 合并功能开关：调用方字段优先，缺省用 DEFAULT_FEATURES。
 */
export function resolveFeatures(features?: AdminShellFeatures): Required<AdminShellFeatures> {
  return {
    theme: features?.theme ?? DEFAULT_FEATURES.theme,
    notifications: features?.notifications ?? DEFAULT_FEATURES.notifications,
    userMenu: features?.userMenu ?? DEFAULT_FEATURES.userMenu,
    command: features?.command ?? DEFAULT_FEATURES.command,
  }
}

/**
 * 装配管理系统壳：合并菜单、路由，返回可直接接入宿主的结果。
 */
export function createAdminShell(options: CreateAdminShellOptions): CreateAdminShellResult {
  const modules = options.modules.map((m) => defineAdminModule(m))
  const menuItems = collectMenuItems(modules)
  const routes = collectRoutes(modules, options.routeMetaDefaults ?? {})
  const collapsedStorageKey = options.collapsedStorageKey ?? DEFAULT_COLLAPSED_STORAGE_KEY
  const pageHero = options.pageHero ?? DEFAULT_PAGE_HERO
  // 显式传空串表示关闭点击；未传则用默认首页 path
  const logoTo = options.logoTo === undefined ? DEFAULT_LOGO_TO : options.logoTo
  const features = resolveFeatures(options.features)

  return {
    menuItems,
    routes,
    shellProps: {
      title: options.title,
      logo: options.logo,
      logoTo,
      menuItems,
      collapsedStorageKey,
      pageHero,
      features,
    },
  }
}
