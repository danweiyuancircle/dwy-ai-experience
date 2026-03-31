export interface ECalendarProps {
  class?: string
  modelValue?: any
  defaultValue?: any
  multiple?: boolean
  disabled?: boolean
  readonly?: boolean
  locale?: string
  minValue?: any
  maxValue?: any
}

export interface ECalendarEmits {
  (e: 'update:modelValue', value: any): void
}
