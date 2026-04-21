/**
 * EAlert 警告提示组件的类型定义
 * 使用 CVA 声明 variant 样式变体
 */
import type { VariantProps } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'
import { cva } from 'class-variance-authority'

/**
 * EAlert 样式变体配置
 * default=常规提示，destructive=危险/错误提示
 */
export const alertVariants = cva(
  'relative w-full rounded-lg border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current',
  {
    variants: {
      variant: {
        default: 'bg-card text-card-foreground',
        destructive:
          'text-destructive bg-card [&>svg]:text-current *:data-[slot=alert-description]:text-destructive/90',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

/** CVA 派生的 variant props 类型 */
export type AlertVariants = VariantProps<typeof alertVariants>

/**
 * EAlert 警告提示 Props
 */
export interface EAlertProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 样式变体（default / destructive） */
  variant?: AlertVariants['variant']
  /** 标题文本，也可通过 title 具名插槽覆盖 */
  title?: string
  /** 描述文本，也可通过默认插槽覆盖 */
  description?: string
  /** 是否显示右上角关闭按钮 */
  closable?: boolean
}

/**
 * EAlert 警告提示事件
 */
export interface EAlertEmits {
  /** 关闭按钮点击时触发（组件本身不隐藏，由调用方控制显隐） */
  close: []
}
