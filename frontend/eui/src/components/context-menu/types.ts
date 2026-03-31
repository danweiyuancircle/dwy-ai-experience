import type { Component } from 'vue'

export interface ContextMenuItem {
  key: string
  label: string
  icon?: Component
  disabled?: boolean
  divided?: boolean
  variant?: 'default' | 'destructive'
  children?: ContextMenuItem[]
}

export interface EContextMenuProps {
  class?: string
  items?: ContextMenuItem[]
}

export interface EContextMenuEmits {
  (e: 'select', key: string): void
}
