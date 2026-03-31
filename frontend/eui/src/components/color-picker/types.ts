export interface EColorPickerProps {
  class?: string
  modelValue?: string
  presets?: string[]
  showAlpha?: boolean
  disabled?: boolean
}

export interface EColorPickerEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}
