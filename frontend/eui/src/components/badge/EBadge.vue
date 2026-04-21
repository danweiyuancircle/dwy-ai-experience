<!--
  EBadge 徽标组件
  基于 reka-ui Primitive 渲染，支持通过 asChild 替换为 <a> 等其他标签
-->
<script setup lang="ts">
import { reactiveOmit } from '@vueuse/core'
import { Primitive } from 'reka-ui'
import { cn } from '@/utils/cn'
import { badgeVariants } from './types'
import type { EBadgeProps } from './types'

const props = defineProps<EBadgeProps>()

// 剥离 class 后将其余 props 透传给 Primitive
const delegatedProps = reactiveOmit(props, 'class')
</script>

<template>
  <Primitive
    data-slot="badge"
    :class="cn(badgeVariants({ variant }), props.class)"
    v-bind="delegatedProps"
  >
    <slot />
  </Primitive>
</template>
