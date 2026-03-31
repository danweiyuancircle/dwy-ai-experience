import type { HTMLAttributes } from 'vue'

export interface DropdownMenuItem {
  key: string
  label: string
  icon?: any
  disabled?: boolean
  divided?: boolean
  variant?: 'default' | 'destructive'
  children?: DropdownMenuItem[]
}

export interface EDropdownProps {
  class?: HTMLAttributes['class']
  items?: DropdownMenuItem[]
  side?: 'top' | 'right' | 'bottom' | 'left'
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
  trigger?: 'click' | 'hover'
  splitButton?: boolean
  buttonText?: string
  buttonVariant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
}

export interface EDropdownEmits {
  (e: 'select', key: string): void
  (e: 'click'): void
}
