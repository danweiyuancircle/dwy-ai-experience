/**
 * EAdminLayout 管理后台布局组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { MenuItem } from '@/types'

/**
 * EAdminLayout 管理后台布局 Props
 */
export interface EAdminLayoutProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 左上角 logo 图片地址 */
  logo?: string
  /** 左上角系统标题，折叠时隐藏 */
  title?: string
  /** 侧边栏菜单数据 */
  menuItems?: MenuItem[]
  /** 当前激活的菜单 key */
  activeKey?: string
  /** 侧边栏是否折叠 */
  collapsed?: boolean
  /** 是否显示底部 footer 区域 */
  showFooter?: boolean
  /** 顶部 header 高度（支持数字 px 或自定义字符串） */
  headerHeight?: string | number
  /** 展开态侧边栏宽度 */
  sidebarWidth?: string | number
  /** 折叠态侧边栏宽度 */
  collapsedWidth?: string | number
  /** 为 true 时菜单点击会触发 vue-router 路由跳转 */
  router?: boolean
  /**
   * 窄屏侧栏模式。
   * `drawer`（默认）：小于断点时侧栏改为 ESheet 覆层，不占宽。
   * `none`：保持桌面折叠行为（逃生开关）。
   */
  mobileMode?: 'drawer' | 'none'
  /** 覆盖全局 mobileBreakpoint（px）。不传则用 EConfigProvider / 默认 767 */
  mobileBreakpoint?: number
  /** 手机抽屉是否打开，v-model:mobileOpen。仅 drawer 模式生效 */
  mobileOpen?: boolean
}

/**
 * EAdminLayout 管理后台布局事件
 */
export interface EAdminLayoutEmits {
  /** 激活菜单 key 变化时触发 */
  'update:activeKey': [key: string]
  /** 折叠状态变化时触发 */
  'update:collapsed': [value: boolean]
  /** 手机抽屉开关，用于 v-model:mobileOpen */
  'update:mobileOpen': [value: boolean]
  /** 菜单点击选中时触发（与 update:activeKey 并发，提供更语义化命名） */
  'menu-select': [key: string]
}
