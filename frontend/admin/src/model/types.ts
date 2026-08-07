/**
 * @dwydev/admin-kit 类型定义
 * 管理系统骨架：模块契约、装配选项、顶栏 chrome 与 RouteMeta 约定。
 * 框架不实现鉴权 / 业务 store，只负责壳布局、通用 chrome 与模块装配。
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
 * 骨架功能开关
 * 全部可选；未传字段回落 DEFAULT_FEATURES。
 */
export interface AdminShellFeatures {
  /** 顶栏主题切换按钮。默认 true */
  theme?: boolean
  /** 顶栏通知铃铛与下拉面板。默认 true */
  notifications?: boolean
  /** 顶栏用户头像下拉。默认 true */
  userMenu?: boolean
  /** 全局命令面板 ⌘K（预留，默认 false） */
  command?: boolean
}

/**
 * 当前登录用户展示信息（骨架只负责展示，不拉接口）
 */
export interface AdminUserInfo {
  /** 显示名。示例：`张三` */
  name: string
  /** 邮箱，展示在下拉头部。示例：`a@b.com` */
  email?: string
  /** 角色文案。示例：`管理员` */
  roleLabel?: string
  /** 头像 URL；缺省用 name 首字母 fallback */
  avatarUrl?: string
}

/**
 * 通知列表项（骨架只渲染，数据由宿主注入）
 */
export interface AdminNotificationItem {
  /** 唯一 id */
  id: string
  /** 标题。长度建议 [1, 80] */
  title: string
  /** 摘要。长度建议 [0, 200] */
  description?: string
  /** 相对时间文案。示例：`2 小时前` */
  time?: string
  /** 是否未读（展示红点） */
  unread?: boolean
}

/**
 * 用户下拉菜单项（除内置「退出」外的扩展）
 */
export interface AdminUserMenuItem {
  /** 唯一 key，select 时回传 */
  key: string
  /** 显示文本 */
  label: string
  /** 选中后跳转 path；与 onSelect 二选一 */
  to?: string
  /** 危险样式（如退出） */
  destructive?: boolean
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
  /**
   * 点击 logo/标题跳转 path。
   * 默认 `/`；空字符串关闭点击。示例：`/dashboard`
   */
  logoTo?: string
  /** 业务模块列表，按 order 排序后合并 */
  modules: AdminModule[]
  /**
   * 侧栏折叠 localStorage key，多站隔离。
   * 默认 `dwy-admin:sidebar:collapsed`。
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
  /** 顶栏功能开关 */
  features?: AdminShellFeatures
}

/**
 * AdminShell 组件 props
 * 与 createAdminShell 产出的 shellProps 对齐，宿主可直接 v-bind 并叠加 user/notifications。
 */
export interface AdminShellProps {
  /** 左上角系统标题 */
  title: string
  /** 左上角 logo */
  logo?: string
  /** 点击 logo 跳转；空串关闭 */
  logoTo?: string
  /** 合并后的侧栏菜单 */
  menuItems: MenuItem[]
  /** 折叠状态 storage key */
  collapsedStorageKey?: string
  /** 壳默认是否显示 PageHero */
  pageHero?: boolean
  /** 功能开关（与 createAdminShell.features 合并） */
  features?: AdminShellFeatures
  /** 当前用户（userMenu 开启时使用） */
  user?: AdminUserInfo | null
  /** 通知列表（notifications 开启时使用） */
  notifications?: AdminNotificationItem[]
  /** 用户下拉额外菜单项（在「退出」前） */
  userMenuItems?: AdminUserMenuItem[]
  /** 个人中心 path，默认 /settings */
  profilePath?: string
  /** 通知「查看全部」path；有则显示脚链 */
  notificationsPath?: string
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
  /** 可直接 v-bind 到 AdminShell 的 props（不含 user/notifications 运行时数据） */
  shellProps: Pick<
    AdminShellProps,
    'title' | 'logo' | 'logoTo' | 'menuItems' | 'collapsedStorageKey' | 'pageHero' | 'features'
  >
}

/** lucide 等图标组件在 MenuItem.icon 上的类型断言辅助入参 */
export type MenuIconSource = unknown
