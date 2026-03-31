<script setup lang="ts">
import { provide, computed, toRef } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { cn } from '@/utils/cn'
import { FORM_CONTEXT_KEY } from './context'
import type { EFormProps, EFormEmits, EFormExpose } from './types'
import type { ZodType } from 'zod'

const props = withDefaults(defineProps<EFormProps>(), {
  labelPosition: 'right',
  size: 'default',
  disabled: false,
})

const emit = defineEmits<EFormEmits>()

const isZodSchema = computed(() => {
  if (!props.rules) return false
  return typeof (props.rules as ZodType)._def !== 'undefined'
})

const validationSchema = computed(() => {
  if (!props.rules) return undefined
  if (isZodSchema.value) {
    return toTypedSchema(props.rules as ZodType)
  }
  return undefined
})

const { handleSubmit, resetForm, setErrors, validate: veeValidate } = useForm({
  validationSchema: validationSchema.value,
  initialValues: props.model,
})

const onSubmit = handleSubmit((values) => {
  emit('submit', values)
})

async function validate(): Promise<boolean> {
  const result = await veeValidate()
  return result.valid
}

function resetFields() {
  resetForm({ values: props.model })
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
  resetFields,
  clearValidate,
})
</script>

<template>
  <form
    data-slot="form"
    :class="cn('space-y-4', props.class)"
    @submit.prevent="onSubmit"
  >
    <slot />
  </form>
</template>
