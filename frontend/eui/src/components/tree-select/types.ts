/**
 * ETreeSelect 树形下拉选择器类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { TreeNode } from '../tree/types'

/** ETreeSelect Props */
export interface ETreeSelectProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前选中值；多选/勾选模式下为数组 */
  modelValue?: string | number | (string | number)[]
  /** 树形数据 */
  data?: TreeNode[]
  /** 占位文本 */
  placeholder?: string
  /** 是否多选（modelValue 为数组） */
  multiple?: boolean
  /** 是否在树中显示复选框 */
  checkable?: boolean
  /** 是否禁用 */
  disabled?: boolean
}

/** ETreeSelect Emits */
export interface ETreeSelectEmits {
  /** 值更新，用于 v-model */
  (e: 'update:modelValue', value: string | number | (string | number)[] | undefined): void
  /** 值变化事件 */
  (e: 'change', value: string | number | (string | number)[] | undefined): void
}
