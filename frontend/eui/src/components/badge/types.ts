/**
 * EBadge 徽标组件的类型定义
 */
import type { VariantProps } from 'class-variance-authority'
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { cva } from 'class-variance-authority'

/**
 * EBadge 样式变体配置
 * default / secondary / destructive / outline 四种风格
 */
export const badgeVariants = cva(
  'inline-flex items-center justify-center rounded-full border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90',
        secondary:
          'border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90',
        destructive:
          'border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60',
        outline: 'text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

/** CVA 派生的 variant props 类型 */
export type BadgeVariants = VariantProps<typeof badgeVariants>

/**
 * EBadge 徽标 Props（继承 reka-ui Primitive 的 as / asChild 等能力）
 */
export interface EBadgeProps extends PrimitiveProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 样式变体 */
  variant?: BadgeVariants['variant']
}
