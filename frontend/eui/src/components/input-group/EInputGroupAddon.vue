<script setup lang="ts">
import { cn } from '@/utils/cn'
import { inputGroupAddonVariants } from './types'
import type { EInputGroupAddonProps } from './types'

const props = withDefaults(defineProps<EInputGroupAddonProps>(), {
  align: 'inline-start',
})
</script>

<template>
  <div
    role="group"
    data-slot="input-group-addon"
    :data-align="props.align"
    :class="cn(inputGroupAddonVariants({ align: props.align }), props.class)"
  >
    <slot />
  </div>
</template>
