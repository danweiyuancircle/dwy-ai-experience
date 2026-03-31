import type { HTMLAttributes } from 'vue'

export interface TimetableItem {
  day: number
  startHour: number
  endHour: number
  title: string
  color?: string
}

export interface ETimetableGridProps {
  class?: HTMLAttributes['class']
  data?: TimetableItem[]
  startHour?: number
  endHour?: number
  days?: string[]
}
