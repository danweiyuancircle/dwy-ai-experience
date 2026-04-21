/**
 * EBreadcrumb 面包屑导航组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * 面包屑项配置
 */
export interface BreadcrumbItem {
  /** 显示文本 */
  label: string
  /** 链接地址，省略则渲染为纯文本 */
  href?: string
  /** 可选图标组件（lucide-vue-next 等图标组件） */
  // 图标组件类型无固定约束，此处允许传入任意组件
  icon?: any
}

/**
 * EBreadcrumb 面包屑导航 Props
 */
export interface EBreadcrumbProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 面包屑数据源 */
  items?: BreadcrumbItem[]
  /** 分隔符文本，未设置时使用默认的右箭头图标 */
  separator?: string
}
