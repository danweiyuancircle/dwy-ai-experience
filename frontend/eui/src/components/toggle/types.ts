/**
 * EToggle 开关按钮组件类型定义与样式变体
 * 使用 class-variance-authority 定义变体组合，便于外部按相同规则生成派生组件
 */
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'

/** 开关按钮的样式变体（variant + size） */
export const toggleVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium hover:bg-muted hover:text-muted-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=on]:bg-accent data-[state=on]:text-accent-foreground [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 [&_svg]:shrink-0 focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none transition-[color,box-shadow] whitespace-nowrap",
  {
    variants: {
      variant: {
        default: 'bg-transparent',
        outline: 'border border-input bg-transparent shadow-xs hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        default: 'h-9 px-2 min-w-9',
        sm: 'h-8 px-1.5 min-w-8',
        lg: 'h-10 px-2.5 min-w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

/** 开关按钮变体 props 类型 */
export type ToggleVariants = VariantProps<typeof toggleVariants>

/** EToggle Props */
export interface EToggleProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 按下状态，v-model 绑定 */
  modelValue?: boolean
  /** 视觉变体：default 无边框，outline 带边框 */
  variant?: ToggleVariants['variant']
  /** 尺寸变体 */
  size?: ToggleVariants['size']
  /** 是否禁用 */
  disabled?: boolean
}

/** EToggle Emits */
export interface EToggleEmits {
  /** 按下状态更新，用于 v-model */
  'update:modelValue': [value: boolean]
}
