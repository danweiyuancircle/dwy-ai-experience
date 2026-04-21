/**
 * EInputGroup 输入框组合组件的类型定义
 */
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'

/**
 * EInputGroupAddon 对齐位置样式变体
 * inline-* 为水平内联（左/右），block-* 为上下分块
 */
export const inputGroupAddonVariants = cva(
  "text-muted-foreground flex h-auto cursor-text items-center justify-center gap-2 py-1.5 text-sm font-medium select-none [&>svg:not([class*='size-'])]:size-4",
  {
    variants: {
      align: {
        'inline-start': 'order-first pl-3',
        'inline-end': 'order-last pr-3',
        'block-start': 'order-first w-full justify-start px-3 pt-3',
        'block-end': 'order-last w-full justify-start px-3 pb-3',
      },
    },
    defaultVariants: {
      align: 'inline-start',
    },
  },
)

/** CVA 派生的 align variant 类型 */
export type InputGroupVariants = VariantProps<typeof inputGroupAddonVariants>

/**
 * EInputGroup 输入框组合容器 Props
 */
export interface EInputGroupProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
}

/**
 * EInputGroupAddon 附加块 Props
 */
export interface EInputGroupAddonProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** 对齐位置（内联前/后、块前/后） */
  align?: InputGroupVariants['align']
}
