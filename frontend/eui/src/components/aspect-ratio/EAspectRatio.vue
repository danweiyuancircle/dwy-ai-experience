<script setup lang="ts">
import { AspectRatio } from 'reka-ui'
import type { EAspectRatioProps } from './types'

const props = withDefaults(defineProps<EAspectRatioProps>(), {
  ratio: 16 / 9,
})
</script>

<template>
  <AspectRatio
    data-slot="aspect-ratio"
    :ratio="props.ratio"
    :class="props.class"
  >
    <slot />
  </AspectRatio>
</template>
