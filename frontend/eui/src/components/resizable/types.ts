export interface EResizablePanelGroupProps {
  class?: string
  direction?: 'horizontal' | 'vertical'
  id?: string
}

export interface EResizablePanelProps {
  defaultSize?: number
  minSize?: number
  maxSize?: number
  id?: string
}

export interface EResizableHandleProps {
  class?: string
  withHandle?: boolean
  id?: string
}
