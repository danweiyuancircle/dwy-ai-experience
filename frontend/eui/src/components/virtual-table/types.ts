/**
 * EVirtualTable 虚拟表格组件类型定义
 */

/** 虚拟表格的列定义 */
export interface VirtualTableColumn {
  /** 字段名（对应行数据的 key） */
  key: string
  /** 表头文字 */
  title: string
  /** 列宽，数字按 px，字符串支持 % 等单位 */
  width?: number | string
  /** 对齐方式 */
  align?: 'left' | 'center' | 'right'
}

/** EVirtualTable Props */
export interface EVirtualTableProps {
  /** 自定义类名 */
  class?: string
  /** 列定义 */
  columns?: VirtualTableColumn[]
  /** 数据源 */
  data?: Record<string, any>[]
  /** 容器固定高度（px） */
  height?: number
  /** 预估行高（px），保留给未来按需虚拟化使用 */
  estimateRowHeight?: number
  /** 行唯一标识字段，默认 'id' */
  rowKey?: string
  /** 是否显示 loading 蒙层 */
  loading?: boolean
  /** 无数据时的提示文本 */
  emptyText?: string
}

/** EVirtualTable Emits */
export interface EVirtualTableEmits {
  /** 点击行事件 */
  (e: 'row-click', row: Record<string, any>, index: number): void
}
