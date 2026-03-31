<script setup lang="ts">
import { Minus, Plus } from 'lucide-vue-next'
import {
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
  NumberFieldRoot,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ENumberFieldProps, ENumberFieldEmits } from './types'

const props = withDefaults(defineProps<ENumberFieldProps>(), {
  disabled: false,
})

const emit = defineEmits<ENumberFieldEmits>()

const sizeClass = {
  sm: 'h-8 text-xs',
  md: 'h-9 text-sm',
  lg: 'h-10 text-base',
}

function onUpdate(value: number) {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<template>
  <NumberFieldRoot
    data-slot="number-field"
    :model-value="modelValue"
    :min="min"
    :max="max"
    :step="step"
    :disabled="disabled"
    :class="cn('grid gap-1.5', props.class)"
    @update:model-value="onUpdate"
  >
    <div
      class="relative [&>[data-slot=input]]:has-[[data-slot=increment]]:pr-10 [&>[data-slot=input]]:has-[[data-slot=decrement]]:pl-10"
    >
      <NumberFieldDecrement
        data-slot="decrement"
        :class="cn(
          'absolute top-1/2 -translate-y-1/2 left-0 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        )"
      >
        <Minus class="h-4 w-4" />
      </NumberFieldDecrement>

      <NumberFieldInput
        data-slot="input"
        :class="cn(
          'flex w-full rounded-md border border-input bg-transparent py-1 text-center shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
          size ? sizeClass[size] : sizeClass.md,
        )"
      />

      <NumberFieldIncrement
        data-slot="increment"
        :class="cn(
          'absolute top-1/2 -translate-y-1/2 right-0 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        )"
      >
        <Plus class="h-4 w-4" />
      </NumberFieldIncrement>
    </div>
  </NumberFieldRoot>
</template>
