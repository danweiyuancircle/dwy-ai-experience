export interface ERangeCalendarProps {
  class?: string
  modelValue?: { start: any; end: any }
  defaultValue?: { start: any; end: any }
  disabled?: boolean
  readonly?: boolean
  locale?: string
  minValue?: any
  maxValue?: any
}

export interface ERangeCalendarEmits {
  (e: 'update:modelValue', value: { start: any; end: any } | null): void
}
