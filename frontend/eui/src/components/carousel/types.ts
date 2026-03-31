import type { HTMLAttributes } from 'vue'

export interface ECarouselProps {
  class?: HTMLAttributes['class']
  loop?: boolean
  direction?: 'horizontal' | 'vertical'
  showArrows?: boolean
  showDots?: boolean
  autoplay?: boolean
  interval?: number
}

export interface ECarouselEmits {
  (e: 'change', index: number): void
}
