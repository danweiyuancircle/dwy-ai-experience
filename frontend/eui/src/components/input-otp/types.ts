/**
 * EInputOTP 一次性验证码输入组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EInputOTP 一次性验证码输入 Props
 */
export interface EInputOTPProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 输入值，长度等于 length 时视为完整 */
  modelValue?: string
  /** 总位数 */
  length?: number
  /** 是否禁用 */
  disabled?: boolean
  /** 每个格子的占位符 */
  placeholder?: string
}

/**
 * EInputOTP 一次性验证码输入事件
 */
export interface EInputOTPEmits {
  /** 输入值变化 */
  'update:modelValue': [value: string]
  /** 填满所有格子时触发，可用于自动提交 */
  complete: [value: string]
}
