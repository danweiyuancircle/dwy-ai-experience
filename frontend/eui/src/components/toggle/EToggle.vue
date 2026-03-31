<script setup lang="ts">
import { Toggle } from 'reka-ui'
import { cn } from '@/utils/cn'
import { toggleVariants } from './types'
import type { EToggleProps, EToggleEmits } from './types'

const props = withDefaults(defineProps<EToggleProps>(), {
  variant: 'default',
  size: 'default',
  disabled: false,
})

const emit = defineEmits<EToggleEmits>()
</script>

<template>
  <Toggle
    data-slot="toggle"
    :pressed="props.modelValue"
    :disabled="props.disabled"
    :class="cn(toggleVariants({ variant: props.variant, size: props.size }), props.class)"
    @update:pressed="(val: boolean) => emit('update:modelValue', val)"
  >
    <slot />
  </Toggle>
</template>
