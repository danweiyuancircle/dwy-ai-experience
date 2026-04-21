/**
 * ENativeSelect 原生下拉组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 下拉选项 */
export interface SelectOption {
  /** 显示文本 */
  label: string
  /** 选项值 */
  value: string | number
}

/** ENativeSelect Props */
export interface ENativeSelectProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前选中值，支持多选数组 */
  modelValue?: string | number | string[] | number[]
  /** 选项列表 */
  options?: SelectOption[]
  /** 占位文本（作为首个 disabled option 展示） */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
}

/** ENativeSelect Emits */
export interface ENativeSelectEmits {
  /** 值变更，用于 v-model */
  'update:modelValue': [value: string | number]
  /** 原生 change 事件透传，附带原始 event 便于自定义处理 */
  change: [event: Event]
}
