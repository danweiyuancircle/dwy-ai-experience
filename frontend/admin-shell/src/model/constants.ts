/**
 * admin-shell 默认常量
 * 宿主未覆盖时使用；业务可调参数不硬编码在组件内。
 */

/** 侧栏折叠状态默认 localStorage key */
export const DEFAULT_COLLAPSED_STORAGE_KEY = 'admin:sidebar:collapsed'

/** 模块默认排序权重 */
export const DEFAULT_MODULE_ORDER = 100

/** 壳层默认开启 PageHero */
export const DEFAULT_PAGE_HERO = true

/**
 * 侧栏 logo/标题默认跳转路径
 * 宿主可按业务改成控制台首页（如 `/dashboard`）或营销首页 `/`
 */
export const DEFAULT_LOGO_TO = '/'
