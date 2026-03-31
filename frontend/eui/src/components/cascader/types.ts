import type { HTMLAttributes } from 'vue'

export interface CascaderOption {
  label: string
  value: string | number
  children?: CascaderOption[]
  disabled?: boolean
  isLeaf?: boolean
}

export interface ECascaderProps {
  class?: HTMLAttributes['class']
  modelValue?: (string | number)[] | (string | number)[][]
  options?: CascaderOption[]
  placeholder?: string
  disabled?: boolean
  clearable?: boolean
  filterable?: boolean
  /** When true, options with undefined children call loadFn on expand */
  lazy?: boolean
  /** Async function to load children for an option (used with lazy) */
  loadFn?: (option: CascaderOption) => Promise<CascaderOption[]>
  /** When true, multiple paths can be selected; modelValue becomes array of paths */
  multiple?: boolean
  /** When true and multiple, collapse selected tags to "+N" after the first */
  collapseTags?: boolean
}

export interface ECascaderEmits {
  (e: 'update:modelValue', value: (string | number)[] | (string | number)[][]): void
  (e: 'change', value: (string | number)[] | (string | number)[][]): void
}
