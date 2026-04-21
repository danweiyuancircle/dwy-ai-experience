/**
 * EContextMenu 右键菜单组件的类型定义
 */
import type { Component } from 'vue'

/**
 * 右键菜单项配置
 */
export interface ContextMenuItem {
  /** 唯一标识，select 事件参数 */
  key: string
  /** 菜单项显示文本 */
  label: string
  /** 菜单项前置图标组件 */
  icon?: Component
  /** 是否禁用 */
  disabled?: boolean
  /** 是否在该项前绘制一条分隔线 */
  divided?: boolean
  /** 样式变体：destructive 表示危险操作（红色） */
  variant?: 'default' | 'destructive'
  /** 子菜单项，有则渲染为 submenu */
  children?: ContextMenuItem[]
}

/**
 * EContextMenu 右键菜单 Props
 */
export interface EContextMenuProps {
  /** 自定义 class，透传到内容区 */
  class?: string
  /** 菜单项数据源 */
  items?: ContextMenuItem[]
}

/**
 * EContextMenu 右键菜单事件
 */
export interface EContextMenuEmits {
  /** 点击菜单项时触发，参数为 item.key */
  (e: 'select', key: string): void
}
