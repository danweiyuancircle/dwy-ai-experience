/**
 * EResizable 可伸缩面板组件类型定义
 */

/** 面板容器 Props */
export interface EResizablePanelGroupProps {
  /** 自定义类名 */
  class?: string
  /** 面板排列方向：水平或垂直 */
  direction?: 'horizontal' | 'vertical'
  /** 容器 id，用于持久化布局 */
  id?: string
}

/** 单个面板 Props */
export interface EResizablePanelProps {
  /** 默认占比（0-100） */
  defaultSize?: number
  /** 最小占比约束 */
  minSize?: number
  /** 最大占比约束 */
  maxSize?: number
  /** 面板 id，用于持久化布局 */
  id?: string
}

/** 拖拽分隔条 Props */
export interface EResizableHandleProps {
  /** 自定义类名 */
  class?: string
  /** 是否显示抓握把手图标，提升可发现性 */
  withHandle?: boolean
  /** 分隔条 id */
  id?: string
}
