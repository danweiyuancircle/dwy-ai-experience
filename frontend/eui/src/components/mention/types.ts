export interface MentionOption {
  label: string
  value: string
}

export interface EMentionProps {
  class?: string
  modelValue?: string
  options?: MentionOption[]
  prefix?: string
  loading?: boolean
  placeholder?: string
  disabled?: boolean
}

export interface EMentionEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'select', option: MentionOption): void
}
