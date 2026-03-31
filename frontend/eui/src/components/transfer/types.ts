export interface TransferItem {
  label: string
  value: string | number
  disabled?: boolean
}

export interface ETransferProps {
  class?: string
  modelValue?: (string | number)[]
  data?: TransferItem[]
  filterable?: boolean
  titles?: [string, string]
}

export interface ETransferEmits {
  (e: 'update:modelValue', value: (string | number)[]): void
  (e: 'change', value: (string | number)[], direction: 'right' | 'left', moved: (string | number)[]): void
}
