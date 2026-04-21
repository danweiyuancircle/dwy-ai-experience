/**
 * ETabs 标签页组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 标签位置 */
export type TabPosition = 'top' | 'bottom' | 'left' | 'right'

/** 单个标签项 */
export interface TabItem {
  /** 唯一标识，作为激活值 */
  key: string
  /** 标签文字 */
  label: string
  /** 是否禁用 */
  disabled?: boolean
}

/** ETabs Props */
export interface ETabsProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前激活的 tab key，v-model 绑定 */
  modelValue?: string
  /** 标签项列表 */
  items?: TabItem[]
  /** 是否在非禁用标签上显示关闭按钮 */
  closable?: boolean
  /** 是否在标签列表末尾显示 + 新增按钮 */
  addable?: boolean
  /** 标签位置：top/bottom/left/right，默认 top */
  tabPosition?: TabPosition
}

/** ETabs Emits */
export interface ETabsEmits {
  /** 激活 tab 更新，用于 v-model */
  (e: 'update:modelValue', key: string): void
  /** 激活 tab 变化事件 */
  (e: 'change', key: string): void
  /** 点击关闭按钮时触发，参数为被关闭的 tab key */
  (e: 'close', key: string): void
  /** 点击新增按钮时触发 */
  (e: 'add'): void
}
