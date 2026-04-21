/**
 * EDescriptions 详情描述列表组件的类型定义
 */

/**
 * 详情列表单项
 */
export interface DescriptionItem {
  /** 字段名称 */
  label: string
  /** 字段值，可通过插槽覆盖 */
  value?: string | number
  /** 占用的列数（用于跨列） */
  span?: number
}

/**
 * EDescriptions 详情描述列表 Props
 */
export interface EDescriptionsProps {
  /** 自定义 class，透传到根元素 */
  class?: string
  /** 描述项数组 */
  items?: DescriptionItem[]
  /** 每行列数 */
  columns?: number
  /** 是否带边框（开启后有表格式样式） */
  bordered?: boolean
  /** 顶部标题 */
  title?: string
}
