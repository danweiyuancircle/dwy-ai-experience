/**
 * ENavigationMenu 导航菜单族组件类型定义
 */

/** 导航菜单根组件 Props */
export interface ENavigationMenuProps {
  /** 自定义类名 */
  class?: string
  /** 是否渲染 Viewport 共用展开区，默认 true */
  viewport?: boolean
}

/** 菜单项列表容器 Props */
export interface ENavigationMenuListProps {
  /** 自定义类名 */
  class?: string
}

/** 单个菜单项 Props */
export interface ENavigationMenuItemProps {
  /** 自定义类名 */
  class?: string
}

/** 菜单展开触发器 Props */
export interface ENavigationMenuTriggerProps {
  /** 自定义类名 */
  class?: string
  /** 是否禁用 */
  disabled?: boolean
}

/** 菜单展开内容 Props */
export interface ENavigationMenuContentProps {
  /** 自定义类名 */
  class?: string
}

/** 菜单链接 Props */
export interface ENavigationMenuLinkProps {
  /** 自定义类名 */
  class?: string
  /** 是否处于激活态（配合路由匹配使用） */
  active?: boolean
  /** 链接地址（asChild 模式下可省略） */
  href?: string
  /** 以子节点身份渲染，用于透传给 RouterLink 等 */
  asChild?: boolean
}

/** 菜单展开区域 Props */
export interface ENavigationMenuViewportProps {
  /** 自定义类名 */
  class?: string
}
