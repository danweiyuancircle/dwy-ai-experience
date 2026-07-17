/**
 * createAdminShell：合并 modules 的菜单与路由，产出壳 props + 可注册路由。
 * 不实现鉴权；routeMetaDefaults 仅做 meta 浅合并。
 */
import type { MenuItem } from '@dwydev/eui'
import type { RouteMeta, RouteRecordRaw } from 'vue-router'
import { defineAdminModule } from './define-admin-module'
import {
  DEFAULT_COLLAPSED_STORAGE_KEY,
  DEFAULT_PAGE_HERO,
} from './model/constants'
import type {
  AdminModule,
  CreateAdminShellOptions,
  CreateAdminShellResult,
} from './model/types'

/**
 * 将路由 path 归一为以 / 开头的绝对 path。
 * 空 path 或仅 `/` 保持为 `/`；已是绝对 path 则不重复加前缀。
 *
 * Args:
 *   path (string): 路由 path。示例：`quota` 或 `/quota`。
 * Returns:
 *   string: 绝对 path。示例：`/quota`。
 */
export function normalizeRoutePath(path: string): string {
  if (!path || path === '/') return '/'
  return path.startsWith('/') ? path : `/${path}`
}

/**
 * 递归把路由树 path 归一为绝对 path，并浅合并默认 meta。
 *
 * Args:
 *   routes (RouteRecordRaw[]): 模块贡献的路由。示例：`[{ path: 'quota', ... }]`。
 *   metaDefaults (RouteMeta): 默认 meta。示例：`{ requiresAuth: true, layout: 'admin' }`。
 * Returns:
 *   RouteRecordRaw[]: 新数组，不修改入参。
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
 *
 * Args:
 *   modules (AdminModule[]): 已 define 的模块列表。
 * Returns:
 *   MenuItem[]: 侧栏菜单（顺序稳定）。
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
 *
 * Args:
 *   modules (AdminModule[]): 模块列表。
 *   metaDefaults (RouteMeta): 默认 meta。
 * Returns:
 *   RouteRecordRaw[]: 扁平拼接后的路由列表（各模块 routes 顺序保留）。
 */
export function collectRoutes(
  modules: AdminModule[],
  metaDefaults: RouteMeta = {},
): RouteRecordRaw[] {
  const sorted = [...modules].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  return sorted.flatMap((mod) => normalizeRoutes(mod.routes, metaDefaults))
}

/**
 * 装配管理系统壳：合并菜单、路由，返回可直接接入宿主的结果。
 *
 * Args:
 *   options (CreateAdminShellOptions): 标题 / logo / modules 等。示例见类型注释。
 * Returns:
 *   CreateAdminShellResult: menuItems、routes、shellProps、AdminShell 组件。
 */
export function createAdminShell(options: CreateAdminShellOptions): CreateAdminShellResult {
  const modules = options.modules.map((m) => defineAdminModule(m))
  const menuItems = collectMenuItems(modules)
  const routes = collectRoutes(modules, options.routeMetaDefaults ?? {})
  const collapsedStorageKey = options.collapsedStorageKey ?? DEFAULT_COLLAPSED_STORAGE_KEY
  const pageHero = options.pageHero ?? DEFAULT_PAGE_HERO

  return {
    menuItems,
    routes,
    shellProps: {
      title: options.title,
      logo: options.logo,
      menuItems,
      collapsedStorageKey,
      pageHero,
    },
  }
}
