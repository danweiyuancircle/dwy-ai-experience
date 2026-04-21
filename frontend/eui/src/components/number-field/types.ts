/**
 * ENumberField 数字输入框组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ENumberField Props */
export interface ENumberFieldProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前数值，v-model 绑定 */
  modelValue?: number
  /** 允许的最小值 */
  min?: number
  /** 允许的最大值 */
  max?: number
  /** 步进值，默认 1 */
  step?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 尺寸，影响高度和字号，默认 md */
  size?: 'sm' | 'md' | 'lg'
  /** 小数精度，用于 Intl.NumberFormat 格式化 */
  precision?: number
  /** 加减按钮位置：default=左右分布，right=叠于右侧 */
  controlsPosition?: 'default' | 'right'
  /** 占位文本 */
  placeholder?: string
  /** 是否只读 */
  readonly?: boolean
}

/** ENumberField Emits */
export interface ENumberFieldEmits {
  /** 值更新，用于 v-model */
  (e: 'update:modelValue', value: number): void
  /** 值变化事件，与 update:modelValue 同步触发 */
  (e: 'change', value: number): void
}
