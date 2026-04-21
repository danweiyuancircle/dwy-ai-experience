/**
 * EProgress 进度条组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** EProgress Props */
export interface EProgressProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前进度值，取值范围 0-100，v-model 绑定 */
  modelValue?: number
}
