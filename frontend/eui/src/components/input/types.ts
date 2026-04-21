/**
 * EInput 输入框组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Size } from '@/types'

/**
 * EInput 输入框 Props
 */
export interface EInputProps {
  /** 自定义 class，透传到根容器 */
  class?: HTMLAttributes['class']
  /** 输入值，支持 v-model */
  modelValue?: string | number
  /** 原生 input type（text / password / email 等） */
  type?: string
  /** 占位文本 */
  placeholder?: string
  /** 尺寸 */
  size?: Size
  /** 是否禁用 */
  disabled?: boolean
  /** 是否只读 */
  readonly?: boolean
  /** 是否显示清空按钮 */
  clearable?: boolean
  /** 最大输入长度 */
  maxlength?: number
  /** 密码类型下是否显示明文切换按钮 */
  showPassword?: boolean
  /** 是否显示字数统计（需配合 maxlength） */
  showWordLimit?: boolean
  /** 原生 name 属性 */
  name?: string
  /** 原生 autocomplete 属性 */
  autocomplete?: string
}

/**
 * EInput 输入框事件
 */
export interface EInputEmits {
  /** 值变化 */
  'update:modelValue': [value: string]
  /** 原生 change 事件（失焦或按回车） */
  change: [value: string]
  /** 失焦事件 */
  blur: [event: FocusEvent]
  /** 聚焦事件 */
  focus: [event: FocusEvent]
  /** 点击清空按钮时触发 */
  clear: []
}
