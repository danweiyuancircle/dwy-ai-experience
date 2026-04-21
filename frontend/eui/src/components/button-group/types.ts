/**
 * EButtonGroup 按钮组组件的类型定义
 */
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'

/**
 * EButtonGroup 样式变体配置
 * 通过 orientation 控制水平/垂直排列，并消除相邻按钮的圆角和边框
 */
export const buttonGroupVariants = cva(
  'flex w-fit items-stretch [&>*]:focus-visible:z-10 [&>*]:focus-visible:relative',
  {
    variants: {
      orientation: {
        horizontal:
          '[&>*:not(:first-child)]:rounded-l-none [&>*:not(:first-child)]:border-l-0 [&>*:not(:last-child)]:rounded-r-none',
        vertical:
          'flex-col [&>*:not(:first-child)]:rounded-t-none [&>*:not(:first-child)]:border-t-0 [&>*:not(:last-child)]:rounded-b-none',
      },
    },
    defaultVariants: {
      orientation: 'horizontal',
    },
  },
)

/** CVA 派生的 variant props 类型 */
export type ButtonGroupVariants = VariantProps<typeof buttonGroupVariants>

/**
 * EButtonGroup 按钮组 Props
 */
export interface EButtonGroupProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 排列方向：horizontal=水平，vertical=垂直 */
  orientation?: ButtonGroupVariants['orientation']
}
