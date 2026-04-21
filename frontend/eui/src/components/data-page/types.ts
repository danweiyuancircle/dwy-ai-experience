/**
 * EDataPage 数据列表页组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { TableColumn } from '@/types'

/**
 * 列表请求参数
 */
export interface FetchParams {
  /** 当前页码，从 1 开始 */
  page: number
  /** 每页条数 */
  pageSize: number
  /** 搜索关键词 */
  keyword?: string
}

/**
 * 列表请求返回结构
 */
export interface FetchResult {
  /** 当前页数据列表 */
  // 业务数据形状由外部决定，此处放宽
  items: any[]
  /** 总条数，用于分页 */
  total: number
}

/**
 * EDataPage 数据列表页 Props
 */
export interface EDataPageProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 表格列配置 */
  columns: TableColumn[]
  /** 数据获取函数，由外部实现 */
  fetchFn: (params: FetchParams) => Promise<FetchResult>
  /** 是否显示搜索框 */
  searchable?: boolean
  /** 每页条数初始值 */
  pageSize?: number
}
