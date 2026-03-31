<script setup lang="ts">
import { cn } from '@/utils/cn'
import { buttonGroupVariants } from './types'
import type { EButtonGroupProps } from './types'

const props = withDefaults(defineProps<EButtonGroupProps>(), {
  orientation: 'horizontal',
})
</script>

<template>
  <div
    role="group"
    data-slot="button-group"
    :data-orientation="props.orientation"
    :class="cn(buttonGroupVariants({ orientation: props.orientation }), props.class)"
  >
    <slot />
  </div>
</template>
