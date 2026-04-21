/**
 * ECollapsible 可折叠内容组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * ECollapsible 可折叠内容 Props
 */
export interface ECollapsibleProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 是否展开，支持 v-model */
  modelValue?: boolean
  /** 是否禁用展开/收起操作 */
  disabled?: boolean
}

/**
 * ECollapsible 可折叠内容事件
 */
export interface ECollapsibleEmits {
  /** 展开状态变化 */
  (e: 'update:modelValue', value: boolean): void
}
