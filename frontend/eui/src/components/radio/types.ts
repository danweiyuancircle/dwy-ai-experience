/**
 * ERadio 单选框组件类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Option, Size } from '@/types'

/** ERadio Props */
export interface ERadioProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前选中值，v-model 绑定 */
  modelValue?: string | number
  /** 选项列表 */
  options?: Option[]
  /** 是否禁用整组 */
  disabled?: boolean
  /** 排列方向：水平或垂直 */
  direction?: 'horizontal' | 'vertical'
  /** 渲染样式：default=圆点，button=相连按钮组 */
  optionType?: 'default' | 'button'
  /** 是否为每个选项加圆角边框（仅 default 模式下生效） */
  border?: boolean
  /** 尺寸变体 */
  size?: Size
}

/** ERadio Emits */
export interface ERadioEmits {
  /** 选中值更新，用于 v-model */
  'update:modelValue': [value: string | number]
  /** 选中值变化事件，与 update:modelValue 同步 */
  change: [value: string | number]
}
