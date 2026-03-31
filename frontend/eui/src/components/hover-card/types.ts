export interface EHoverCardProps {
  class?: string
  openDelay?: number
  closeDelay?: number
}

export interface EHoverCardEmits {
  (e: 'update:open', open: boolean): void
}
