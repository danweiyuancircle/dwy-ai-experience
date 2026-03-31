<script setup lang="ts">
import { computed } from 'vue'
import { Check, Minus } from 'lucide-vue-next'
import { CheckboxRoot, CheckboxIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECheckboxProps, ECheckboxEmits } from './types'

const props = withDefaults(defineProps<ECheckboxProps>(), {
  disabled: false,
  indeterminate: false,
  direction: 'horizontal',
  border: false,
})

const emit = defineEmits<ECheckboxEmits>()

/** Whether the component is in group mode (options provided) */
const isGroup = computed(() => Array.isArray(props.options) && props.options.length > 0)

/** Selected values array for group mode */
const selectedValues = computed(() => {
  if (!isGroup.value) return []
  return Array.isArray(props.modelValue) ? props.modelValue : []
})

/** Single checkbox checked state */
const checked = computed(() => {
  if (isGroup.value) return false
  if (props.indeterminate) return 'indeterminate'
  return (props.modelValue as boolean) ?? false
})

function onUpdate(value: boolean | 'indeterminate') {
  const boolValue = value === 'indeterminate' ? false : value
  emit('update:modelValue', boolValue)
  emit('change', boolValue)
}

function isOptionChecked(optionValue: string | number): boolean {
  return selectedValues.value.includes(optionValue)
}

function onGroupItemUpdate(optionValue: string | number, checked: boolean | 'indeterminate') {
  const isChecked = checked === 'indeterminate' ? false : checked
  const current = [...selectedValues.value]
  if (isChecked) {
    if (!current.includes(optionValue)) {
      current.push(optionValue)
    }
  } else {
    const idx = current.indexOf(optionValue)
    if (idx !== -1) {
      current.splice(idx, 1)
    }
  }
  emit('update:modelValue', current)
  emit('change', current)
}
</script>

<template>
  <!-- Group mode -->
  <div
    v-if="isGroup"
    data-slot="checkbox-group"
    :class="cn(
      direction === 'horizontal' ? 'flex flex-row gap-4 flex-wrap' : 'grid gap-3',
      props.class,
    )"
  >
    <label
      v-for="option in options"
      :key="option.value"
      data-slot="checkbox-wrapper"
      :class="cn(
        'flex items-center gap-2',
        (disabled || option.disabled) ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
        border && 'border rounded-md px-3 py-2 transition-colors',
        border && isOptionChecked(option.value) && 'border-primary',
      )"
    >
      <CheckboxRoot
        data-slot="checkbox"
        :checked="isOptionChecked(option.value)"
        :disabled="disabled || option.disabled"
        :class="cn(
          'peer border-input data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground data-[state=checked]:border-primary focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive size-4 shrink-0 rounded-[4px] border shadow-xs transition-shadow outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        )"
        @update:checked="(val: boolean | 'indeterminate') => onGroupItemUpdate(option.value, val)"
      >
        <CheckboxIndicator
          data-slot="checkbox-indicator"
          class="grid place-content-center text-current transition-none"
        >
          <Check class="size-3.5" />
        </CheckboxIndicator>
      </CheckboxRoot>
      <span class="text-sm leading-none select-none">{{ option.label }}</span>
    </label>
  </div>

  <!-- Single mode -->
  <label
    v-else
    data-slot="checkbox-wrapper"
    :class="cn(
      'flex items-center gap-2',
      disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
      border && 'border rounded-md px-3 py-2 transition-colors',
      border && checked === true && 'border-primary',
    )"
  >
    <CheckboxRoot
      data-slot="checkbox"
      :checked="checked"
      :disabled="disabled"
      :class="cn(
        'peer border-input data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground data-[state=checked]:border-primary data-[state=indeterminate]:bg-primary data-[state=indeterminate]:text-primary-foreground data-[state=indeterminate]:border-primary focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive size-4 shrink-0 rounded-[4px] border shadow-xs transition-shadow outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )"
      @update:checked="onUpdate"
    >
      <CheckboxIndicator
        data-slot="checkbox-indicator"
        class="grid place-content-center text-current transition-none"
      >
        <Minus v-if="indeterminate" class="size-3.5" />
        <Check v-else class="size-3.5" />
      </CheckboxIndicator>
    </CheckboxRoot>
    <slot>
      <span v-if="label" class="text-sm leading-none select-none">{{ label }}</span>
    </slot>
  </label>
</template>
