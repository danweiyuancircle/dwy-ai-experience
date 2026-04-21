/**
 * ETimePicker 时间选择器组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ETimePicker Props */
export interface ETimePickerProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前值，格式 HH:mm，v-model 绑定 */
  modelValue?: string
  /** 占位文本；未提供时回落到 locale */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 显示格式（目前主要用于外部标识，实际渲染固定 HH:mm） */
  format?: string
  /** 小时步长，默认 1 */
  hourStep?: number
  /** 分钟步长，默认 1 */
  minuteStep?: number
}

/** ETimePicker Emits */
export interface ETimePickerEmits {
  /** 值更新，用于 v-model */
  (e: 'update:modelValue', value: string): void
  /** 值变化事件 */
  (e: 'change', value: string): void
}
