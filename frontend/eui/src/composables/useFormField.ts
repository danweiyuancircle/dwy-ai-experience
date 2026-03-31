import { FieldContextKey } from 'vee-validate'
import { computed, inject } from 'vue'
import type { InjectionKey } from 'vue'

export const FORM_ITEM_INJECTION_KEY = Symbol() as InjectionKey<string>

export function useFormField() {
  const fieldContext = inject(FieldContextKey)
  const fieldItemContext = inject(FORM_ITEM_INJECTION_KEY)

  if (!fieldContext)
    throw new Error('useFormField should be used within <FormField>')

  const { name, errorMessage: error, meta } = fieldContext
  const id = fieldItemContext

  return {
    id,
    name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    valid: computed(() => meta.valid),
    isDirty: computed(() => meta.dirty),
    isTouched: computed(() => meta.touched),
    error,
  }
}
