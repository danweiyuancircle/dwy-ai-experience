/**
 * ELabel 表单标签组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * ELabel 表单标签 Props
 */
export interface ELabelProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** 关联的表单控件 id（对应原生 label for 属性） */
  for?: string
}
