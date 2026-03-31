<script setup lang="ts">
import { computed } from 'vue'
import { Check, Minus } from 'lucide-vue-next'
import { CheckboxRoot, CheckboxIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECheckboxProps, ECheckboxEmits } from './types'

const props = withDefaults(defineProps<ECheckboxProps>(), {
  disabled: false,
  indeterminate: false,
})

const emit = defineEmits<ECheckboxEmits>()

const checked = computed(() => {
  if (props.indeterminate) return 'indeterminate'
  return props.modelValue ?? false
})

function onUpdate(value: boolean | 'indeterminate') {
  const boolValue = value === 'indeterminate' ? false : value
  emit('update:modelValue', boolValue)
  emit('change', boolValue)
}
</script>

<template>
  <label
    data-slot="checkbox-wrapper"
    :class="cn(
      'flex items-center gap-2',
      disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
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
