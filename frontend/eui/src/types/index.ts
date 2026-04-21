/**
 * EUI 组件库通用类型定义
 * 定义跨组件共享的基础类型：尺寸、通用选项、配置注入、菜单/表格/分页/表单规则等
 */
import type { HTMLAttributes } from 'vue'

/** 统一的尺寸枚举，用于按钮、输入框等所有需要尺寸的组件 */
export type Size = 'sm' | 'default' | 'lg'

/** 下拉/单选等列表型组件的标准选项 */
export interface Option {
  /** 显示文案 */
  label: string
  /** 选项值（支持字符串或数字） */
  value: string | number
  /** 是否禁用该选项 */
  disabled?: boolean
}

/** 带分组的选项结构，label 为分组标题 */
export interface GroupedOption {
  /** 分组标题 */
  label: string
  /** 当前分组下的选项列表 */
  options: Option[]
}

/** 所有组件共用的基础 props（允许传入 Tailwind class） */
export interface BaseProps {
  /** 自定义类名，透传到根元素 */
  class?: HTMLAttributes['class']
}

/** EConfigProvider 对外暴露的上下文结构 */
export interface ConfigProviderContext {
  /** 全局默认尺寸 */
  size: Size
  /** 全局弹层基础 z-index */
  zIndex: number
  /** 全局文案语言包 */
  locale: Record<string, string>
}

/** 菜单项定义，支持多级嵌套 */
export interface MenuItem {
  /** 唯一标识，默认也作为点击事件的 key */
  key: string
  /** 菜单文本 */
  label: string
  /** 图标名或 class（由使用方决定渲染方式） */
  icon?: string
  /** 路由模式下的跳转路径；未提供时回落到 key */
  path?: string
  /** 子菜单 */
  children?: MenuItem[]
  /** 是否禁用 */
  disabled?: boolean
}

/** 表格列定义 */
export interface TableColumn<T = any> {
  /** 对应行数据的字段名 */
  key: string
  /** 表头标题 */
  title: string
  /** 列宽，数字按 px，字符串可传 % 或 rem */
  width?: number | string
  /** 最小列宽（px），用于响应式/拉伸 */
  minWidth?: number
  /** 是否可排序 */
  sortable?: boolean
  /** 固定列位置 */
  fixed?: 'left' | 'right'
  /** 对齐方式 */
  align?: 'left' | 'center' | 'right'
  /** 自定义渲染函数，返回值用于列单元格内容 */
  render?: (row: T, index: number) => any
}

/** 分页状态（页码从 1 开始） */
export interface PaginationInfo {
  /** 当前页码 */
  page: number
  /** 每页条数 */
  pageSize: number
  /** 总记录数 */
  total: number
}

/** 表单校验规则，兼容 Element Plus 语义，便于项目迁移 */
export interface FormRule {
  /** 是否必填 */
  required?: boolean
  /** 校验失败时的提示文本 */
  message?: string
  /** 触发时机：失焦或值变化 */
  trigger?: 'blur' | 'change'
  /** 最小长度（字符串）或最小值（数字） */
  min?: number
  /** 最大长度（字符串）或最大值（数字） */
  max?: number
  /** 值类型标识，如 'email' / 'number' */
  type?: string
  /** 正则匹配 */
  pattern?: RegExp
  /** 自定义异步/同步校验器，调用 callback 返回结果 */
  validator?: (rule: FormRule, value: any, callback: (error?: Error) => void) => void
}
