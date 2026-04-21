/**
 * EInfiniteScroll 无限滚动组件的类型定义
 */

/**
 * EInfiniteScroll 无限滚动 Props
 */
export interface EInfiniteScrollProps {
  /** 自定义 class */
  class?: string
  /** 是否正在加载，加载中不会重复触发 load */
  loading?: boolean
  /** 是否已加载完毕（无更多数据），为 true 时不再触发 load */
  disabled?: boolean
  /** 距离底部多少 px 开始触发加载 */
  distance?: number
}

/**
 * EInfiniteScroll 无限滚动事件
 */
export interface EInfiniteScrollEmits {
  /** 触底时触发，由外部实现加载下一页 */
  (e: 'load'): void
}
