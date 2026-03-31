export interface TimelineItem {
  title: string
  content?: string
  timestamp?: string
  type?: 'primary' | 'success' | 'warning' | 'danger'
}

export interface ETimelineProps {
  class?: string
  items?: TimelineItem[]
  reverse?: boolean
}
