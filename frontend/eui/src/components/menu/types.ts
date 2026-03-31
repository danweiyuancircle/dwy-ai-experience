import type { HTMLAttributes } from 'vue'
import type { MenuItem } from '@/types'

export interface EMenuProps {
  class?: HTMLAttributes['class']
  items?: MenuItem[]
  modelValue?: string
  collapsed?: boolean
}

export interface EMenuEmits {
  'update:modelValue': [value: string]
  select: [key: string]
}
