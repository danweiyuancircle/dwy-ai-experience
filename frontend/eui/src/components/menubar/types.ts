/**
 * EMenubar 顶部菜单栏组件族的类型定义
 * 每个子组件对应一个独立的 Props 接口
 */

/** 菜单栏根容器 Props */
export interface EMenubarProps {
  /** 自定义 class */
  class?: string
}

/** 单个菜单项 Props（包裹 trigger + content 的组合） */
export interface EMenubarMenuProps {
  /** 菜单值，用于受控状态下标识当前激活项 */
  value?: string
}

/** 菜单触发器 Props */
export interface EMenubarTriggerProps {
  class?: string
  /** 是否禁用 */
  disabled?: boolean
}

/** 菜单内容面板 Props */
export interface EMenubarContentProps {
  class?: string
  /** 对齐方式 */
  align?: 'start' | 'center' | 'end'
  /** 沿对齐轴的偏移量 */
  alignOffset?: number
  /** 相对触发器的垂直偏移 */
  sideOffset?: number
}

/** 普通菜单项 Props */
export interface EMenubarItemProps {
  class?: string
  /** 是否缩进以对齐 checkbox/radio 项 */
  inset?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 样式变体：destructive 用于危险操作 */
  variant?: 'default' | 'destructive'
}

/** 分隔线 Props */
export interface EMenubarSeparatorProps {
  class?: string
}

/** 复选菜单项 Props */
export interface EMenubarCheckboxItemProps {
  class?: string
  /** 是否勾选 */
  checked?: boolean
  /** 是否禁用 */
  disabled?: boolean
}

/** 单选组 Props */
export interface EMenubarRadioGroupProps {
  class?: string
  /** 当前选中值 */
  modelValue?: string
}

/** 单选项 Props */
export interface EMenubarRadioItemProps {
  class?: string
  /** 该选项的值 */
  value: string
  /** 是否禁用 */
  disabled?: boolean
}

/** 子菜单触发器 Props */
export interface EMenubarSubTriggerProps {
  class?: string
  /** 是否缩进 */
  inset?: boolean
  /** 是否禁用 */
  disabled?: boolean
}

/** 子菜单内容面板 Props */
export interface EMenubarSubContentProps {
  class?: string
}
