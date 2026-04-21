/**
 * ETypography 排版组件类型定义与样式映射
 */
import type { HTMLAttributes } from 'vue'

/** 排版变体：标题层级 h1-h4、段落 p、大段导语 lead、大号 large、小号 small、弱化 muted */
export type TypographyVariant = 'h1' | 'h2' | 'h3' | 'h4' | 'p' | 'lead' | 'large' | 'small' | 'muted'

/** ETypography Props */
export interface ETypographyProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 排版变体；默认 p */
  variant?: TypographyVariant
  /** 自定义渲染标签名，覆盖变体默认标签（用于调整语义） */
  as?: string
}

/** 每种变体对应的 Tailwind class */
export const typographyVariantClasses: Record<TypographyVariant, string> = {
  h1: 'scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl',
  h2: 'scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight first:mt-0',
  h3: 'scroll-m-20 text-2xl font-semibold tracking-tight',
  h4: 'scroll-m-20 text-xl font-semibold tracking-tight',
  p: 'leading-7 [&:not(:first-child)]:mt-6',
  lead: 'text-xl text-muted-foreground',
  large: 'text-lg font-semibold',
  small: 'text-sm font-medium leading-none',
  muted: 'text-sm text-muted-foreground',
}

/** 每种变体对应的默认 HTML 标签 */
export const typographyVariantElements: Record<TypographyVariant, string> = {
  h1: 'h1',
  h2: 'h2',
  h3: 'h3',
  h4: 'h4',
  p: 'p',
  lead: 'p',
  large: 'div',
  small: 'small',
  muted: 'p',
}
