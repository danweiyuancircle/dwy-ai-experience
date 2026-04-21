/**
 * ETagsInput 标签输入组件类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

/** ETagsInput Props */
export interface ETagsInputProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 标签字符串数组，v-model 绑定 */
  modelValue?: string[]
  /** 输入框占位文本 */
  placeholder?: string
  /** 最多允许的标签数量 */
  max?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 尺寸变体 */
  size?: Size
}

/** ETagsInput Emits */
export interface ETagsInputEmits {
  /** 标签列表更新，用于 v-model */
  'update:modelValue': [value: string[]]
  /** 标签变化事件 */
  change: [value: string[]]
}
