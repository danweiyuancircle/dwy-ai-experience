/**
 * EMenu 侧边栏导航菜单组件的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { MenuItem } from '@/types'

/**
 * EMenu 侧边栏导航菜单 Props
 */
export interface EMenuProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** 菜单项数据源 */
  items?: MenuItem[]
  /** 当前激活的菜单 key */
  modelValue?: string
  /** 是否折叠（仅显示图标） */
  collapsed?: boolean
  /** 为 true 时点击菜单项会通过 vue-router 跳转（使用 item.path 或 item.key） */
  router?: boolean
  /** 为 true 时同一时间仅允许一个子菜单展开，展开新菜单会自动收起其他 */
  uniqueOpened?: boolean
  /** 挂载时默认展开的子菜单 key 列表 */
  defaultOpeneds?: string[]
}

/**
 * EMenu 侧边栏导航菜单事件
 */
export interface EMenuEmits {
  /** 激活菜单 key 变化 */
  'update:modelValue': [value: string]
  /** 菜单项选中时触发 */
  select: [key: string]
}
