/**
 * EAffix 固钉组件的类型定义
 */

/**
 * EAffix 固钉组件 Props
 */
export interface EAffixProps {
  /** 自定义 class，透传到内层固定元素 */
  class?: string
  /** 固定时距视口边缘的偏移量（单位 px） */
  offset?: number
  /** 固定位置：top=顶部吸附，bottom=底部吸附 */
  position?: 'top' | 'bottom'
}
