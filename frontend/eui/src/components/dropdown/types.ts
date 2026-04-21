/**
 * EDropdown 下拉菜单组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * 下拉菜单项配置
 */
export interface DropdownMenuItem {
  /** 唯一 key，select 事件参数 */
  key: string
  /** 显示文本 */
  label: string
  /** 前置图标组件 */
  // 图标组件无统一类型约束
  icon?: any
  /** 是否禁用 */
  disabled?: boolean
  /** 是否在该项前绘制一条分隔线 */
  divided?: boolean
  /** 样式变体：destructive 用于危险操作 */
  variant?: 'default' | 'destructive'
  /** 子菜单项，有则渲染为 submenu */
  children?: DropdownMenuItem[]
}

/**
 * EDropdown 下拉菜单 Props
 */
export interface EDropdownProps {
  /** 自定义 class，透传到内容区 */
  class?: HTMLAttributes['class']
  /** 菜单项数据源 */
  items?: DropdownMenuItem[]
  /** 菜单相对触发器的位置 */
  side?: 'top' | 'right' | 'bottom' | 'left'
  /** 菜单对齐方式 */
  align?: 'start' | 'center' | 'end'
  /** 菜单与触发器的间距（px） */
  sideOffset?: number
  /** 触发方式：click 点击；hover 悬浮 */
  trigger?: 'click' | 'hover'
  /** 是否渲染为分割按钮（主按钮 + 箭头按钮） */
  splitButton?: boolean
  /** 分割按钮模式下主按钮的文本 */
  buttonText?: string
  /** 分割按钮模式下按钮的样式变体 */
  buttonVariant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
}

/**
 * EDropdown 下拉菜单事件
 */
export interface EDropdownEmits {
  /** 菜单项选中时触发，参数为 item.key */
  (e: 'select', key: string): void
  /** 分割按钮的主按钮点击时触发 */
  (e: 'click'): void
}
