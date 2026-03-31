export interface EInfiniteScrollProps {
  class?: string
  loading?: boolean
  disabled?: boolean
  distance?: number
}

export interface EInfiniteScrollEmits {
  (e: 'load'): void
}
