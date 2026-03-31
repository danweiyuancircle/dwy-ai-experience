import type { HTMLAttributes } from 'vue'

export type DatePickerType = 'date' | 'daterange' | 'month' | 'year'

export interface DatePickerShortcut {
  text: string
  value: Date | Date[] | (() => Date | Date[])
}

export interface EDatePickerProps {
  class?: HTMLAttributes['class']
  modelValue?: string | Date | [string, string] | [Date, Date]
  type?: DatePickerType
  placeholder?: string
  startPlaceholder?: string
  endPlaceholder?: string
  rangeSeparator?: string
  format?: string
  disabled?: boolean
  clearable?: boolean
  disabledDate?: (date: Date) => boolean
  shortcuts?: DatePickerShortcut[]
}

export interface EDatePickerEmits {
  (e: 'update:modelValue', value: string | [string, string] | undefined): void
  (e: 'change', value: string | [string, string] | undefined): void
}
