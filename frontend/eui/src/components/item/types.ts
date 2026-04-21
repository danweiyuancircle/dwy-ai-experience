/**
 * EItem 列表项通用容器组件的类型定义
 */
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'

/**
 * EItem 样式变体配置
 * variant: default / outline / muted；size: default / sm
 */
export const itemVariants = cva(
  'group/item flex items-center border border-transparent text-sm rounded-md transition-colors flex-wrap outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
  {
    variants: {
      variant: {
        default: 'bg-transparent',
        outline: 'border-border',
        muted: 'bg-muted/50',
      },
      size: {
        default: 'p-4 gap-4',
        sm: 'py-3 px-4 gap-2.5',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

/** CVA 派生的 variant/size 类型 */
export type ItemVariants = VariantProps<typeof itemVariants>

/**
 * EItem 列表项 Props
 */
export interface EItemProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** 样式变体 */
  variant?: ItemVariants['variant']
  /** 尺寸 */
  size?: ItemVariants['size']
  /** 渲染的 HTML 标签，默认 div */
  as?: string
}
