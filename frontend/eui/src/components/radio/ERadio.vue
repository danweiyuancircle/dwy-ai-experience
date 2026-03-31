<script setup lang="ts">
import { RadioGroupRoot, RadioGroupItem, RadioGroupIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ERadioProps, ERadioEmits } from './types'

const props = withDefaults(defineProps<ERadioProps>(), {
  options: () => [],
  disabled: false,
  direction: 'horizontal',
})

const emit = defineEmits<ERadioEmits>()

function onUpdate(value: string | number | bigint | Record<string, any> | null) {
  const strValue = value != null ? String(value) : ''
  emit('update:modelValue', strValue)
  emit('change', strValue)
}
</script>

<template>
  <RadioGroupRoot
    data-slot="radio-group"
    :model-value="modelValue !== undefined ? String(modelValue) : undefined"
    :disabled="disabled"
    :class="cn(
      direction === 'horizontal' ? 'flex flex-row gap-4 flex-wrap' : 'grid gap-3',
      props.class,
    )"
    @update:model-value="onUpdate"
  >
    <label
      v-for="option in options"
      :key="option.value"
      :class="cn(
        'flex items-center gap-2',
        (disabled || option.disabled) ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
      )"
    >
      <RadioGroupItem
        data-slot="radio-group-item"
        :value="String(option.value)"
        :disabled="disabled || option.disabled"
        :class="cn(
          'border-input text-primary focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 aspect-square size-4 shrink-0 rounded-full border shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        )"
      >
        <RadioGroupIndicator
          data-slot="radio-group-indicator"
          class="relative flex items-center justify-center"
        >
          <span class="fill-primary absolute top-1/2 left-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary" />
        </RadioGroupIndicator>
      </RadioGroupItem>
      <span class="text-sm leading-none select-none">{{ option.label }}</span>
    </label>
  </RadioGroupRoot>
</template>
