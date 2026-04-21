/**
 * ECombobox 可搜索下拉选择器组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Option } from '@/types'

/**
 * ECombobox 可搜索下拉选择器 Props
 */
export interface EComboboxProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 选中项 value，支持 v-model */
  modelValue?: string | number
  /** 下拉选项 */
  options?: Option[]
  /** 占位文本 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 无搜索结果时的提示文案 */
  emptyText?: string
}

/**
 * ECombobox 可搜索下拉选择器事件
 */
export interface EComboboxEmits {
  /** 选中值变化 */
  (e: 'update:modelValue', value: string | number | undefined): void
  /** 业务 change 事件 */
  (e: 'change', value: string | number | undefined): void
}
