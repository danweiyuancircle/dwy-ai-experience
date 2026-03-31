<script setup lang="ts">
import { Primitive } from 'reka-ui'
import { cn } from '@/utils/cn'
import { itemVariants } from './types'
import type { EItemProps } from './types'

const props = withDefaults(defineProps<EItemProps>(), {
  as: 'div',
})
</script>

<template>
  <Primitive
    data-slot="item"
    :as="props.as"
    :class="cn(itemVariants({ variant: props.variant, size: props.size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
