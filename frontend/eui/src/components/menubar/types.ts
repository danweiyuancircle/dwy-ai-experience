export interface EMenubarProps {
  class?: string
}

export interface EMenubarMenuProps {
  value?: string
}

export interface EMenubarTriggerProps {
  class?: string
  disabled?: boolean
}

export interface EMenubarContentProps {
  class?: string
  align?: 'start' | 'center' | 'end'
  alignOffset?: number
  sideOffset?: number
}

export interface EMenubarItemProps {
  class?: string
  inset?: boolean
  disabled?: boolean
  variant?: 'default' | 'destructive'
}

export interface EMenubarSeparatorProps {
  class?: string
}

export interface EMenubarCheckboxItemProps {
  class?: string
  checked?: boolean
  disabled?: boolean
}

export interface EMenubarRadioGroupProps {
  class?: string
  modelValue?: string
}

export interface EMenubarRadioItemProps {
  class?: string
  value: string
  disabled?: boolean
}

export interface EMenubarSubTriggerProps {
  class?: string
  inset?: boolean
  disabled?: boolean
}

export interface EMenubarSubContentProps {
  class?: string
}
