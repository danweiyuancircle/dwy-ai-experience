import type { HTMLAttributes } from 'vue'
import type { Size, Option, GroupedOption } from '@/types'

export interface ESelectProps {
  class?: HTMLAttributes['class']
  modelValue?: string | number | (string | number)[]
  options?: Option[] | GroupedOption[]
  placeholder?: string
  disabled?: boolean
  size?: Size
  clearable?: boolean
  valueKey?: string
  labelKey?: string
  /** When true, show a search input in the dropdown to filter options by label */
  filterable?: boolean
  /** When true, allow selecting multiple options (modelValue becomes an array) */
  multiple?: boolean
  /** When true and multiple is enabled, show first tag + "+N" instead of all tags */
  collapseTags?: boolean
  /** When true (with filterable), skip local filtering and call remoteMethod instead */
  remote?: boolean
  /** Called with the search query when remote is true; caller should update options externally */
  remoteMethod?: (query: string) => Promise<void>
  /** When true, show a loading spinner in the dropdown (used with remote mode) */
  loading?: boolean
}

export interface ESelectEmits {
  'update:modelValue': [value: string | number | (string | number)[] | undefined]
  change: [value: string | number | (string | number)[] | undefined]
  'visible-change': [visible: boolean]
}
