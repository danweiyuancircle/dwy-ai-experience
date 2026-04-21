/**
 * EDrawer 抽屉组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 抽屉滑出方向 */
export type DrawerDirection = 'top' | 'right' | 'bottom' | 'left'

/**
 * EDrawer 抽屉 Props
 */
export interface EDrawerProps {
  /** 自定义 class，透传到内容区 */
  class?: HTMLAttributes['class']
  /** 是否展开，支持 v-model:open */
  open?: boolean
  /** 抽屉标题 */
  title?: string
  /** 抽屉描述 */
  description?: string
  /** 滑出方向 */
  direction?: DrawerDirection
  /** 是否显示右上角关闭按钮 */
  showClose?: boolean
  /** 关闭时是否卸载默认插槽内容，默认 true */
  destroyOnClose?: boolean
}

/**
 * EDrawer 抽屉事件
 */
export interface EDrawerEmits {
  /** 展开状态变化 */
  'update:open': [value: boolean]
  /** 关闭时触发 */
  close: []
}
