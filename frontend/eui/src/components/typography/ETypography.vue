<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/utils/cn'
import type { ETypographyProps } from './types'
import { typographyVariantClasses, typographyVariantElements } from './types'

const props = withDefaults(defineProps<ETypographyProps>(), {
  variant: 'p',
})

const tag = computed(() => props.as ?? typographyVariantElements[props.variant ?? 'p'])
const classes = computed(() => typographyVariantClasses[props.variant ?? 'p'])
</script>

<template>
  <component
    :is="tag"
    data-slot="typography"
    :class="cn(classes, props.class)"
  >
    <slot />
  </component>
</template>
