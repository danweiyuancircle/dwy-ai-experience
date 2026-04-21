<!--
  ETypography 排版组件
  shadcn-vue 风格的语义化排版；variant 同时决定样式和默认渲染标签
  可通过 as 覆盖标签，便于在不改变视觉的前提下调整语义层级
-->
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
