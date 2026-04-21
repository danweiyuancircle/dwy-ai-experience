/**
 * EPagination 分页组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** EPagination Props */
export interface EPaginationProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前页码（从 1 开始），v-model 绑定 */
  modelValue?: number
  /** 总条数 */
  total?: number
  /** 每页条数 */
  pageSize?: number
  /** 当前页两侧显示的相邻页码数量 */
  siblingCount?: number
  /** 是否展示每页条数切换器 */
  showSizeChanger?: boolean
  /** 可选的每页条数列表 */
  pageSizes?: number[]
  /** 是否展示总条数文字 */
  showTotal?: boolean
  /** 是否展示页码跳转输入框 */
  jumper?: boolean
  /** 布局字符串，逗号分隔：total/sizes/prev/pager/next/jumper */
  layout?: string
  /** 是否禁用整个分页 */
  disabled?: boolean
}

/** EPagination Emits */
export interface EPaginationEmits {
  /** 当前页变化，用于 v-model */
  (e: 'update:modelValue', page: number): void
  /** 当前页变化事件（与 update:modelValue 同步） */
  (e: 'change', page: number): void
  /** 每页条数变化，用于 v-model:pageSize */
  (e: 'update:pageSize', size: number): void
  /** 每页条数变化事件 */
  (e: 'size-change', size: number): void
}
