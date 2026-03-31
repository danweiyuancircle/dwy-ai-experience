import type { HTMLAttributes } from 'vue'

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: any
}

export interface EBreadcrumbProps {
  class?: HTMLAttributes['class']
  items?: BreadcrumbItem[]
  separator?: string
}
