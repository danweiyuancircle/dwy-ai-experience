/**
 * ECheckbox 复选框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Option } from '@/types'

/**
 * ECheckbox 复选框 Props
 */
export interface ECheckboxProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 单选模式为 boolean；传 options 后为组模式，值为已选项 value 数组 */
  modelValue?: boolean | (string | number)[]
  /** 单选模式下的标签文本 */
  label?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否处于半选状态（仅单选模式有效） */
  indeterminate?: boolean
  /** 传入选项数组时切换为组模式，渲染多个复选框 */
  options?: Option[]
  /** 组模式下的排列方向 */
  direction?: 'horizontal' | 'vertical'
  /** 是否给每个复选项加边框（类似 segment 风格） */
  border?: boolean
}

/**
 * ECheckbox 复选框事件
 */
export interface ECheckboxEmits {
  /** 选中值变化：单选为 boolean，组模式为值数组 */
  'update:modelValue': [value: boolean | (string | number)[]]
  /** change 事件，便于业务显式监听 */
  change: [value: boolean | (string | number)[]]
}
