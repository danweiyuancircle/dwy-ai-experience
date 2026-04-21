/**
 * ETextarea 多行文本输入框组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ETextarea Props */
export interface ETextareaProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前值，v-model 绑定 */
  modelValue?: string
  /** 占位文本 */
  placeholder?: string
  /** 初始行数 */
  rows?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 是否只读 */
  readonly?: boolean
  /** 最大字符数 */
  maxlength?: number
  /** 是否根据内容自动调整高度 */
  autoResize?: boolean
  /** 配合 maxlength 显示 "当前/上限" 字数计数 */
  showWordLimit?: boolean
  /** autoResize 下允许的最小行数 */
  minRows?: number
  /** autoResize 下允许的最大行数，超出改为内部滚动 */
  maxRows?: number
}

/** ETextarea Emits */
export interface ETextareaEmits {
  /** 值更新，用于 v-model */
  (e: 'update:modelValue', value: string): void
  /** 值变化事件（native change） */
  (e: 'change', value: string): void
  /** 失焦事件 */
  (e: 'blur', event: FocusEvent): void
  /** 聚焦事件 */
  (e: 'focus', event: FocusEvent): void
}
