<script setup lang="ts">
import { cn } from '@/utils/cn'
import { fieldVariants } from './types'
import type { EFieldProps } from './types'

const props = withDefaults(defineProps<EFieldProps>(), {
  orientation: 'vertical',
})
</script>

<template>
  <div
    role="group"
    data-slot="field"
    :data-orientation="props.orientation"
    :data-invalid="props.invalid"
    :class="cn(fieldVariants({ orientation: props.orientation }), props.class)"
  >
    <slot />
  </div>
</template>
