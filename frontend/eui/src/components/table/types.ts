/**
 * ETable 数据表格组件类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { TableColumn } from '@/types'

/** ETable Props */
export interface ETableProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 数据源 */
  data?: Record<string, any>[]
  /** 列定义 */
  columns?: TableColumn[]
  /** 是否显示 loading 蒙层 */
  loading?: boolean
  /** 行唯一标识字段，默认 'id' */
  rowKey?: string
  /** 是否斑马纹 */
  striped?: boolean
  /** 是否显示外边框 */
  bordered?: boolean
  /** 空数据提示文本 */
  emptyText?: string
  /** 是否开启行选择（复选框列） */
  selectable?: boolean
  /** 当前选中的行 key 列表，v-model:selectedKeys */
  selectedKeys?: (string | number)[]
  /** 是否支持行展开 */
  expandable?: boolean
  /** 当前展开的行 key 列表，v-model:expandedRowKeys */
  expandedRowKeys?: (string | number)[]
  /** 行级 class，支持静态字符串或函数按行计算 */
  rowClassName?: string | ((row: Record<string, any>, index: number) => string)
  /** 是否显示汇总行（tfoot） */
  showSummary?: boolean
  /** 自定义汇总计算函数；返回按列顺序排列的汇总值数组 */
  summaryMethod?: (data: Record<string, any>[], columns: TableColumn[]) => (string | number)[]
  /** 是否开启虚拟滚动（适用于大数据量） */
  virtual?: boolean
  /** 虚拟滚动的行高（px），用于位置计算 */
  virtualRowHeight?: number
  /** 是否允许拖拽列宽 */
  resizable?: boolean
}

/** ETable Emits */
export interface ETableEmits {
  /** 点击行事件 */
  'row-click': [row: Record<string, any>, index: number]
  /** 选中行变更，用于 v-model:selectedKeys */
  'update:selectedKeys': [keys: (string | number)[]]
  /** 展开行变更，用于 v-model:expandedRowKeys */
  'update:expandedRowKeys': [keys: (string | number)[]]
  /** 排序变化事件，direction 为 null 表示取消排序 */
  sort: [key: string, direction: 'asc' | 'desc' | null]
}
