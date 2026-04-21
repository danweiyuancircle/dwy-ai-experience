/**
 * EButton 按钮组件的类型定义
 * 使用 CVA 管理 variant / size 组合样式
 */
import type { VariantProps } from 'class-variance-authority'
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { cva } from 'class-variance-authority'

/**
 * EButton 样式变体配置
 * variant: default / destructive / outline / secondary / ghost / link
 * size: default / sm / lg / icon / icon-sm / icon-lg
 */
export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60',
        outline:
          'border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-9 px-4 py-2 has-[>svg]:px-3',
        sm: 'h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5',
        lg: 'h-10 rounded-md px-6 has-[>svg]:px-4',
        icon: 'size-9',
        'icon-sm': 'size-8',
        'icon-lg': 'size-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

/** CVA 派生的 variant/size props 类型 */
export type ButtonVariants = VariantProps<typeof buttonVariants>

/**
 * EButton 按钮 Props（继承 reka-ui Primitive 的 as / asChild 能力）
 */
export interface EButtonProps extends PrimitiveProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 样式变体 */
  variant?: ButtonVariants['variant']
  /** 尺寸 */
  size?: ButtonVariants['size']
  /** 是否禁用 */
  disabled?: boolean
  /** 是否处于加载中：会显示 spinner 并禁用点击 */
  loading?: boolean
}
