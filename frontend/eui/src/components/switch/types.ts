/**
 * ESwitch 开关组件类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

/** ESwitch Props */
export interface ESwitchProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 开关状态，v-model 绑定 */
  modelValue?: boolean
  /** 开关右侧的描述文本 */
  label?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 尺寸变体 */
  size?: Size
}

/** ESwitch Emits */
export interface ESwitchEmits {
  /** 状态更新，用于 v-model */
  'update:modelValue': [value: boolean]
  /** 状态变化事件 */
  change: [value: boolean]
}
