import type { InjectionKey, Ref } from 'vue'

export interface FormContext {
  labelWidth?: Ref<string | undefined>
  labelPosition: Ref<'left' | 'right' | 'top'>
  size: Ref<string>
  disabled: Ref<boolean>
  model: Ref<Record<string, any> | undefined>
}

export const FORM_CONTEXT_KEY = Symbol() as InjectionKey<FormContext>
