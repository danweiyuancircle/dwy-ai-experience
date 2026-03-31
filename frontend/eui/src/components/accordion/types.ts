import type { HTMLAttributes } from 'vue'

export interface AccordionItemOption {
  key: string
  title: string
  disabled?: boolean
}

export interface EAccordionProps {
  class?: HTMLAttributes['class']
  modelValue?: string | string[]
  items?: AccordionItemOption[]
  multiple?: boolean
  collapsible?: boolean
}

export interface EAccordionEmits {
  (e: 'update:modelValue', value: string | string[] | undefined): void
}
