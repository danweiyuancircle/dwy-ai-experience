/**
 * EToggleGroup 开关按钮组类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { ToggleVariants } from '../toggle/types'

/** EToggleGroup Props */
export interface EToggleGroupProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 选中值；single 模式为字符串，multiple 模式为字符串数组 */
  modelValue?: string | string[]
  /** 组类型：single=互斥单选，multiple=多选 */
  type?: 'single' | 'multiple'
  /** 视觉变体，透传给每个 EToggle */
  variant?: ToggleVariants['variant']
  /** 尺寸变体，透传给每个 EToggle */
  size?: ToggleVariants['size']
  /** 是否禁用整组 */
  disabled?: boolean
}

/** EToggleGroup Emits */
export interface EToggleGroupEmits {
  /** 选中值更新，用于 v-model */
  'update:modelValue': [value: string | string[]]
}
