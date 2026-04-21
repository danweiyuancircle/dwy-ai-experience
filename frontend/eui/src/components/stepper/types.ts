/**
 * EStepper 步骤条组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 单个步骤项定义 */
export interface StepperItem {
  /** 步骤标题 */
  title: string
  /** 步骤描述（可选） */
  description?: string
}

/** EStepper Props */
export interface EStepperProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前步骤序号（从 1 开始），v-model 绑定 */
  modelValue?: number
  /** 步骤项列表 */
  items?: StepperItem[]
  /** 排列方向，默认水平 */
  direction?: 'horizontal' | 'vertical'
}

/** EStepper Emits */
export interface EStepperEmits {
  /** 当前步骤更新，用于 v-model */
  (e: 'update:modelValue', value: number): void
}
