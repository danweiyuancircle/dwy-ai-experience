export interface AutocompleteOption {
  label: string
  value: string | number
}

export interface EAutocompleteProps {
  class?: string
  modelValue?: string
  fetchSuggestions?: (query: string) => Promise<AutocompleteOption[]>
  debounce?: number
  placeholder?: string
  disabled?: boolean
}

export interface EAutocompleteEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'select', option: AutocompleteOption): void
  (e: 'change', value: string): void
}
