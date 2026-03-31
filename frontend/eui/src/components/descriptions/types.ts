export interface DescriptionItem {
  label: string
  value?: string | number
  span?: number
}

export interface EDescriptionsProps {
  class?: string
  items?: DescriptionItem[]
  columns?: number
  bordered?: boolean
  title?: string
}
