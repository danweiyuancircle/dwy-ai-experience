/**
 * ESlider 滑动条组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ESlider Props */
export interface ESliderProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前值数组；长度决定滑块数量（1=单滑块，2=范围） */
  modelValue?: number[]
  /** 最小值，默认 0 */
  min?: number
  /** 最大值，默认 100 */
  max?: number
  /** 步进值，默认 1 */
  step?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 方向，默认水平 */
  orientation?: 'horizontal' | 'vertical'
}

/** ESlider Emits */
export interface ESliderEmits {
  /** 值更新，用于 v-model */
  'update:modelValue': [value: number[]]
}
