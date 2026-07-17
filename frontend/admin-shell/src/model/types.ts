/**
 * @dwydev/admin-shell 类型定义
 * 管理系统扩展站路由框架的模块契约、装配选项与 RouteMeta 约定。
 * 框架不实现鉴权 / 业务 store，只负责壳布局与模块装配。
 */
import type { RouteMeta, RouteRecordRaw } from 'vue-router'
import type { MenuItem } from '@dwydev/eui'

/**
 * 面包屑单项
 * to 存在时渲染为可点击链接（SPA router-link），末项通常不传 to。
 */
export interface AdminBreadcrumbItem {
  /** 显示文本。长度建议 [1, 64]。示例：`用量统计` */
  label: string
  /** 跳转 path；省略则纯文本。示例：`/dashboard` */
  to?: string
}

/**
 * 管理系统路由 meta 约定（宿主可在 vue-router 模块扩展中对齐）
 * 与业务鉴权字段（requiresAuth 等）并存，框架只消费下列字段。
 */
export interface AdminRouteMeta {
  /** 页面标题；PageHero 与 document.title 同源。示例：`数据概览` */
  title?: string
  /** 页头副标题 / 描述。示例：`管理 SDK 访问凭证` */
  description?: string
  /**
   * 侧栏高亮 key；嵌套子路径时指向父叶子菜单 key。
   * 缺省用 route.path。示例：`/settings`
   */
  menuKey?: string
  /**
   * 是否由 AdminShell 渲染 PageHero（面包屑 + 页头）。
   * 默认 true；复杂自定义页可 false。
   */
  pageHero?: boolean
  /** 覆盖自动推导的面包屑；末项一般无 to */
  breadcrumb?: AdminBreadcrumbItem[]
}

/**
 * 可挂接的业务模块
 * 宿主通过 modules 列表注册，框架合并菜单与路由。
 */
export interface AdminModule {
  /** 模块唯一 id，用于调试与去重。示例：`quota` */
  id: string
  /**
   * 侧栏菜单贡献；支持 children 子菜单 / 分组。
   * 分组父节点 key 建议 `group-*`，不参与路由跳转。
   */
  menu?: MenuItem | MenuItem[]
  /** 路由贡献（叶子或带子路由）。path 可用相对或绝对，装配时归一为绝对 path */
  routes: RouteRecordRaw[]
  /**
   * 菜单排序权重，越小越靠前。
   * 取值范围 [0, 10000]，默认 100。示例：`10`
   */
  order?: number
  /**
   * 是否展示在侧栏；false 时只注册路由（隐藏页 / 详情页）。
   * 默认 true。
   */
  showInMenu?: boolean
}

/**
 * createAdminShell 装配选项
 * 纯数据配置，不持有业务状态。
 */
export interface CreateAdminShellOptions {
  /** 左上角系统标题。示例：`宽舟科技` */
  title: string
  /** 左上角 logo 图片地址。示例：`/logo.png` */
  logo?: string
  /** 业务模块列表，按 order 排序后合并 */
  modules: AdminModule[]
  /**
   * 侧栏折叠 localStorage key，多站隔离。
   * 默认 `admin:sidebar:collapsed`。示例：`cloud:admin:sidebar:collapsed`
   */
  collapsedStorageKey?: string
  /**
   * 壳层默认是否渲染 PageHero。
   * 可被单页 meta.pageHero 覆盖。默认 true。
   */
  pageHero?: boolean
  /**
   * 写入每个 module 路由的默认 meta（宿主 layout / 鉴权等）。
   * 与路由自身 meta 浅合并，路由字段优先。
   */
  routeMetaDefaults?: RouteMeta
}

/**
 * AdminShell 组件 props
 * 与 createAdminShell 产出的 shellProps 对齐，宿主可直接 v-bind。
 */
export interface AdminShellProps {
  /** 左上角系统标题 */
  title: string
  /** 左上角 logo */
  logo?: string
  /** 合并后的侧栏菜单 */
  menuItems: MenuItem[]
  /** 折叠状态 storage key */
  collapsedStorageKey?: string
  /** 壳默认是否显示 PageHero */
  pageHero?: boolean
}

/**
 * createAdminShell 返回值
 * 宿主用 routes 注册路由，用 shellProps 驱动 AdminShell。
 */
export interface CreateAdminShellResult {
  /** 按 order 合并后的侧栏菜单 */
  menuItems: MenuItem[]
  /** 归一化 path 并注入 routeMetaDefaults 后的路由列表 */
  routes: RouteRecordRaw[]
  /** 可直接 v-bind 到 AdminShell 的 props */
  shellProps: AdminShellProps
}

/** lucide 等图标组件在 MenuItem.icon 上的类型断言辅助入参 */
export type MenuIconSource = unknown
