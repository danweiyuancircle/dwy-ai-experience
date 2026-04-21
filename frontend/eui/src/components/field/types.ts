/**
 * EField 表单字段容器组件的类型定义
 */
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'
import type { HTMLAttributes } from 'vue'

/**
 * EField 样式变体配置
 * 根据 orientation 控制子项的纵向/横向排列
 */
export const fieldVariants = cva(
  'group/field flex w-full gap-3 data-[invalid=true]:text-destructive',
  {
    variants: {
      orientation: {
        vertical: 'flex-col [&>*]:w-full [&>.sr-only]:w-auto',
        horizontal: 'flex-row items-center [&>[data-slot=field-label]]:flex-auto',
        responsive: 'flex-col [&>*]:w-full [&>.sr-only]:w-auto',
      },
    },
    defaultVariants: {
      orientation: 'vertical',
    },
  },
)

/** CVA 派生的 variant props 类型 */
export type FieldVariants = VariantProps<typeof fieldVariants>

/**
 * EField 表单字段容器 Props
 */
export interface EFieldProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 子项排列方向 */
  orientation?: FieldVariants['orientation']
  /** 是否处于校验失败态（会触发红色样式） */
  invalid?: boolean
}
