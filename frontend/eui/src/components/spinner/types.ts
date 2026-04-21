/**
 * ESpinner 加载中指示器类型定义
 */
import type { HTMLAttributes } from 'vue'

/** ESpinner Props */
export interface ESpinnerProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 尺寸变体，默认 default */
  size?: 'sm' | 'default' | 'lg'
}
