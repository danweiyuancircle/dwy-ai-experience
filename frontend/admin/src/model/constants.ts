/**
 * @dwydev/admin 默认常量
 * 宿主未覆盖时使用；业务可调参数不硬编码在组件内。
 */

/** 侧栏折叠状态默认 localStorage key */
export const DEFAULT_COLLAPSED_STORAGE_KEY = 'dwy-admin:sidebar:collapsed'

/** 点击 logo 默认跳转 path */
export const DEFAULT_LOGO_TO = '/'

/** 模块默认排序权重 */
export const DEFAULT_MODULE_ORDER = 100

/** 壳层默认开启 PageHero */
export const DEFAULT_PAGE_HERO = true

/**
 * 默认功能开关
 * theme/notifications/userMenu 默认开启（骨架完整预览）；
 * 业务仓若只要布局可显式关掉，继续用 #header-extra。
 */
export const DEFAULT_FEATURES = {
  theme: true,
  notifications: true,
  userMenu: true,
  command: false,
} as const
