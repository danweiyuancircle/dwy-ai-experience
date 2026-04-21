/**
 * EKbd 键盘按键展示组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * EKbd 键盘按键 Props
 */
export interface EKbdProps {
  /** 自定义 class，透传到 <kbd> 元素 */
  class?: HTMLAttributes['class']
}
