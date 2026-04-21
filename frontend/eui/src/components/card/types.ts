/**
 * ECard 卡片组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * ECard 卡片 Props
 */
export interface ECardProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 卡片标题文本，也可通过 title 具名插槽覆盖 */
  title?: string
  /** 卡片描述文本，也可通过 description 具名插槽覆盖 */
  description?: string
}
