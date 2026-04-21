<!--
  EFormItem 表单字段组件
  绑定 prop 字段到 vee-validate useField，与外部 model 做双向同步
  通过 provide FORM_ITEM_INJECTION_KEY 让子控件（如 EInput）感知所属 FormItem id
-->
<script setup lang="ts">
import { inject, computed, provide, watch } from 'vue'
import { useId } from 'reka-ui'
import { useField } from 'vee-validate'
import { cn } from '@/utils/cn'
import { FORM_ITEM_INJECTION_KEY } from '@/composables'
import { FORM_CONTEXT_KEY } from './context'
import type { EFormItemProps } from './types'

const props = defineProps<EFormItemProps>()

const formContext = inject(FORM_CONTEXT_KEY, undefined)

const id = useId()
// 向子控件暴露 FormItem id，便于 aria-describedby 关联
provide(FORM_ITEM_INJECTION_KEY, id)

// 优先使用 FormItem 自身 labelWidth，否则回退到 EForm 的 labelWidth
const resolvedLabelWidth = computed(() => {
  return props.labelWidth ?? formContext?.labelWidth?.value
})

const labelPosition = computed(() => {
  return formContext?.labelPosition?.value ?? 'right'
})

const isTopLabel = computed(() => labelPosition.value === 'top')

// 通过 vee-validate 注册字段，让 schema 校验能命中本字段
const fieldState = props.prop
  ? useField(() => props.prop!, undefined, {
      syncVModel: false,
      initialValue: formContext?.model?.value?.[props.prop!],
    })
  : null

// model ↔ fieldState 双向同步：保证外部 v-model 与 vee-validate 值一致
if (fieldState && formContext?.model) {
  // model → field
  watch(
    () => formContext.model?.value?.[props.prop!],
    (newVal) => {
      if (fieldState.value.value !== newVal) {
        fieldState.value.value = newVal
      }
    },
  )
  // field → model（用于 resetForm 时回写）
  watch(
    () => fieldState.value.value,
    (newVal) => {
      if (formContext.model?.value && formContext.model.value[props.prop!] !== newVal) {
        formContext.model.value[props.prop!] = newVal
      }
    },
  )
}

const errorMessage = computed(() => fieldState?.errorMessage?.value)
</script>

<template>
  <div
    data-slot="form-item"
    :class="cn(
      'grid gap-2',
      !isTopLabel && 'grid-cols-[auto_1fr] items-start',
      props.class,
    )"
  >
    <!-- Label -->
    <label
      v-if="label"
      data-slot="form-label"
      :data-error="!!errorMessage"
      :for="`${id}-form-item`"
      :class="cn(
        'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
        'data-[error=true]:text-destructive',
        !isTopLabel && 'flex h-9 items-center',
        labelPosition === 'right' && !isTopLabel && 'text-right',
      )"
      :style="resolvedLabelWidth ? { width: resolvedLabelWidth, minWidth: resolvedLabelWidth } : undefined"
    >
      <span v-if="required" class="text-destructive mr-1">*</span>
      {{ label }}
    </label>

    <!-- Empty cell for grid when no label -->
    <div v-if="!label && !isTopLabel" />

    <!-- Control + error -->
    <div>
      <div
        :id="`${id}-form-item`"
        :class="cn(!isTopLabel && 'min-h-9 flex items-center w-full [&>*]:w-full')"
        :aria-invalid="!!errorMessage"
        :aria-describedby="errorMessage ? `${id}-form-item-message` : undefined"
      >
        <slot />
      </div>
      <p
        v-if="errorMessage"
        :id="`${id}-form-item-message`"
        data-slot="form-message"
        :class="cn('text-destructive text-sm mt-1')"
      >
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>
