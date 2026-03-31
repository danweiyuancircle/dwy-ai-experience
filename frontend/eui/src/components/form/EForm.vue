<script setup lang="ts">
import { provide, computed, toRef } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { cn } from '@/utils/cn'
import { FORM_CONTEXT_KEY } from './context'
import type { EFormProps, EFormEmits, EFormExpose } from './types'
import type { FormRule } from '@/types'
import type { ZodType } from 'zod'

const props = withDefaults(defineProps<EFormProps>(), {
  labelPosition: 'right',
  size: 'default',
  disabled: false,
  inline: false,
})

const emit = defineEmits<EFormEmits>()

const isZodSchema = computed(() => {
  if (!props.rules) return false
  return typeof (props.rules as ZodType)._def !== 'undefined'
})

/**
 * Convert a single FormRule to a validation function for vee-validate.
 */
function ruleToValidator(rule: FormRule) {
  return (value: any) => {
    if (rule.required && (value === undefined || value === null || value === '')) {
      return rule.message || '此字段为必填项'
    }
    if (typeof value === 'string') {
      if (rule.min !== undefined && value.length < rule.min) {
        return rule.message || `最少 ${rule.min} 个字符`
      }
      if (rule.max !== undefined && value.length > rule.max) {
        return rule.message || `最多 ${rule.max} 个字符`
      }
    }
    if (rule.type === 'email' && value) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return rule.message || '请输入有效的邮箱地址'
      }
    }
    if (rule.pattern && value && !rule.pattern.test(value)) {
      return rule.message || '格式不正确'
    }
    if (rule.validator) {
      let error: string | undefined
      rule.validator(rule, value, (err?: Error) => {
        if (err) error = err.message
      })
      if (error) return error
    }
    return true
  }
}

/**
 * Build a vee-validate compatible validation schema from plain rules object.
 */
function buildPlainSchema(rules: Record<string, FormRule | FormRule[]>) {
  const schema: Record<string, (value: any) => string | true> = {}
  for (const [field, fieldRules] of Object.entries(rules)) {
    const ruleArray = Array.isArray(fieldRules) ? fieldRules : [fieldRules]
    const validators = ruleArray.map(ruleToValidator)
    schema[field] = (value: any) => {
      for (const v of validators) {
        const result = v(value)
        if (result !== true) return result
      }
      return true
    }
  }
  return schema
}

const validationSchema = computed(() => {
  if (!props.rules) return undefined
  if (isZodSchema.value) {
    return toTypedSchema(props.rules as ZodType)
  }
  // Plain rules object — build field-level validators
  return buildPlainSchema(props.rules as Record<string, FormRule | FormRule[]>)
})

// Deep clone initial values so reset works correctly
const initialSnapshot = JSON.parse(JSON.stringify(props.model ?? {}))

const { handleSubmit, resetForm, setErrors, validate: veeValidate, validateField: veeValidateField, setFieldValue } = useForm({
  validationSchema,
  initialValues: initialSnapshot,
})

const onSubmit = handleSubmit((values) => {
  emit('submit', values)
})

async function validate(): Promise<boolean> {
  const result = await veeValidate()
  return result.valid
}

async function validateField(name: string): Promise<boolean> {
  const result = await veeValidateField(name)
  return result.valid
}

function resetFields() {
  resetForm({ values: JSON.parse(JSON.stringify(initialSnapshot)) })
  // Sync reactive model back to initial values
  if (props.model) {
    for (const key of Object.keys(initialSnapshot)) {
      props.model[key] = initialSnapshot[key]
    }
  }
}

function clearValidate() {
  setErrors({})
}

provide(FORM_CONTEXT_KEY, {
  labelWidth: toRef(() => props.labelWidth),
  labelPosition: toRef(() => props.labelPosition),
  size: toRef(() => props.size),
  disabled: toRef(() => props.disabled),
  model: toRef(() => props.model),
})

defineExpose<EFormExpose>({
  validate,
  validateField,
  resetFields,
  clearValidate,
})
</script>

<template>
  <form
    data-slot="form"
    :class="cn(
      props.inline ? 'flex flex-wrap gap-4 items-start' : 'space-y-4',
      props.class,
    )"
    @submit.prevent="onSubmit"
  >
    <slot />
  </form>
</template>
